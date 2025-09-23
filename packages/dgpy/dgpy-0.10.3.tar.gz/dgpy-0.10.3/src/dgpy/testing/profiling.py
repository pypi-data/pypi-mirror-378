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
"""Profiling utilities"""

from __future__ import annotations

import asyncio

from cProfile import Profile
from functools import wraps
from time import time
from typing import TYPE_CHECKING, Any, TypeVar, cast

from shellfish.sh import echo

if TYPE_CHECKING:
    from collections.abc import Callable

_T = TypeVar("_T")


def time_funk(funk: Callable[..., Any], *args: Any, **kwargs: Any) -> tuple[Any, float]:
    """Time a function and returns the function-return-value and runtime"""
    ti = time()
    _ret = funk(*args, **kwargs)
    tf = time()
    return _ret, tf - ti


def time_funks(
    f1: Callable[..., Any],
    f2: Callable[..., Any],
    runs: int = 1,
    *args: Any,
    **kwargs: Any,
) -> dict[str, str | int | float]:
    """Time two functions and returns stats as a dictionary"""
    f1_time = 0.0
    f2_time = 0.0
    for _i in range(runs):
        _r1, f1t = time_funk(f1, *args, **kwargs)
        f1_time += f1t
        _r2, f2t = time_funk(f2, *args, **kwargs)
        f2_time += f2t
    f1_time = f1_time / runs
    f2_time = f2_time / runs
    return {
        "f1": str(f1.__name__),
        "f2": str(f2.__name__),
        "f1-time": f1_time,
        "f2-time": f2_time,
        "f1/f2": f1_time / f2_time,
        "runs": runs,
    }


def cprof(funk: Callable[..., _T]) -> Callable[..., _T]:
    """Decorator to perform profiling on a function

    Args:
        funk: Function to profile

    Returns:
        Wrapped function that now will be profiled when called

    """

    @wraps(funk)
    async def _profile_wrapper_async(*args: Any, **kwargs: Any) -> _T:
        """Wrapper funk"""
        profile = Profile()
        try:
            profile.enable()
            ret_val = await funk(*args, **kwargs)  # type: ignore[misc]
            profile.disable()
        finally:
            echo("__CPROFILE__")
            profile.print_stats("cumulative")
        return cast("_T", ret_val)

    @wraps(funk)
    def _profile_wrapper(*args: Any, **kwargs: Any) -> _T:
        """Wrapper funk"""
        profile = Profile()
        try:
            profile.enable()
            ret_val = funk(*args, **kwargs)
            profile.disable()
        finally:
            echo("__CPROFILE__")
            profile.print_stats("cumulative")
        return ret_val

    if asyncio.iscoroutinefunction(funk) or asyncio.iscoroutine(funk):
        return _profile_wrapper_async  # type: ignore[return-value]
    return _profile_wrapper
