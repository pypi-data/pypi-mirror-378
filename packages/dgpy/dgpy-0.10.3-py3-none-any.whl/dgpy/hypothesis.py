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
"""dgpy.hypothesis lib"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from hypothesis import strategies as st
from hypothesis.extra.numpy import (  # type: ignore[attr-defined]
    boolean_dtypes,
    complex_number_dtypes,
    datetime64_dtypes,
    defines_strategy,
    floating_dtypes,
    integer_dtypes,
    timedelta64_dtypes,
    unsigned_integer_dtypes,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    import numpy as np

INTEGER_SIZES: tuple[Literal[8], Literal[16], Literal[32], Literal[64]] = (
    8,
    16,
    32,
    64,
)
UNSIGNED_INTEGER_SIZES: tuple[Literal[8], Literal[16], Literal[32], Literal[64]] = (
    8,
    16,
    32,
    64,
)
FLOATING_SIZES: tuple[Literal[16], Literal[32], Literal[64]] = (16, 32, 64)

COMPLEX_SIZES: tuple[Literal[64], Literal[128]] = (64, 128)
ENDIANNESS: tuple[str, str, str] = ("?", "<", ">")
DTYPE_KINDS: tuple[str, str, str, str, str, str, str] = (
    "b",
    "i",
    "u",
    "f",
    "c",
    "M",
    "m",
)


@defines_strategy()
def scalar_dtypes(
    *,
    boolean: bool = True,
    integer: bool = True,
    unsigned_integer: bool = True,
    floating: bool = True,
    complex_number: bool = True,
    datetime64: bool = True,
    timedelta64: bool = True,
    endianness: str = "?",
    floating_sizes: Sequence[Literal[16, 32, 64, 128]] = FLOATING_SIZES,
    complex_sizes: Sequence[Literal[64, 128, 192, 256]] = COMPLEX_SIZES,
    integer_sizes: Sequence[Literal[8, 16, 32, 64]] = INTEGER_SIZES,
    unsigned_integer_sizes: Sequence[Literal[8, 16, 32, 64]] = UNSIGNED_INTEGER_SIZES,
) -> st.SearchStrategy[np.dtype]:
    """Return a strategy that can return any non-flexible scalar dtype."""
    strategies = (
        boolean_dtypes() if boolean else st.nothing(),
        (
            integer_dtypes(
                endianness=endianness,
                sizes=integer_sizes,
            )
            if integer
            else st.nothing()
        ),
        (
            unsigned_integer_dtypes(
                endianness=endianness,
                sizes=unsigned_integer_sizes,
            )
            if unsigned_integer
            else st.nothing()
        ),
        (
            floating_dtypes(
                endianness=endianness,
                sizes=floating_sizes,
            )
            if floating
            else st.nothing()
        ),
        (
            complex_number_dtypes(
                endianness=endianness,
                sizes=complex_sizes,
            )
            if complex_number
            else st.nothing()
        ),
        (
            datetime64_dtypes(
                endianness=endianness,
            )
            if datetime64
            else st.nothing()
        ),
        (
            timedelta64_dtypes(
                endianness=endianness,
            )
            if timedelta64
            else st.nothing()
        ),
    )
    return st.one_of(*filter(lambda x: x is not st.nothing(), strategies))


@defines_strategy()
def scalar_basic_dtypes(
    endianness: str = "?",
) -> st.SearchStrategy[np.dtype]:
    """Return a strategy that can return any non-flexible dtype."""
    return scalar_dtypes(
        complex_number=False,
        datetime64=False,
        timedelta64=False,
        endianness=endianness,
    )


@defines_strategy()
def scalar_floating_dtypes(
    endianness: str = "?",
    sizes: Sequence[Literal[16, 32, 64, 128]] = FLOATING_SIZES,
) -> st.SearchStrategy[np.dtype]:
    """Return a strategy that can return any non-flexible dtype."""
    return scalar_dtypes(
        boolean=False,
        integer=False,
        unsigned_integer=False,
        complex_number=False,
        datetime64=False,
        timedelta64=False,
        endianness=endianness,
        floating_sizes=sizes,
    )
