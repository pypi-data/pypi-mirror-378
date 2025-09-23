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
"""ArgsKwargs class and related utilities"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypedDict

from jsonbourne import JSON

if TYPE_CHECKING:
    from collections.abc import Callable

    from dgpy._types import _R


class ArgsKwargsDict(TypedDict):
    args: tuple[Any, ...]
    kwargs: dict[str, Any]


class ArgsKwargs:
    """Dataclass for storing args and kwargs

    Examples:
        >>> ArgsKwargs(1, 2, 3, a=4, b=5)
        ArgsKwargs(args=(1, 2, 3), kwargs={'a': 4, 'b': 5})
        >>> ArgsKwargs(args=(1, 2, 3), kwargs=dict(a=4, b=5))
        ArgsKwargs(args=(1, 2, 3), kwargs={'a': 4, 'b': 5})


    """

    __slots__ = ("args", "kwargs")

    args: tuple[Any, ...]
    kwargs: dict[str, Any]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize ArgsKwargs with args and kwargs."""
        if "args" in kwargs and not args:
            args = kwargs.pop("args")
        if "kwargs" in kwargs:
            kwargs = kwargs.pop("kwargs")
        self.args = args
        self.kwargs = kwargs

    def args_str(self) -> str:
        return ", ".join(map(repr, self.args)) if self.args else ""

    def kwargs_str(self) -> str:
        return (
            ", ".join(f"{k}={v!r}" for k, v in self.kwargs.items())
            if self.kwargs
            else ""
        )

    def format(self) -> str:
        return f"({self.args_str()}, {self.kwargs_str()})"

    def __repr__(self) -> str:
        return f"ArgsKwargs(args={self.args}, kwargs={self.kwargs})"

    @classmethod
    def from_args_kwargs(cls, *args: Any, **kwargs: Any) -> ArgsKwargs:
        return cls(*args, **kwargs)

    def to_dict(self) -> ArgsKwargsDict:
        return {"args": self.args, "kwargs": self.kwargs}

    @classmethod
    def from_dict(cls, args_kwargs_dict: ArgsKwargsDict) -> ArgsKwargs:
        return cls(**args_kwargs_dict)

    def to_tuple(self) -> tuple[Any, ...]:
        return self.args, self.kwargs

    def apply(self, func: Callable[..., _R]) -> _R:
        return func(*self.args, **self.kwargs)

    def json(self, *, fmt: bool = False, sort_keys: bool = False) -> str:
        return JSON.dumps(self.to_dict(), fmt=fmt, sort_keys=sort_keys)


def args_kwargs(*args: Any, **kwargs: Any) -> ArgsKwargs:
    """Alias for ArgsKwargs.from_args_kwargs"""
    return ArgsKwargs.from_args_kwargs(*args, **kwargs)


def ak(*args: Any, **kwargs: Any) -> ArgsKwargs:
    """Alias for ArgsKwargs.from_args_kwargs"""
    return ArgsKwargs.from_args_kwargs(*args, **kwargs)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
