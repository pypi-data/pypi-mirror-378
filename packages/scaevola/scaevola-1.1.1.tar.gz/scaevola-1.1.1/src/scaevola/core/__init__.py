import enum
import functools
import operator
import tomllib
import types
from importlib import resources
from typing import *

__all__ = ["Scaevola", "auto", "getfuncnames", "makefunc"]


class Util(enum.Enum):
    "This enum provides a singleton."
    util = None

    @functools.cached_property
    def data(self: Self) -> dict:
        "This cached property holds the cfg data."
        text: str = resources.read_text("scaevola.core", "cfg.toml")
        ans: dict = tomllib.loads(text)
        return ans

    @functools.cached_property
    def funcdata(self: Self) -> dict:
        "This cached property holds the data for easy function making."
        ans: dict = dict()
        name: str
        doc: str
        inner: Callable
        name = "__ge__"
        doc = self.data["docs"]["ge"]
        inner = operator.le
        ans[name] = dict(doc=doc, inner=inner)
        name = "__gt__"
        doc = self.data["docs"]["gt"]
        inner = operator.lt
        ans[name] = dict(doc=doc, inner=inner)
        name = "__rdivmod__"
        doc = self.data["docs"]["rdivmod"]
        inner = divmod
        ans[name] = dict(doc=doc, inner=inner)
        x: Any
        y: Any
        for x, y in self.data["operator"].items():
            name = "__r%s__" % x.rstrip("_")
            doc = self.data["docs"]["operator"] % y
            inner = getattr(operator, x)
            ans[name] = dict(doc=doc, inner=inner)
        ans = dict(sorted(ans.items()))
        return ans


def auto(cls: type) -> type:
    "This decorator implements all the righthand functions."
    name: str
    for name in getfuncnames():
        if name not in cls.__dict__.keys():
            makefunc(cls, name)
    return cls


def getfuncnames() -> list[str]:
    "This function returns the names of all righthand functions."
    return list(Util.util.funcdata.keys())


def makefunc(cls: type, name: str) -> types.FunctionType:
    "This function implements a certain righthand function."
    inner: Callable = Util.util.funcdata[name]["inner"]

    def outer(self: Self, other: Any) -> Any:
        "This docstring will be overwritten."
        return inner(type(self)(other), self)

    outer.__doc__ = Util.util.funcdata[name]["doc"]
    outer.__module__ = cls.__module__
    outer.__name__ = name
    outer.__qualname__ = cls.__qualname__ + "." + name
    setattr(cls, name, outer)
    return outer


@auto
class Scaevola:
    pass
