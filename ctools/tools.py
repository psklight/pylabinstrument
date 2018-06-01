from ctypes import CFUNCTYPE, CDLL
from typing import List, Any

def bind(lib: CDLL, func: str,
         argtypes: List[Any]=None, restype: Any=None) -> CFUNCTYPE:
    _func = getattr(lib, func, null_function)
    _func.argtypes = argtypes
    _func.restype = restype

    return _func


def null_function():
    pass

__all__ = [
    bind,
    null_function,
]