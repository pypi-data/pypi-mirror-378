from binascii import b2a_hex
from collections import OrderedDict
from functools import lru_cache
from hashlib import sha256
from operator import attrgetter
from types import FunctionType, ModuleType
from typing import Any, Hashable, Protocol
from warnings import warn

primitives = (str, int, float, type(None), bytes, complex, type(Ellipsis))

importables = (type, FunctionType)  # TODO: add more of the builtin stuff

try:
    from numpy import dtype, ndarray
except ModuleNotFoundError:

    class ndarray: ...  # phony placeholder

else:
    primitives += (dtype,)


primitives_set = frozenset(primitives)


class UsesLocalsError(ValueError): ...


class UsesMainWarning(RuntimeWarning): ...


class UsesPickleWarning(RuntimeWarning): ...


class UnsupportedError(ValueError): ...


class _SHash(list):
    end = sha256(b"").digest()

    def __call__(self, value: Any) -> bytes:
        if value.__class__ in primitives_set:
            return _repr(value)
        if isinstance(value, (type, FunctionType, ModuleType)):
            return _imp(value)

        if value in self:
            return sha256(str(len(self) - self.index(value)).encode()).digest()

        try:
            self.append(value)

            if shash := getattr(value, "__shash__", None):
                return shash(self)

            ret = sha256(_imp(value.__class__))

            if isinstance(value, ndarray):
                inner = value.tolist()
            elif isinstance(value, dict):
                inner = map(self.item, value.items())
                if not isinstance(value, OrderedDict):
                    inner = sorted(inner)
            elif isinstance(value, (list, tuple)):
                inner = map(self, value)
            elif isinstance(value, (set, frozenset)):
                inner = sorted(map(self, value))
            elif isinstance(value, (range, slice)):
                inner = map(self, attrgetter("start", "stop", "step")(value))
            elif isinstance(value, primitives):
                return _repr(value)
            elif callable(red := getattr(value, "__reduce__", None)):
                warn(UsesPickleWarning(value.__class__))
                ret.update(self(red()))
                return ret.digest()
            else:
                raise UnsupportedError(value)

            for val in inner:
                ret.update(self(val))
            ret.update(self.end)
            return ret.digest()

        finally:
            self.pop()

    def item(self, item: tuple[Hashable, Any]) -> bytes:
        h = sha256(self(item[0]))
        h.update(self(item[1]))
        return h.digest()


class SHashable(Protocol):
    def __shash__(self, shash: _SHash) -> bytes: ...


def _repr(value) -> bytes:
    return sha256(repr(value).encode()).digest()


@lru_cache
def _imp(value: type | FunctionType) -> bytes:
    if isinstance(value, ModuleType):
        rep = value.__name__
    else:
        rep = f"{value.__module__}:{value.__qualname__}"
    if "<locals>" in rep:
        raise UsesLocalsError(value)
    if rep.startswith("__main__"):
        warn(UsesMainWarning(value))
    return sha256(rep.encode()).digest()


def bin_hash(value: Any) -> bytes:
    return _SHash()(value)


def hex_hash(value: Any) -> bytes:
    return b2a_hex(bin_hash(value))
