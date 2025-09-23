# -*- coding: utf-8 -*-
# =============================================================================
# Copyright (2025) Dynamic Graphics, Inc. Lafayette, CA, USA.
#
# This DGPY library (the "Software") may not be used except in connection with
# the Licensees use of the Dynamic Graphics' software pursuant to an
# Agreement (defined below) between Licensee (defined below) and
# Dynamic Graphics, Inc. ("DGI"). This Software shall be deemed part of the
# Licensed Software under the Agreement. Licensees use of the Software must
# comply at all times with any restrictions applicable to the Licensed
# Software, generally, and must be used in accordance with applicable
# documentation. If you have not agreed to an Agreement or otherwise do not
# agree to these terms, you may not use the Software. This license terminates
# automatically upon the termination of the Agreement or Licensees breach of
# these terms.
#
# DEFINITIONS:
#  - Agreement: The software product license agreement, as amended, executed
#               between DGI and Licensee governing the use of the DGI software.
#  - Licensee: The user of the Software, or, if the Software is being used on
#              behalf of a company, the company.
# =============================================================================
"""Decorators"""

from __future__ import annotations

import asyncio

from functools import wraps
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    TypeVar,
    overload,
)

from shellfish.fs import mkdir
from shellfish.fs._async import mkdir_async

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from dgpy._types import FsPath, P

T = TypeVar("T")


@overload
def dirdec(
    funk: Callable[P, Awaitable[FsPath]],
) -> Callable[P, Awaitable[FsPath]]: ...


@overload
def dirdec(
    funk: Callable[P, FsPath],
) -> Callable[P, FsPath]: ...


def dirdec(funk: Callable[P, Any]) -> Callable[P, Any]:
    """Ensure the existence of returned dir-path

    Decorator for functions that return dir-paths that ensures the returned
    dir-path exists.

    Args:
        funk: Function that returns a directory path

    Returns:
        Wrapped function

    Examples:
        >>> from shellfish import fs, sh
        >>> from os import mkdir, path
        >>> from shutil import rmtree
        >>> from pathlib import Path
        >>> from dgpy.decorate import dirdec
        >>> from shellfish.sh import pwd
        >>> def get_home_something_dir():
        ...     return path.join(Path.home(), "something_dir")
        >>> dirpath = get_home_something_dir()
        >>> if fs.exists(dirpath):
        ...     rmtree(dirpath)
        >>> fs.exists(dirpath)  # just removed it so it shouldn't exist
        False
        >>> @dirdec
        ... def get_home_something_dir_decorated():
        ...     return path.join(Path.home(), "something_dir")
        >>> dirpath = get_home_something_dir_decorated()
        >>> fs.exists(dirpath)  # Should exist because of @dirdec decorator
        True
        >>> if fs.exists(dirpath): rmtree(dirpath)

    """

    @wraps(funk)
    def _dirdec(*args: P.args, **kwargs: P.kwargs) -> FsPath:
        result = funk(*args, **kwargs)
        try:
            mkdir(str(result))
        except (FileExistsError, OSError):
            ...
        return result

    @wraps(funk)
    async def _dirdec_async(*args: P.args, **kwargs: P.kwargs) -> FsPath:
        result: FsPath = await funk(*args, **kwargs)
        try:
            await mkdir_async(str(result))
        except (FileExistsError, OSError):
            ...
        return result

    if asyncio.iscoroutinefunction(funk) or asyncio.iscoroutine(funk):
        return _dirdec_async
    return _dirdec


class Const(Generic[T]):
    """Generic class that wraps a function caching its return value.

    The function should take no arguments and return a value. The first time the
    function is called, it will execute the function and cache the return value.
    Subsequent calls will return the cached value without executing the function.
    The cache can be cleared or reset, which will allow the function to be called
    again and cache a new value.
    """

    value: T | None = None
    func: Callable[[], T]
    _cached: bool = False

    def __init__(self, func: Callable[[], T]) -> None:
        """Initialize with function to be cached"""
        self.func = func
        if func.__doc__:
            self.__doc__ = func.__doc__
        self.reset()

    def call_fn(self) -> T:
        return self.func()

    @property
    def cached(self) -> bool:
        return self._cached

    def __call__(self, *args: Any, **kwargs: Any) -> T:
        if self._cached:
            return self.value  # type: ignore[return-value]
        self.value = self.call_fn()
        self._cached = True
        return self.value

    def clear(self) -> bool:
        self.value = None
        if self._cached:
            self._cached = False
            return True
        return False

    def reset(self) -> bool:
        return self.clear()


def const(func: Callable[[], T]) -> Const[T]:
    """Decorator to cache the return value of a function

    Args:
        func: function to cache that takes no arguments and returns a value

    Returns:
        Const: object that wraps the function and caches its return value

    Example:
        >>> @const
        ... def func():
        ...     return 1
        >>> func.cached
        False
        >>> func.clear()  # clear the cache returns false because it was not cached
        False
        >>> func()
        1
        >>> func.cached
        True
        >>> func.clear()
        True
        >>> func.cached
        False

    """
    return Const(func)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
