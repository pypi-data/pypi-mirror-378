from typing import Any

from ovld import Medley, call_next, ovld

from ..ctx import Context
from ..model import FieldModelizable
from ..priority import HI2


def unflatten(d: dict):
    rval = {}
    split_keys = [(k.split("."), v) for k, v in d.items()]
    for parts, v in sorted(split_keys, key=lambda kv: len(kv[0])):
        current = rval
        for p in parts[:-1]:
            current = current.setdefault(p, {})
        current[parts[-1]] = v
    return rval


class DottedNotation(Medley):
    @ovld(priority=HI2)
    def deserialize(self, t: Any, obj: dict, ctx: Context):
        if issubclass(t, FieldModelizable) and any("." in k for k in obj.keys()):
            return call_next(t, unflatten(obj), ctx)
        return call_next(t, obj, ctx)
