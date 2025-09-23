from dataclasses import MISSING, field, is_dataclass
from datetime import date, datetime
from enum import Enum
from functools import wraps
from itertools import pairwise
from pathlib import Path
from types import NoneType, UnionType
from typing import Annotated, Any, get_args, get_origin

from ovld import (
    Code,
    CodegenInProgress,
    CodegenParameter,
    Def,
    Lambda,
    Medley,
    call_next,
    code_generator,
    keyword_decorator,
    ovld,
    recurse,
)
from ovld.codegen import Function
from ovld.medley import KeepLast, use_combiner
from ovld.types import All, Exactly
from ovld.utils import ResolutionError, subtler_type

from . import formats
from .auto import Auto
from .ctx import AccessPath, Context, Sourced, WorkingDirectory
from .exc import SchemaError, SerieuxError, ValidationError, ValidationExceptionGroup
from .instructions import pushdown
from .model import FieldModelizable, ListModelizable, Modelizable, StringModelizable, model
from .priority import LO4, LOW, MAX, MIN, STD, STD2, STD3
from .schema import AnnotatedSchema, Schema
from .tell import tells as get_tells
from .utils import (
    JSON,
    Indirect,
    IsLiteral,
    TypeAliasType,
    UnionAlias,
    basic_type,
    clsstring,
)


@keyword_decorator
def code_generator_wrap_error(fn, priority=0):
    @wraps(fn)
    def f(cls, *args, **kwargs):
        result = fn(cls, *args, **kwargs)
        if not result:
            return None
        body = result.create_body(("t", "obj", "ctx"))
        stmts = [
            "try:",
            [body],
            "except $SXE:",
            ["raise"],
            "except Exception as exc:",
            ["raise $VE(exc=exc, ctx=$ctx)"],
        ]
        return Def(stmts, SXE=SerieuxError, VE=ValidationError)

    return code_generator(f, priority=priority)


class BaseImplementation(Medley):
    default_context: Context = field(default_factory=AccessPath)
    validate_serialize: CodegenParameter[bool] = True
    validate_deserialize: CodegenParameter[bool] = True

    def __post_init__(self):
        self._schema_cache = {}

    #######################
    # User-facing methods #
    #######################

    @use_combiner(KeepLast)
    def load(self, t, obj, ctx=None):
        ctx = ctx or self.default_context
        return self.deserialize(t, obj, ctx)

    @use_combiner(KeepLast)
    def dump(self, t, obj, ctx=None, *, dest=None, format=None):
        ctx = ctx or self.default_context
        if dest:
            dest = Path(dest)
            ctx = ctx + Sourced(origin=dest)
        serialized = self.serialize(t, obj, ctx)
        if dest:
            formats.dump(p=dest, data=serialized, suffix=format)
        elif format:
            return formats.dumps(data=serialized, suffix=format)
        else:
            return serialized

    ##################
    # Global helpers #
    ##################

    @classmethod
    def subcode(
        cls, method_name, t, accessor, ctx_t, ctx_expr=Code("$ctx"), after=None, validate=None
    ):
        accessor = accessor if isinstance(accessor, Code) else Code(accessor)
        if validate is None:
            validate = getattr(cls, f"validate_{method_name}")
        method = getattr(cls, method_name)
        if ec := getattr(cls, f"{method_name}_embed_condition")(t):
            ec = All[ec]
        if ec is not None:
            try:
                fn = method.resolve(type[t], ec, ctx_t, after=after)
                cg = getattr(fn, "__codegen__", None)
                if cg:
                    body = cg.create_expression([None, t, accessor, ctx_expr])
                    ot = get_origin(t) or t
                    if not validate:
                        return Code(body)
                    else:
                        return Code(
                            "$body if type(__checked := $accessor) is $t else $recurse($self, $t, __checked, $ctx_expr)",
                            body=Code(body),
                            accessor=accessor,
                            t=ot,
                            recurse=method,
                            ctx_expr=ctx_expr,
                        )
            except (CodegenInProgress, ValueError):  # pragma: no cover
                # This is important if we are going to inline recursively
                # a type that refers to itself down the line.
                # We currently never do that.
                pass
        return Code(
            "$method_map[$tt, type(OBJ := $accessor), $ctxt]($self, $t, OBJ, $ctx_expr)",
            tt=subtler_type(t),
            ctxt=ctx_t,
            t=t,
            accessor=accessor,
            method_map=method.map,
            ctx_expr=ctx_expr,
        )

    ########################################
    # serialize:  helpers and entry points #
    ########################################

    @classmethod
    def serialize_embed_condition(cls, t):
        if t in (int, str, bool, float, NoneType):
            return t

    @ovld(priority=MIN)
    def serialize(self, t: Any, obj: Any, ctx: Context, /):
        raise ValidationError(
            f"Cannot serialize object of type '{clsstring(type(obj))}'"
            + (f" into expected type '{clsstring(t)}'." if t is not type(obj) else ""),
            ctx=ctx,
        )

    @ovld(priority=MIN)
    def serialize(self, t: Indirect | TypeAliasType, obj: Any, ctx: Context, /):
        return recurse(t.__value__, obj, ctx)

    @ovld(priority=LOW)
    def serialize(self, t: type[Annotated], obj: Any, ctx: Context, /):
        return recurse(pushdown(t), obj, ctx)

    def serialize(self, obj: Any, /):
        return recurse(type(obj), obj, self.default_context)

    def serialize(self, t: Any, obj: Any, /):
        return recurse(t, obj, self.default_context)

    #########################################
    # deserialize: helpers and entry points #
    #########################################

    deserialize_embed_condition = serialize_embed_condition

    @ovld(priority=MIN)
    def deserialize(self, t: Any, obj: Any, ctx: Context, /):
        try:
            # Pass through if the object happens to already be the right type
            if t is Any or isinstance(obj, t):
                return obj
        except TypeError:  # pragma: no cover
            pass
        disp = str(obj)
        if len(disp) > (n := 30):  # pragma: no cover
            disp = disp[:n] + "..."
        if isinstance(obj, str):
            descr = f"string '{disp}'"
        else:
            descr = f"object `{disp}` of type '{clsstring(type(obj))}'"
        raise ValidationError(
            f"Cannot deserialize {descr} into expected type '{clsstring(t)}'.",
            ctx=ctx,
        )

    @ovld(priority=MIN)
    def deserialize(self, t: Indirect | TypeAliasType, obj: Any, ctx: Context, /):
        return recurse(t.__value__, obj, ctx)

    @ovld(priority=LOW)
    def deserialize(self, t: type[Annotated], obj: Any, ctx: Context, /):
        return recurse(pushdown(t), obj, ctx)

    def deserialize(self, t: Any, obj: Any, /):
        return recurse(t, obj, self.default_context)

    ####################################
    # schema: helpers and entry points #
    ####################################

    @ovld(priority=MAX)
    def schema(self, t: Any, ctx: Context, /):
        if t not in self._schema_cache:
            self._schema_cache[t] = holder = Schema(t)
            try:
                result = call_next(t, ctx)
            except Exception:
                del self._schema_cache[t]
                raise
            holder.update(result)
        return self._schema_cache[t]

    @ovld(priority=MIN)
    def schema(self, t: Indirect | TypeAliasType, ctx: Context, /):  # pragma: no cover
        return recurse(t.__value__, ctx)

    @ovld(priority=LOW)  # pragma: no cover
    def schema(self, t: type[Annotated], ctx: Context, /):
        return recurse(pushdown(t), ctx)

    def schema(self, t: Any, /):
        return recurse(t, self.default_context)

    ################################
    # Implementations: basic types #
    ################################

    # str

    @code_generator(priority=STD)
    def serialize(cls, t: type[str], obj: str, ctx: Context, /):
        return Lambda(Code("$obj"))

    @code_generator(priority=STD)
    def deserialize(cls, t: type[str], obj: str, ctx: Context, /):
        return Lambda(Code("$obj"))

    @ovld(priority=STD)
    def schema(self, t: type[str], ctx: Context, /):
        return {"type": "string"}

    # bool

    @code_generator(priority=STD)
    def serialize(cls, t: type[bool], obj: bool, ctx: Context, /):
        return Lambda(Code("$obj"))

    @code_generator(priority=STD)
    def deserialize(cls, t: type[bool], obj: bool, ctx: Context, /):
        return Lambda(Code("$obj"))

    @ovld(priority=STD)
    def schema(self, t: type[bool], ctx: Context, /):
        return {"type": "boolean"}

    # int

    @code_generator(priority=STD)
    def serialize(cls, t: type[int], obj: int, ctx: Context, /):
        return Lambda(Code("$obj"))

    @code_generator(priority=STD)
    def deserialize(cls, t: type[int], obj: int, ctx: Context, /):
        return Lambda(Code("$obj"))

    @ovld(priority=STD)
    def schema(self, t: type[int], ctx: Context, /):
        return {"type": "integer"}

    # float

    @code_generator(priority=STD)
    def serialize(cls, t: type[float], obj: float, ctx: Context, /):
        return Lambda(Code("$obj"))

    @code_generator(priority=STD)
    def deserialize(cls, t: type[float], obj: float, ctx: Context, /):
        return Lambda(Code("$obj"))

    # float

    @code_generator(priority=STD)
    def serialize(cls, t: type[float], obj: int, ctx: Context, /):
        return Lambda(Code("$obj"))

    @code_generator(priority=STD)
    def deserialize(cls, t: type[float], obj: int, ctx: Context, /):
        return Lambda(Code("float($obj)"))

    @ovld(priority=STD)
    def schema(self, t: type[float], ctx: Context, /):
        return {"type": "number"}

    # None

    @code_generator(priority=STD)
    def serialize(cls, t: type[NoneType], obj: NoneType, ctx: Context, /):
        return Lambda(Code("$obj"))

    @code_generator(priority=STD)
    def deserialize(cls, t: type[NoneType], obj: NoneType, ctx: Context, /):
        return Lambda(Code("$obj"))

    @ovld(priority=STD)
    def schema(self, t: type[NoneType], ctx: Context, /):
        return {"type": "null"}

    ##########################
    # Implementations: dicts #
    ##########################

    @classmethod
    def __generic_codegen_dict(cls, method, t: type[dict], obj: dict, ctx: Context, /):
        (t,) = get_args(t)
        builder = dict if method == "serialize" else get_origin(t) or t
        kt, vt = get_args(t) or (object, object)
        ctx_expr = (
            Code("$ctx.follow($objt, $obj, K)", objt=t) if hasattr(ctx, "follow") else Code("$ctx")
        )
        code = "{$kbody: $vbody for K, V in $obj.items()}"
        if builder is not dict:
            code = f"$builder({code})"
        return Lambda(
            code,
            kbody=cls.subcode(method, kt, "K", ctx, ctx_expr=ctx_expr),
            vbody=cls.subcode(method, vt, "V", ctx, ctx_expr=ctx_expr),
            builder=builder,
        )

    @code_generator(priority=STD)
    def serialize(cls, t: type[dict], obj: dict, ctx: Context, /):
        return cls.__generic_codegen_dict("serialize", t, obj, ctx)

    @code_generator(priority=STD)
    def deserialize(cls, t: type[dict], obj: dict, ctx: Context, /):
        return cls.__generic_codegen_dict("deserialize", t, obj, ctx)

    def schema(self, t: type[dict], ctx: Context, /):
        kt, vt = get_args(t)
        if kt is not str:
            raise SchemaError(
                f"Cannot create a schema for dicts with non-string keys (found key type: `{kt}`)"
            )
        follow = hasattr(ctx, "follow")
        fctx = ctx.follow(t, None, "*") if follow else ctx
        return {"type": "object", "additionalProperties": recurse(vt, fctx)}

    #####################################
    # Implementations: FieldModelizable #
    #####################################

    @code_generator_wrap_error(priority=STD)
    def serialize(cls, t: type[FieldModelizable], obj: Any, ctx: Context, /):
        (orig_t,) = get_args(t)
        t = model(orig_t)
        if not t.accepts(obj):
            return None
        stmts = []
        follow = hasattr(ctx, "follow")
        for i, f in enumerate(t.fields):
            if f.property_name is None:
                raise SchemaError(
                    f"Cannot serialize '{clsstring(t)}' because its model does not specify how to serialize property '{f.name}'"
                )
            ctx_expr = (
                Code("$ctx.follow($objt, $obj, $fld)", objt=orig_t, fld=f.name)
                if follow
                else Code("$ctx")
            )
            stmt = Code(
                f"v_{i} = $setter",
                setter=cls.subcode(
                    "serialize", f.type, f"$obj.{f.property_name}", ctx, ctx_expr=ctx_expr
                ),
            )
            stmts.append(stmt)
        final = Code(
            "return {$[,]parts}",
            parts=[
                Code(
                    f"$fname: v_{i}",
                    fname=f.serialized_name,
                )
                for i, f in enumerate(t.fields)
            ],
        )
        stmts.append(final)
        return Def(stmts, VE=ValidationError, VEG=ValidationExceptionGroup)

    @code_generator_wrap_error(priority=STD)
    def deserialize(cls, t: type[FieldModelizable], obj: dict, ctx: Context, /):
        (orig_t,) = get_args(t)
        t = model(orig_t)
        follow = hasattr(ctx, "follow")
        stmts = []
        args = []
        for i, f in enumerate(t.fields):
            ctx_expr = (
                Code("$ctx.follow($objt, $obj, $fld)", objt=orig_t, fld=f.name)
                if follow
                else Code("$ctx")
            )
            if f.metavar:
                expr = Code(f.metavar)
            else:
                expr = cls.subcode(
                    "deserialize",
                    f.type,
                    Code("$obj[$pname]", pname=f.serialized_name),
                    ctx,
                    ctx_expr=ctx_expr,
                )

            stmt = Code([f"v_{i} = $expr"], expr=expr)

            if f.required or f.metavar:
                pass
            elif f.default is not MISSING:
                stmt = Code(
                    [
                        "if $pname in $obj:",
                        ["$stmt"],
                        "else:",
                        [f"v_{i} = $dflt"],
                    ],
                    dflt=f.default,
                    pname=f.serialized_name,
                    stmt=stmt,
                )
            elif f.default_factory is not MISSING:
                stmt = Code(
                    [
                        "if $pname in $obj:",
                        ["$stmt"],
                        "else:",
                        [f"v_{i} = $dflt()"],
                    ],
                    dflt=f.default_factory,
                    pname=f.serialized_name,
                    stmt=stmt,
                )
            stmts.append(stmt)
            if isinstance(f.argument_name, str):
                arg = f"{f.argument_name}=v_{i}"
            else:
                arg = f"v_{i}"
            args.append(arg)

        final = Code(
            "return $constructor($[,]parts)",
            constructor=t.constructor,
            parts=[Code(a) for a in args],
        )
        stmts.append(final)
        return Def(stmts, VE=ValidationError, VEG=ValidationExceptionGroup)

    ######################################
    # Implementations: StringModelizable #
    ######################################

    @code_generator_wrap_error(priority=STD2)
    def serialize(self, t: type[StringModelizable], obj: Any, ctx: Context, /):
        (t,) = get_args(t)
        m = model(t)
        if not m.accepts(obj) or m.to_string is None:
            return None
        if isinstance(m.to_string, Function):
            return m.to_string
        else:
            return Lambda("$to_string($obj)", to_string=m.to_string)

    @code_generator_wrap_error(priority=STD2)
    def deserialize(self, t: type[StringModelizable], obj: str, ctx: Context, /):
        (t,) = get_args(t)
        m = model(t)
        if m.regexp:
            if isinstance(m.from_string, Def):  # pragma: no cover
                raise Exception("In model definitions, use Lambda with regexp, not Def")
            elif isinstance(m.from_string, Lambda):
                expr = m.from_string.create_expression(["t", "obj", "ctx"])
            else:
                expr = Code("$from_string($obj)", from_string=m.from_string)
            descr = m.string_description or f"pattern {m.regexp.pattern!r}"
            pattern = f"String {{$obj!r}} is not a valid {clsstring(t)}. It should match: {descr}"
            return Def(
                ["t", "obj", "ctx"],
                Code(
                    [
                        ["if $regexp.match($obj):", ["return $expr"]],
                        [
                            "else:",
                            [f"""raise $VE(f"{pattern}")"""],
                        ],
                    ]
                ),
                from_string=m.from_string,
                regexp=m.regexp,
                expr=expr,
                descr=descr,
                VE=ValidationError,
            )
        elif isinstance(m.from_string, Function):
            return m.from_string
        else:
            return Lambda("$from_string($obj)", from_string=m.from_string)

    ####################################
    # Implementations: ListModelizable #
    ####################################

    @classmethod
    def __generic_codegen_list(cls, method, m, obj, ctx):
        builder = list if method == "serialize" else m.list_constructor
        lt = m.element_field.type
        comp = "$lbody for IDX, X in enumerate($obj)"
        if builder is list:
            code = f"[{comp}]"
        elif builder is set:
            code = f"{{{comp}}}"
        else:
            code = f"$builder({comp})"
        if hasattr(ctx, "follow"):
            ctx_expr = Code("$ctx.follow($objt, $obj, IDX)", objt=m.original_type)
        else:
            ctx_expr = Code("$ctx")
        return Lambda(
            code,
            lbody=cls.subcode(method, lt, "X", ctx, ctx_expr=ctx_expr),
            builder=builder,
        )

    @code_generator(priority=STD)
    def serialize(cls, t: type[ListModelizable], obj: Any, ctx: Context, /):
        (t,) = get_args(t)
        m = model(t)
        return cls.__generic_codegen_list("serialize", m, obj, ctx)

    @code_generator(priority=STD)
    def deserialize(cls, t: type[ListModelizable], obj: list, ctx: Context, /):
        (t,) = get_args(t)
        m = model(t)
        return cls.__generic_codegen_list("deserialize", m, obj, ctx)

    ################################
    # Implementations: Modelizable #
    ################################

    @ovld(priority=STD)
    def schema(self, t: type[Modelizable], ctx: Context, /):
        m = model(t)

        f_schema = s_schema = l_schema = None
        follow = hasattr(ctx, "follow")

        if m.fields is not None:
            properties = {}
            required = []

            for f in m.fields:
                fctx = ctx.follow(t, None, f.name) if follow else ctx
                fsch = recurse(f.type, fctx)
                extra = {}
                if f.description:
                    extra["description"] = f.description
                if f.default is not MISSING:
                    extra["default"] = f.default
                fsch = fsch if not f.description else AnnotatedSchema(fsch, **extra)
                properties[f.serialized_name] = fsch
                if f.required:
                    required.append(f.serialized_name)

            f_schema = {
                "type": "object",
                "properties": properties,
                "required": required,
                "additionalProperties": m.extensible,
            }

        if m.from_string is not None:
            s_schema = {"type": "string"}
            if m.regexp:
                s_schema["pattern"] = m.regexp.pattern

        if m.element_field is not None:
            fctx = ctx.follow(t, None, "*") if follow else ctx
            l_schema = {
                "type": "array",
                "items": recurse(m.element_field.type, fctx),
            }

        assert f_schema or s_schema or l_schema
        possibilities = [x for x in [f_schema, s_schema, l_schema] if x]
        match possibilities:
            case [sch]:
                return sch
            case _:
                return {"oneOf": possibilities}

    ###########################
    # Implementations: Unions #
    ###########################

    @code_generator(priority=STD)
    def serialize(cls, t: type[UnionAlias], obj: Any, ctx: Context, /):
        (t,) = get_args(t)
        o1, *rest = get_args(t)
        code = cls.subcode("serialize", o1, "$obj", ctx, validate=False)
        for opt in rest:
            code = Code(
                "$ocode if isinstance($obj, $sopt) else $code",
                sopt=basic_type(opt),
                ocode=cls.subcode("serialize", opt, "$obj", ctx, validate=False),
                code=code,
            )
        return Lambda(code)

    @code_generator(priority=STD)
    def deserialize(cls, t: type[UnionAlias] | type[UnionType], obj: Any, ctx: Context, /):
        (t,) = get_args(t)
        options = get_args(t)

        try:
            tells = [get_tells(opt := o) for o in options]
        except ResolutionError as exc:
            raise SchemaError(
                f"Cannot deserialize union type `{t}`, because no rule is defined to discriminate `{opt}` from other types.",
                exc=exc,
            )
        elim = set()
        for tl1, tl2 in pairwise(tells):
            elim |= tl1 & tl2
        for tls in tells:
            tls -= elim

        if sum(not tl for tl in tells) > 1:
            raise SchemaError(f"Cannot differentiate the possible union members in type '{t}'")

        options = list(zip(tells, options))
        options.sort(key=lambda x: len(x[0]))

        (_, o1), *rest = options

        code = cls.subcode("deserialize", o1, "$obj", ctx)
        for tls, opt in rest:
            code = Code(
                "($ocode if $cond else $code)",
                cond=min(tls).gen(Code("$obj")),
                code=code,
                ocode=cls.subcode("deserialize", opt, "$obj", ctx),
            )
        return Lambda(code)

    @ovld(priority=STD)
    def schema(self, t: type[UnionAlias], ctx: Context, /):
        options = get_args(t)
        return {"oneOf": [recurse(opt, ctx) for opt in options]}

    #########################
    # Implementations: JSON #
    #########################

    @ovld(priority=STD)
    def serialize(self, t: type[Exactly[JSON]], obj: object, ctx: Context, /):
        if isinstance(obj, dict):
            obj = {recurse(str, k, ctx): recurse(JSON, v, ctx) for k, v in obj.items()}
        elif isinstance(obj, list):
            obj = [recurse(JSON, v, ctx) for v in obj]
        elif not isinstance(obj, JSON):
            raise ValidationError(f"Object {obj!r} is not valid JSON", ctx=ctx)
        return obj

    @ovld(priority=STD)
    def deserialize(self, t: type[Exactly[JSON]], obj: object, ctx: Context, /):
        if isinstance(obj, dict):
            obj = {recurse(str, k, ctx): recurse(JSON, v, ctx) for k, v in obj.items()}
        elif isinstance(obj, list):
            obj = [recurse(JSON, v, ctx) for v in obj]
        elif not isinstance(obj, JSON):
            raise ValidationError(f"Object {obj!r} is not valid JSON", ctx=ctx)
        return obj

    @ovld(priority=STD)
    def schema(self, t: type[Exactly[JSON]], ctx: Context, /):
        return {}

    ##########################
    # Implementations: Enums #
    ##########################

    @code_generator_wrap_error(priority=STD3)
    def serialize(cls, t: type[Enum], obj: Enum, ctx: Context, /):
        return Lambda(Code("$obj.value"))

    @code_generator_wrap_error(priority=STD3)
    def deserialize(cls, t: type[Enum], obj: Any, ctx: Context, /):
        (t,) = get_args(t)
        return Lambda(Code("$t($obj)", t=t))

    @ovld(priority=STD3)
    def schema(self, t: type[Enum], ctx: Context, /):
        return {"enum": [e.value for e in t]}

    ##################################
    # Implementations: Literal Enums #
    ##################################

    @ovld(priority=STD)
    def serialize(self, t: type[IsLiteral], obj: Any, ctx: Context, /):
        options = get_args(t)
        if obj not in options:
            raise ValidationError(f"'{obj}' is not a valid option for {t}", ctx=ctx)
        return obj

    @ovld(priority=STD)
    def deserialize(self, t: type[IsLiteral], obj: Any, ctx: Context, /):
        options = get_args(t)
        if obj not in options:
            raise ValidationError(f"'{obj}' is not a valid option for {t}", ctx=ctx)
        return obj

    @ovld(priority=STD)
    def schema(self, t: type[IsLiteral], ctx: Context, /):
        return {"enum": list(get_args(t))}

    ##########################
    # Implementations: Dates #
    ##########################

    @code_generator_wrap_error(priority=STD)
    def deserialize(cls, t: type[datetime], obj: int | float, ctx: Context, /):
        return Lambda(Code("$fromtimestamp($obj)", fromtimestamp=datetime.fromtimestamp))

    # We specify schemas explicitly because they have special formats
    # The serialization/deserializable is taken care of by their model()

    @ovld(priority=STD)
    def schema(self, t: type[date], ctx: Context, /):
        return {"type": "string", "format": "date"}

    @ovld(priority=STD)
    def schema(self, t: type[datetime], ctx: Context, /):
        return {"type": "string", "format": "date-time"}

    #########################
    # Implementations: Path #
    #########################

    @ovld(priority=STD)
    def serialize(self, t: type[Path], obj: Path, ctx: Context):
        if isinstance(ctx, WorkingDirectory) and not obj.is_absolute():
            obj = obj.relative_to(ctx.directory)
        return str(obj)

    @ovld(priority=STD)
    def deserialize(self, t: type[Path], obj: str, ctx: Context):
        pth = Path(obj).expanduser()
        if isinstance(ctx, WorkingDirectory):
            pth = ctx.directory / pth
        return pth

    @ovld(priority=STD)
    def schema(self, t: type[Path], ctx: Context, /):
        return {"type": "string"}

    ##################################
    # Implementations: From __init__ #
    ##################################

    @ovld(priority=LO4)
    def deserialize(self, t: type[object], obj: dict, ctx: Context):
        if t.__init__ is object.__init__:
            msg = f"Cannot deserialize `{obj}` to type `{clsstring(t)}.`"
            if getattr(t, "__annotations__", None) and not is_dataclass(t):
                msg += f" `{clsstring(t)}` appears to have type annotations on some fields, but it is not a dataclass. Did you mean for it to be a dataclass?"
            raise ValidationError(msg, ctx=ctx)
        # We use the Auto feature to convert __init__ to a model. force=True means we
        # will not try to find a model for t itself.
        return recurse(Annotated[t, Auto(call=False, embed_self=False, force=True)], obj, ctx)

    @ovld(priority=LO4)
    def schema(self, t: type[object], ctx: Context):
        if t.__init__ is object.__init__:
            msg = f"Cannot generate schema for type `{clsstring(t)}`."
            if getattr(t, "__annotations__", None) and not is_dataclass(t):
                msg += f" `{clsstring(t)}` appears to have type annotations on some fields, but it is not a dataclass. Did you mean for it to be a dataclass?"
            raise ValidationError(msg, ctx=ctx)
        return recurse(Annotated[t, Auto(call=False, embed_self=False, force=True)], ctx)
