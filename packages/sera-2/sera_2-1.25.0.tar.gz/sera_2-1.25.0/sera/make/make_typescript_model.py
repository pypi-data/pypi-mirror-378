from __future__ import annotations

import re
from typing import Any, Callable

from codegen.models import AST, ImportHelper, PredefinedFn, Program, expr, stmt
from codegen.models.var import DeferredVar
from loguru import logger

from sera.make.ts_frontend.make_class_schema import make_class_schema
from sera.make.ts_frontend.misc import TS_GLOBAL_IDENTS, get_normalizer
from sera.misc import (
    assert_isinstance,
    assert_not_null,
    identity,
    to_camel_case,
    to_pascal_case,
    to_snake_case,
)
from sera.models import (
    Class,
    DataProperty,
    Enum,
    ObjectProperty,
    Package,
    Schema,
    TsTypeWithDep,
)
from sera.typing import is_set


def make_typescript_data_model(schema: Schema, target_pkg: Package):
    """Generate TypeScript data model from the schema. The data model aligns with the public data model in Python, not the database model."""
    app = target_pkg.app

    # mapping from type alias of idprop to its real type
    idprop_aliases = {}
    for cls in schema.classes.values():
        idprop = cls.get_id_property()
        if idprop is not None:
            idprop_aliases[f"{cls.name}Id"] = (
                idprop.get_data_model_datatype().get_typescript_type()
            )

    def clone_prop(prop: DataProperty | ObjectProperty, value: expr.Expr):
        # detect all complex types is hard, we can assume that any update to this does not mutate
        # the original object, then it's okay.
        return value

    def get_normal_deser_args(
        prop: DataProperty | ObjectProperty,
    ) -> expr.Expr:
        """Extract the value from the data record from the server response to set to the class property in the client."""
        handle_optional = lambda value: expr.ExprTernary(
            expr.ExprNotEqual(value, expr.ExprConstant(None)),
            value,
            expr.ExprConstant("undefined"),
        )

        if isinstance(prop, DataProperty):
            value = PredefinedFn.attr_getter(
                expr.ExprIdent("data"), expr.ExprIdent(prop.name)
            )
            if prop.is_optional:
                value = handle_optional(value)
                value.true_expr = (
                    prop.datatype.get_typescript_type().get_json_deser_func(
                        value.true_expr
                    )
                )
            else:
                value = prop.datatype.get_typescript_type().get_json_deser_func(value)

            return value

        assert isinstance(prop, ObjectProperty)
        if prop.target.db is not None:
            value = PredefinedFn.attr_getter(
                expr.ExprIdent("data"), expr.ExprIdent(prop.name + "_id")
            )
            if prop.is_optional:
                value = handle_optional(value)
            return value
        else:
            if prop.cardinality.is_star_to_many():
                # optional type for a list is simply an empty list, we don't need to check for None
                value = PredefinedFn.map_list(
                    PredefinedFn.attr_getter(
                        expr.ExprIdent("data"),
                        expr.ExprIdent(prop.name),
                    ),
                    lambda item: expr.ExprMethodCall(
                        expr.ExprIdent(
                            assert_isinstance(prop, ObjectProperty).target.name
                        ),
                        "deser",
                        [item],
                    ),
                )
                return value
            else:
                value = expr.ExprFuncCall(
                    PredefinedFn.attr_getter(
                        expr.ExprIdent(prop.target.name),
                        expr.ExprIdent("deser"),
                    ),
                    [
                        PredefinedFn.attr_getter(
                            expr.ExprIdent("data"),
                            expr.ExprIdent(prop.name),
                        )
                    ],
                )
                if prop.is_optional:
                    value = handle_optional(value)
                return value

    def make_normal(cls: Class, pkg: Package):
        """Make a data model for the normal Python data model"""
        if not cls.is_public:
            # skip classes that are not public
            return

        idprop = cls.get_id_property()
        program = Program()
        program.import_(
            f"@.models.{pkg.dir.name}.Draft{cls.name}.Draft{cls.name}", True
        )

        prop_defs = []
        prop_constructor_assigns = []
        deser_args = []

        for prop in cls.properties.values():
            if prop.data.is_private:
                # skip private fields as this is for APIs exchange
                continue

            propname = to_camel_case(prop.name)

            if isinstance(prop, DataProperty):
                tstype = prop.get_data_model_datatype().get_typescript_type()
                for dep in tstype.deps:
                    program.import_(dep, True)

                if idprop is not None and prop.name == idprop.name:
                    # use id type alias
                    tstype = TsTypeWithDep(
                        type=f"{cls.name}Id", spectype=tstype.spectype
                    )

                if prop.is_optional:
                    # convert type to optional
                    tstype = tstype.as_optional_type()

                deser_args.append(
                    (
                        expr.ExprIdent(propname),
                        get_normal_deser_args(prop),
                    )
                )
            else:
                assert isinstance(prop, ObjectProperty)
                if prop.target.db is not None:
                    # this class is stored in the database, we store the id instead
                    propname = propname + "Id"
                    tstype = TsTypeWithDep(
                        type=f"{prop.target.name}Id",
                        spectype=assert_not_null(prop.target.get_id_property())
                        .get_data_model_datatype()
                        .get_typescript_type()
                        .spectype,
                        deps=(
                            [
                                f"@.models.{prop.target.get_tsmodule_name()}.{prop.target.name}.{prop.target.name}Id"
                            ]
                            if prop.target.name != cls.name
                            else []
                        ),
                    )
                    if prop.cardinality.is_star_to_many():
                        tstype = tstype.as_list_type()
                    elif prop.is_optional:
                        # convert type to optional only if it isn't a list
                        tstype = tstype.as_optional_type()
                    deser_args.append(
                        (
                            expr.ExprIdent(propname),
                            get_normal_deser_args(prop),
                        )
                    )
                else:
                    # we are going to store the whole object
                    tstype = TsTypeWithDep(
                        type=prop.target.name,
                        spectype=prop.target.name,
                        deps=[
                            f"@.models.{prop.target.get_tsmodule_name()}.{prop.target.name}.{prop.target.name}"
                        ],
                    )
                    if prop.cardinality.is_star_to_many():
                        tstype = tstype.as_list_type()
                        deser_args.append(
                            (
                                expr.ExprIdent(propname),
                                get_normal_deser_args(prop),
                            )
                        )
                    else:
                        if prop.is_optional:
                            # convert type to optional only if it isn't a list
                            tstype = tstype.as_optional_type()
                        deser_args.append(
                            (
                                expr.ExprIdent(propname),
                                get_normal_deser_args(prop),
                            )
                        )

                for dep in tstype.deps:
                    program.import_(
                        dep,
                        True,
                    )

            prop_defs.append(stmt.DefClassVarStatement(propname, tstype.type))
            prop_constructor_assigns.append(
                stmt.AssignStatement(
                    PredefinedFn.attr_getter(
                        expr.ExprIdent("this"),
                        expr.ExprIdent(propname),
                    ),
                    expr.ExprIdent("args." + propname),
                )
            )

        program.root(
            stmt.LineBreak(),
            (
                stmt.TypescriptStatement(
                    f"export type {cls.name}Id = {idprop.get_data_model_datatype().get_typescript_type().type};"
                )
                if idprop is not None
                else None
            ),
            stmt.LineBreak(),
            lambda ast00: ast00.class_like(
                "interface",
                cls.name + "ConstructorArgs",
            )(*prop_defs),
            stmt.LineBreak(),
            lambda ast10: ast10.class_(cls.name)(
                *prop_defs,
                stmt.LineBreak(),
                lambda ast11: ast11.func(
                    "constructor",
                    [
                        DeferredVar.simple(
                            "args", expr.ExprIdent(cls.name + "ConstructorArgs")
                        ),
                    ],
                )(*prop_constructor_assigns),
                stmt.LineBreak(),
                lambda ast12: ast12.func(
                    "className",
                    [],
                    expr.ExprIdent("string"),
                    is_static=True,
                    modifiers=["get"],
                    comment="Name of the class in the Schema",
                )(
                    stmt.ReturnStatement(expr.ExprConstant(cls.name)),
                ),
                stmt.LineBreak(),
                lambda ast12: ast12.func(
                    "deser",
                    [
                        DeferredVar.simple("data", expr.ExprIdent("any")),
                    ],
                    expr.ExprIdent(cls.name),
                    is_static=True,
                    comment="Deserialize the data from the server to create a new instance of the class",
                )(
                    lambda ast: ast.return_(
                        expr.ExprNewInstance(
                            expr.ExprIdent(cls.name), [PredefinedFn.dict(deser_args)]
                        )
                    )
                ),
                stmt.LineBreak(),
                lambda ast13: ast13.func(
                    "toDraft",
                    [],
                    expr.ExprIdent(f"Draft{cls.name}"),
                    comment="Convert the class instance to a draft for editing",
                )(
                    stmt.ReturnStatement(
                        expr.ExprMethodCall(
                            expr.ExprIdent(f"Draft{cls.name}"),
                            "update",
                            [expr.ExprIdent("this")],
                        )
                    ),
                ),
            ),
        )

        pkg.module(cls.name).write(program)

    def make_draft(cls: Class, pkg: Package):
        if not cls.is_public:
            # skip classes that are not public
            return

        idprop = cls.get_id_property()

        draft_clsname = "Draft" + cls.name
        draft_validators = f"draft{cls.name}Validators"

        program = Program()
        program.import_(f"@.models.{pkg.dir.name}.{cls.name}.{cls.name}", True)
        program.import_("mobx.makeObservable", True)
        program.import_("mobx.observable", True)
        program.import_("mobx.action", True)
        program.import_("sera-db.validators", True)

        import_helper = ImportHelper(program, TS_GLOBAL_IDENTS)

        program.root(
            stmt.LineBreak(),
            stmt.TypescriptStatement(
                "const {getValidator, memoizeOneValidators} = validators;"
            ),
            stmt.LineBreak(),
        )

        # make sure that the property stale is not in existing properties
        if "stale" in cls.properties:
            raise ValueError(f"Class {cls.name} already has property stale")

        # information about class primary key
        cls_pk = None
        observable_args: list[tuple[expr.Expr, expr.ExprIdent]] = []
        prop_defs = []
        prop_validators: list[tuple[expr.ExprIdent, expr.Expr]] = []
        prop_constructor_assigns = []
        # attrs needed for the cls.create function
        create_args = []
        update_args = []
        ser_args = []
        to_record_args = []
        update_field_funcs: list[Callable[[AST], Any]] = []

        prop2tsname = {}

        for prop in cls.properties.values():
            # if prop.data.is_private:
            #     # skip private fields as this is for APIs exchange
            #     continue

            propname = to_camel_case(prop.name)
            if isinstance(prop, ObjectProperty) and prop.target.db is not None:
                propname = propname + "Id"
            prop2tsname[prop.name] = propname

            def _update_field_func(
                prop: DataProperty | ObjectProperty,
                propname: str,
                tstype: TsTypeWithDep,
                draft_clsname: str,
            ):
                return lambda ast: ast(
                    stmt.LineBreak(),
                    lambda ast01: ast01.func(
                        f"update{to_pascal_case(prop.name)}",
                        [
                            DeferredVar.simple(
                                "value",
                                expr.ExprIdent(tstype.type),
                            ),
                        ],
                        expr.ExprIdent(draft_clsname),
                        comment=f"Update the `{prop.name}` field",
                    )(
                        stmt.AssignStatement(
                            PredefinedFn.attr_getter(
                                expr.ExprIdent("this"), expr.ExprIdent(propname)
                            ),
                            expr.ExprIdent("value"),
                        ),
                        stmt.AssignStatement(
                            PredefinedFn.attr_getter(
                                expr.ExprIdent("this"), expr.ExprIdent("stale")
                            ),
                            expr.ExprConstant(True),
                        ),
                        stmt.ReturnStatement(expr.ExprIdent("this")),
                    ),
                )

            if isinstance(prop, DataProperty):
                tstype = prop.get_data_model_datatype().get_typescript_type()
                original_tstype = tstype

                if idprop is not None and prop.name == idprop.name:
                    # use id type alias
                    tstype = TsTypeWithDep(
                        type=f"{cls.name}Id",
                        spectype=tstype.spectype,
                        deps=[f"@.models.{pkg.dir.name}.{cls.name}.{cls.name}Id"],
                    )
                elif tstype.type not in schema.enums:
                    # for none id & none enum properties, we need to include a type for "invalid" value
                    tstype = _inject_type_for_invalid_value(tstype)

                if prop.is_optional:
                    # convert type to optional
                    tstype = tstype.as_optional_type()
                    original_tstype = original_tstype.as_optional_type()

                for dep in tstype.deps:
                    program.import_(dep, True)

                # however, if this is a primary key and auto-increment, we set a different default value
                # to be -1 to avoid start from 0
                if (
                    prop.db is not None
                    and prop.db.is_primary_key
                    and prop.db.is_auto_increment
                ):
                    create_propvalue = expr.ExprConstant(-1)
                elif is_set(prop.data.default_value):
                    create_propvalue = expr.ExprConstant(prop.data.default_value)
                else:
                    if tstype.type in idprop_aliases:
                        create_propvalue = idprop_aliases[tstype.type].get_default()
                    elif tstype.type in schema.enums:
                        enum_value_name = next(
                            iter(schema.enums[tstype.type].values.values())
                        ).name
                        assert isinstance(enum_value_name, str), enum_value_name
                        create_propvalue = expr.ExprIdent(
                            tstype.type + "." + enum_value_name
                        )
                    else:
                        create_propvalue = tstype.get_default()

                prop_validators.append(
                    (
                        expr.ExprIdent(propname),
                        expr.ExprFuncCall(
                            expr.ExprIdent("getValidator"),
                            [
                                PredefinedFn.list(
                                    [
                                        expr.ExprConstant(
                                            constraint.get_typescript_constraint()
                                        )
                                        for constraint in prop.data.constraints
                                    ]
                                ),
                            ],
                        ),
                    )
                )

                if prop.db is not None and prop.db.is_primary_key:
                    # for checking if the primary key is from the database or default (create_propvalue)
                    cls_pk = (expr.ExprIdent(propname), create_propvalue)

                # if this field is private, we cannot get it from the normal record
                # we have to create a default value for it.
                if prop.data.is_private:
                    update_propvalue = create_propvalue
                else:
                    update_propvalue = PredefinedFn.attr_getter(
                        expr.ExprIdent("record"), expr.ExprIdent(propname)
                    )

                if (
                    original_tstype.type != tstype.type
                    and tstype.type != f"{cls.name}Id"
                ):
                    norm_func = get_norm_func(original_tstype, import_helper)
                else:
                    norm_func = identity

                ser_args.append(
                    (
                        expr.ExprIdent(prop.name),
                        (
                            expr.ExprTernary(
                                PredefinedFn.attr_getter(
                                    expr.ExprFuncCall(
                                        PredefinedFn.attr_getter(
                                            expr.ExprIdent(draft_validators),
                                            expr.ExprIdent(propname),
                                        ),
                                        [
                                            PredefinedFn.attr_getter(
                                                expr.ExprIdent("this"),
                                                expr.ExprIdent(propname),
                                            )
                                        ],
                                    ),
                                    expr.ExprIdent("isValid"),
                                ),
                                original_tstype.get_json_ser_func(
                                    norm_func(
                                        PredefinedFn.attr_getter(
                                            expr.ExprIdent("this"),
                                            expr.ExprIdent(propname),
                                        )
                                    )
                                ),
                                expr.ExprIdent("undefined"),
                            )
                            if prop.is_optional
                            else original_tstype.get_json_ser_func(
                                norm_func(
                                    PredefinedFn.attr_getter(
                                        expr.ExprIdent("this"), expr.ExprIdent(propname)
                                    )
                                )
                            )
                        ),
                    )
                )

                if not prop.data.is_private:
                    # private property does not include in the public record
                    to_record_args.append(
                        (
                            expr.ExprIdent(propname),
                            (
                                expr.ExprTernary(
                                    PredefinedFn.attr_getter(
                                        expr.ExprFuncCall(
                                            PredefinedFn.attr_getter(
                                                expr.ExprIdent(draft_validators),
                                                expr.ExprIdent(propname),
                                            ),
                                            [
                                                PredefinedFn.attr_getter(
                                                    expr.ExprIdent("this"),
                                                    expr.ExprIdent(propname),
                                                )
                                            ],
                                        ),
                                        expr.ExprIdent("isValid"),
                                    ),
                                    norm_func(
                                        PredefinedFn.attr_getter(
                                            expr.ExprIdent("this"),
                                            expr.ExprIdent(propname),
                                        )
                                    ),
                                    expr.ExprIdent("undefined"),
                                )
                                if prop.is_optional
                                else norm_func(
                                    PredefinedFn.attr_getter(
                                        expr.ExprIdent("this"), expr.ExprIdent(propname)
                                    )
                                )
                            ),
                        )
                    )
                if not (prop.db is not None and prop.db.is_primary_key):
                    # skip observable for primary key as it is not needed
                    observable_args.append(
                        (
                            expr.ExprIdent(propname),
                            expr.ExprIdent("observable"),
                        )
                    )
                    observable_args.append(
                        (
                            expr.ExprIdent(f"update{to_pascal_case(prop.name)}"),
                            expr.ExprIdent("action"),
                        )
                    )
            else:
                assert isinstance(prop, ObjectProperty)
                if prop.target.db is not None:
                    # this class is stored in the database, we store the id instead
                    tstype = TsTypeWithDep(
                        type=f"{prop.target.name}Id",
                        spectype=assert_not_null(prop.target.get_id_property())
                        .get_data_model_datatype()
                        .get_typescript_type()
                        .spectype,
                        deps=[
                            f"@.models.{prop.target.get_tsmodule_name()}.{prop.target.name}.{prop.target.name}Id"
                        ],
                    )
                    if prop.cardinality.is_star_to_many():
                        tstype = tstype.as_list_type()
                        create_propvalue = expr.ExprConstant([])
                    else:
                        if prop.is_optional:
                            # convert type to optional - for list type, we don't need to do this
                            # as we will use empty list as no value
                            tstype = tstype.as_optional_type()
                        # if target class has an auto-increment primary key, we set a different default value
                        # to be -1 to avoid start from 0
                        target_idprop = prop.target.get_id_property()
                        if (
                            target_idprop is not None
                            and target_idprop.db is not None
                            and target_idprop.db.is_primary_key
                            and target_idprop.db.is_auto_increment
                        ):
                            create_propvalue = expr.ExprConstant(-1)
                        else:
                            assert tstype.type in idprop_aliases
                            create_propvalue = idprop_aliases[tstype.type].get_default()

                    update_propvalue = PredefinedFn.attr_getter(
                        expr.ExprIdent("record"), expr.ExprIdent(propname)
                    )
                    ser_args.append(
                        (
                            expr.ExprIdent(prop.name + "_id"),
                            PredefinedFn.attr_getter(
                                expr.ExprIdent("this"), expr.ExprIdent(propname)
                            ),
                        )
                    )

                    if not prop.data.is_private:
                        # private property does not include in the public record
                        to_record_args.append(
                            (
                                expr.ExprIdent(propname),
                                PredefinedFn.attr_getter(
                                    expr.ExprIdent("this"), expr.ExprIdent(propname)
                                ),
                            )
                        )
                else:
                    # we are going to store the whole object
                    tstype = TsTypeWithDep(
                        type=f"Draft{prop.target.name}",
                        spectype=f"Draft{prop.target.name}",
                        deps=[
                            f"@.models.{prop.target.get_tsmodule_name()}.Draft{prop.target.name}.Draft{prop.target.name}"
                        ],
                    )
                    if prop.cardinality.is_star_to_many():
                        create_propvalue = expr.ExprConstant([])
                        update_propvalue = PredefinedFn.map_list(
                            PredefinedFn.attr_getter(
                                expr.ExprIdent("record"), expr.ExprIdent(propname)
                            ),
                            lambda item: expr.ExprMethodCall(
                                expr.ExprIdent(tstype.type),
                                "update",
                                [item],
                            ),
                        )
                        ser_args.append(
                            (
                                expr.ExprIdent(prop.name),
                                PredefinedFn.map_list(
                                    PredefinedFn.attr_getter(
                                        expr.ExprIdent("this"), expr.ExprIdent(propname)
                                    ),
                                    lambda item: expr.ExprMethodCall(item, "ser", []),
                                    (
                                        (
                                            lambda item: PredefinedFn.attr_getter(
                                                expr.ExprFuncCall(
                                                    PredefinedFn.attr_getter(
                                                        expr.ExprIdent(
                                                            draft_validators
                                                        ),
                                                        expr.ExprIdent(propname),
                                                    ),
                                                    [item],
                                                ),
                                                expr.ExprIdent("isValid"),
                                            )
                                        )
                                        if prop.is_optional
                                        else None
                                    ),
                                ),
                            )
                        )

                        if not prop.data.is_private:
                            # private property does not include in the public record
                            to_record_args.append(
                                (
                                    expr.ExprIdent(propname),
                                    PredefinedFn.map_list(
                                        PredefinedFn.attr_getter(
                                            expr.ExprIdent("this"),
                                            expr.ExprIdent(propname),
                                        ),
                                        lambda item: expr.ExprMethodCall(
                                            item, "toRecord", []
                                        ),
                                        (
                                            (
                                                lambda item: PredefinedFn.attr_getter(
                                                    expr.ExprFuncCall(
                                                        PredefinedFn.attr_getter(
                                                            expr.ExprIdent(
                                                                draft_validators
                                                            ),
                                                            expr.ExprIdent(propname),
                                                        ),
                                                        [item],
                                                    ),
                                                    expr.ExprIdent("isValid"),
                                                )
                                            )
                                            if prop.is_optional
                                            else None
                                        ),
                                    ),
                                )
                            )

                        tstype = tstype.as_list_type()
                    else:
                        create_propvalue = expr.ExprMethodCall(
                            expr.ExprIdent(tstype.type),
                            "create",
                            [],
                        )
                        update_propvalue = expr.ExprMethodCall(
                            expr.ExprIdent(tstype.type),
                            "update",
                            [
                                PredefinedFn.attr_getter(
                                    expr.ExprIdent("record"), expr.ExprIdent(propname)
                                ),
                            ],
                        )

                        if prop.is_optional:
                            ser_args.append(
                                (
                                    expr.ExprIdent(prop.name),
                                    expr.ExprTernary(
                                        PredefinedFn.attr_getter(
                                            expr.ExprFuncCall(
                                                PredefinedFn.attr_getter(
                                                    expr.ExprIdent(draft_validators),
                                                    expr.ExprIdent(propname),
                                                ),
                                                [
                                                    PredefinedFn.attr_getter(
                                                        expr.ExprIdent("this"),
                                                        expr.ExprIdent(propname),
                                                    )
                                                ],
                                            ),
                                            expr.ExprIdent("isValid"),
                                        ),
                                        expr.ExprMethodCall(
                                            PredefinedFn.attr_getter(
                                                expr.ExprIdent("this"),
                                                expr.ExprIdent(propname),
                                            ),
                                            "ser",
                                            [],
                                        ),
                                        expr.ExprIdent("undefined"),
                                    ),
                                )
                            )
                            if not prop.data.is_private:
                                # private property does not include in the public record
                                to_record_args.append(
                                    (
                                        expr.ExprIdent(propname),
                                        expr.ExprTernary(
                                            PredefinedFn.attr_getter(
                                                expr.ExprFuncCall(
                                                    PredefinedFn.attr_getter(
                                                        expr.ExprIdent(
                                                            draft_validators
                                                        ),
                                                        expr.ExprIdent(propname),
                                                    ),
                                                    [
                                                        PredefinedFn.attr_getter(
                                                            expr.ExprIdent("this"),
                                                            expr.ExprIdent(propname),
                                                        )
                                                    ],
                                                ),
                                                expr.ExprIdent("isValid"),
                                            ),
                                            expr.ExprMethodCall(
                                                PredefinedFn.attr_getter(
                                                    expr.ExprIdent("this"),
                                                    expr.ExprIdent(propname),
                                                ),
                                                "toRecord",
                                                [],
                                            ),
                                            expr.ExprIdent("undefined"),
                                        ),
                                    )
                                )
                        else:
                            ser_args.append(
                                (
                                    expr.ExprIdent(prop.name),
                                    expr.ExprMethodCall(
                                        PredefinedFn.attr_getter(
                                            expr.ExprIdent("this"),
                                            expr.ExprIdent(propname),
                                        ),
                                        "ser",
                                        [],
                                    ),
                                )
                            )
                            if not prop.data.is_private:
                                # private property does not include in the public record
                                to_record_args.append(
                                    (
                                        expr.ExprIdent(propname),
                                        expr.ExprMethodCall(
                                            PredefinedFn.attr_getter(
                                                expr.ExprIdent("this"),
                                                expr.ExprIdent(propname),
                                            ),
                                            "toRecord",
                                            [],
                                        ),
                                    )
                                )

                        if prop.is_optional:
                            # convert type to optional - for list type, we don't need to do this
                            # as we will use empty list as no value
                            tstype = tstype.as_optional_type()

                for dep in tstype.deps:
                    program.import_(
                        dep,
                        True,
                    )

                observable_args.append(
                    (
                        expr.ExprIdent(propname),
                        expr.ExprIdent("observable"),
                    )
                )
                observable_args.append(
                    (
                        expr.ExprIdent(f"update{to_pascal_case(prop.name)}"),
                        expr.ExprIdent("action"),
                    )
                )

                # TODO: fix me! fix me what?? next time give more context.
                prop_validators.append(
                    (
                        expr.ExprIdent(propname),
                        expr.ExprFuncCall(
                            expr.ExprIdent("getValidator"),
                            [
                                PredefinedFn.list(
                                    [
                                        expr.ExprConstant(
                                            constraint.get_typescript_constraint()
                                        )
                                        for constraint in prop.data.constraints
                                    ]
                                ),
                            ],
                        ),
                    )
                )

            prop_defs.append(stmt.DefClassVarStatement(propname, tstype.type))
            prop_constructor_assigns.append(
                stmt.AssignStatement(
                    PredefinedFn.attr_getter(
                        expr.ExprIdent("this"),
                        expr.ExprIdent(propname),
                    ),
                    expr.ExprIdent("args." + propname),
                )
            )
            create_args.append((expr.ExprIdent(propname), create_propvalue))
            update_args.append(
                (
                    expr.ExprIdent(propname),
                    # if this is mutable property, we need to copy to make it immutable.
                    clone_prop(prop, update_propvalue),
                )
            )
            update_field_funcs.append(
                _update_field_func(prop, propname, tstype, draft_clsname)
            )

        prop_defs.append(stmt.DefClassVarStatement("stale", "boolean"))
        prop_constructor_assigns.append(
            stmt.AssignStatement(
                PredefinedFn.attr_getter(
                    expr.ExprIdent("this"), expr.ExprIdent("stale")
                ),
                expr.ExprIdent("args.stale"),
            )
        )
        observable_args.append(
            (
                expr.ExprIdent("stale"),
                expr.ExprIdent("observable"),
            )
        )
        create_args.append(
            (
                expr.ExprIdent("stale"),
                expr.ExprConstant(True),
            ),
        )
        update_args.append(
            (
                expr.ExprIdent("stale"),
                expr.ExprConstant(False),
            ),
        )
        observable_args.sort(key=lambda x: {"observable": 0, "action": 1}[x[1].ident])

        validators = expr.ExprFuncCall(
            expr.ExprIdent("memoizeOneValidators"), [PredefinedFn.dict(prop_validators)]
        )

        program.root(
            lambda ast00: ast00.class_like(
                "interface",
                draft_clsname + "ConstructorArgs",
            )(*prop_defs),
            stmt.LineBreak(),
            lambda ast10: ast10.class_(draft_clsname)(
                *prop_defs,
                stmt.LineBreak(),
                lambda ast10: ast10.func(
                    "constructor",
                    [
                        DeferredVar.simple(
                            "args",
                            expr.ExprIdent(draft_clsname + "ConstructorArgs"),
                        ),
                    ],
                )(
                    *prop_constructor_assigns,
                    stmt.LineBreak(),
                    stmt.SingleExprStatement(
                        expr.ExprFuncCall(
                            expr.ExprIdent("makeObservable"),
                            [
                                expr.ExprIdent("this"),
                                PredefinedFn.dict(observable_args),
                            ],
                        )
                    ),
                ),
                stmt.LineBreak(),
                lambda ast11: (
                    ast11.func(
                        "isNewRecord",
                        [],
                        expr.ExprIdent("boolean"),
                        comment="Check if this draft is for creating a new record",
                    )(
                        stmt.ReturnStatement(
                            expr.ExprEqual(
                                PredefinedFn.attr_getter(
                                    expr.ExprIdent("this"), cls_pk[0]
                                ),
                                cls_pk[1],
                            )
                        )
                    )
                    if cls_pk is not None
                    else None
                ),
                stmt.LineBreak(),
                lambda ast12: ast12.func(
                    "create",
                    [],
                    expr.ExprIdent(draft_clsname),
                    is_static=True,
                    comment="Make a new draft for creating a new record",
                )(
                    stmt.ReturnStatement(
                        expr.ExprNewInstance(
                            expr.ExprIdent(draft_clsname),
                            [PredefinedFn.dict(create_args)],
                        )
                    ),
                ),
                stmt.LineBreak(),
                lambda ast13: ast13.func(
                    "update",
                    [DeferredVar.simple("record", expr.ExprIdent(cls.name))],
                    expr.ExprIdent(draft_clsname),
                    is_static=True,
                    comment="Make a new draft for updating an existing record",
                )(
                    stmt.ReturnStatement(
                        expr.ExprNewInstance(
                            expr.ExprIdent(draft_clsname),
                            [PredefinedFn.dict(update_args)],
                        )
                    ),
                ),
                *update_field_funcs,
                stmt.LineBreak(),
                lambda ast14: ast14.func(
                    "isValid",
                    [],
                    expr.ExprIdent("boolean"),
                    comment="Check if the draft is valid (only check the required fields as the non-required fields if it's invalid will be set to undefined)",
                )(
                    stmt.ReturnStatement(
                        expr.ExprRawTypescript(
                            " && ".join(
                                f"{draft_validators}.{prop2tsname[prop.name]}(this.{prop2tsname[prop.name]}).isValid"
                                for prop in cls.properties.values()
                                if not prop.is_optional
                            )
                            if any(
                                not prop.is_optional for prop in cls.properties.values()
                            )
                            else "true"
                        )
                    )
                ),
                stmt.LineBreak(),
                lambda ast15: ast15.func(
                    "ser",
                    [],
                    expr.ExprIdent("any"),
                    comment="Serialize the draft to communicate with the server. `isValid` must be called first to ensure all data is valid",
                )(
                    stmt.ReturnStatement(
                        PredefinedFn.dict(ser_args),
                    ),
                ),
                stmt.LineBreak(),
                lambda ast16: ast16.func(
                    "toRecord",
                    [],
                    expr.ExprIdent(cls.name),
                    comment="Convert the draft to a normal record. `isValid` must be called first to ensure all data is valid",
                )(
                    stmt.ReturnStatement(
                        expr.ExprNewInstance(
                            expr.ExprIdent(cls.name),
                            [PredefinedFn.dict(to_record_args)],
                        ),
                    )
                ),
            ),
            stmt.LineBreak(),
            stmt.TypescriptStatement(
                f"export const {draft_validators} = " + validators.to_typescript() + ";"
            ),
        )

        pkg.module("Draft" + cls.name).write(program)

    def make_table(cls: Class, pkg: Package):
        if not cls.is_public or cls.db is None:
            # skip classes that are not public and not stored in the database
            return

        outmod = pkg.module(cls.name + "Table")
        if outmod.exists():
            # skip if the module already exists
            logger.info(f"Module {outmod.path} already exists, skip")
            return

        program = Program()
        program.import_(f"@.models.{pkg.dir.name}.{cls.name}.{cls.name}", True)
        program.import_(f"@.models.{pkg.dir.name}.{cls.name}.{cls.name}Id", True)
        program.import_(f"@.models.{pkg.dir.name}.{cls.name}Query.query", True)
        program.import_(
            f"@.models.{pkg.dir.name}.Draft{cls.name}.Draft{cls.name}", True
        )
        program.import_("sera-db.Table", True)
        program.import_("sera-db.DB", True)

        program.root(
            stmt.LineBreak(),
            lambda ast00: ast00.class_(
                f"{cls.name}Table",
                [expr.ExprIdent(f"Table<{cls.name}Id, {cls.name}, Draft{cls.name}>")],
            )(
                lambda ast01: ast01.func(
                    "constructor",
                    [
                        DeferredVar.simple(
                            "db",
                            expr.ExprIdent("DB"),
                        )
                    ],
                )(
                    stmt.SingleExprStatement(
                        expr.ExprFuncCall(
                            expr.ExprIdent("super"),
                            [
                                PredefinedFn.dict(
                                    [
                                        (
                                            expr.ExprIdent("cls"),
                                            expr.ExprIdent(cls.name),
                                        ),
                                        (
                                            expr.ExprIdent("remoteURL"),
                                            expr.ExprConstant(
                                                f"/api/{to_snake_case(cls.name).replace('_', '-')}"
                                            ),
                                        ),
                                        (
                                            expr.ExprIdent("db"),
                                            expr.ExprIdent("db"),
                                        ),
                                        (
                                            expr.ExprIdent("queryProcessor"),
                                            expr.ExprIdent("query"),
                                        ),
                                    ]
                                )
                            ],
                        )
                    )
                ),
            ),
        )

        outmod.write(program)

    def make_query_processor(cls: Class, pkg: Package):
        if not cls.is_public:
            # skip classes that are not public
            return

        outmod = pkg.module(cls.name + "Query")

        program = Program()
        program.import_(f"@.models.{pkg.dir.name}.{cls.name}.{cls.name}", True)
        program.import_(f"sera-db.QueryProcessor", True)

        query_args = []
        for prop in cls.properties.values():
            pypropname = prop.name
            tspropname = to_camel_case(prop.name)

            if isinstance(prop, ObjectProperty) and prop.target.db is not None:
                tspropname = tspropname + "Id"
                pypropname = prop.name + "_id"

            if tspropname != pypropname:
                query_args.append(
                    (
                        expr.ExprIdent(tspropname),
                        expr.ExprConstant(pypropname),
                    )
                )

        program.root(
            stmt.LineBreak(),
            stmt.TypescriptStatement(
                f"export const query = "
                + expr.ExprNewInstance(
                    expr.ExprIdent(f"QueryProcessor<{cls.name}>"),
                    [
                        PredefinedFn.dict(query_args),
                    ],
                ).to_typescript()
                + ";",
            ),
        )

        outmod.write(program)

    def make_index(pkg: Package):
        outmod = pkg.module("index")
        if outmod.exists():
            # skip if the module already exists
            logger.info(f"Module {outmod.path} already exists, skip")
            return

        export_types = []
        export_iso_types = []  # isolatedModules required separate export type clause

        program = Program()
        program.import_(f"@.models.{pkg.dir.name}.{cls.name}.{cls.name}", True)
        export_types.append(cls.name)
        if cls.db is not None:
            # only import the id if this class is stored in the database
            program.import_(f"@.models.{pkg.dir.name}.{cls.name}.{cls.name}Id", True)
            export_iso_types.append(f"{cls.name}Id")

        program.import_(
            f"@.models.{pkg.dir.name}.{cls.name}Schema.{cls.name}Schema", True
        )
        export_types.append(f"{cls.name}Schema")
        program.import_(
            f"@.models.{pkg.dir.name}.{cls.name}Schema.{cls.name}SchemaType", True
        )
        export_iso_types.append(f"{cls.name}SchemaType")

        program.import_(
            f"@.models.{pkg.dir.name}.Draft{cls.name}.Draft{cls.name}", True
        )
        export_types.append(f"Draft{cls.name}")
        if cls.db is not None:
            program.import_(
                f"@.models.{pkg.dir.name}.{cls.name}Table.{cls.name}Table", True
            )
            export_types.append(f"{cls.name}Table")

        program.root(
            stmt.LineBreak(),
            stmt.TypescriptStatement("export { %s };" % (", ".join(export_types))),
            (
                stmt.TypescriptStatement(
                    "export type { %s };" % (", ".join(export_iso_types))
                )
            ),
        )

        outmod.write(program)

    for cls in schema.topological_sort():
        pkg = target_pkg.pkg(cls.get_tsmodule_name())
        make_normal(cls, pkg)
        make_draft(cls, pkg)
        make_query_processor(cls, pkg)
        make_table(cls, pkg)
        make_class_schema(schema, cls, pkg)

        make_index(pkg)


def make_typescript_enum(schema: Schema, target_pkg: Package):
    """Make typescript enum for the schema"""
    enum_pkg = target_pkg.pkg("enums")

    def make_enum(enum: Enum, pkg: Package):
        program = Program()
        program.root(
            stmt.LineBreak(),
            lambda ast: ast.class_like("enum", enum.name)(
                *[
                    stmt.DefEnumValueStatement(
                        name=value.name,
                        value=expr.ExprConstant(value.value),
                    )
                    for value in enum.values.values()
                ]
            ),
        )
        pkg.module(enum.get_tsmodule_name()).write(program)

    for enum in schema.enums.values():
        make_enum(enum, enum_pkg)

    program = Program()
    for enum in schema.enums.values():
        program.import_(f"@.models.enums.{enum.get_tsmodule_name()}.{enum.name}", True)

    program.root(
        stmt.LineBreak(),
        stmt.TypescriptStatement(
            "export { "
            + ", ".join([enum.name for enum in schema.enums.values()])
            + "};"
        ),
    )
    enum_pkg.module("index").write(program)


def _inject_type_for_invalid_value(tstype: TsTypeWithDep) -> TsTypeWithDep:
    """
    Inject a type for "invalid" values into the given TypeScript type. For context, see the discussion in Data Modeling Problems:
    What would be an appropriate type for an invalid value? Since it's user input, it will be a string type.

    However, there are some exceptions such as boolean type, which will always be valid and do not need injection.

    If the type already includes `string` type, no changes are needed. Otherwise, we add `string` to the type. For example:
    - (number | undefined) -> (number | undefined | string)
    - number | undefined -> number | undefined | string
    - number[] -> (number | string)[]
    - (number | undefined)[] -> (number | undefined | string)[]
    """
    if tstype.type == "boolean":
        return tstype

    # TODO: fix me and make it more robust!
    m = re.match(r"(\(?[a-zA-Z \|]+\)?)(\[\])", tstype.type)
    if m is not None:
        # This is an array type, add string to the inner type
        inner_type = m.group(1)
        inner_spectype = assert_not_null(
            re.match(r"(\(?[a-zA-Z \|]+\)?)(\[\])", tstype.spectype)
        ).group(1)
        if "string" not in inner_type:
            if inner_type.startswith("(") and inner_type.endswith(")"):
                # Already has parentheses
                inner_type = f"{inner_type[:-1]} | string)"
                inner_spectype = f"{inner_spectype[:-1]} | string)"
            else:
                # Need to add parentheses
                inner_type = f"({inner_type} | string)"
                inner_spectype = f"({inner_spectype} | string)"
        return TsTypeWithDep(inner_type + "[]", inner_spectype + "[]", tstype.deps)

    m = re.match(r"^\(?[a-zA-Z \|]+\)?$", tstype.type)
    if m is not None:
        if "string" not in tstype.type:
            if tstype.type.startswith("(") and tstype.type.endswith(")"):
                # Already has parentheses
                new_type = f"{tstype.type[:-1]} | string)"
                new_spectype = f"{tstype.spectype[:-1]} | string)"
            else:
                # Needs parentheses for clarity
                new_type = f"({tstype.type} | string)"
                new_spectype = f"({tstype.spectype} | string)"
            return TsTypeWithDep(new_type, new_spectype, tstype.deps)
        return tstype

    raise NotImplementedError(tstype.type)


def get_norm_func(
    tstype: TsTypeWithDep, import_helper: ImportHelper
) -> Callable[[expr.Expr], expr.Expr]:
    """
    Get the normalizer function for the given TypeScript type.
    If no normalizer is available, return None.
    """
    norm_func = get_normalizer(tstype, import_helper)
    if norm_func is not None:

        def modify_expr(value: expr.Expr) -> expr.Expr:
            return expr.ExprFuncCall(
                norm_func,
                [value],
            )

        return modify_expr
    return identity  # Return the value as is if no normalizer is available
