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
"""Sheldon Array Comparisons

This module contains the logic Sheldon uses for comparing arrays.
"""

from __future__ import annotations

import logging

from math import isclose
from operator import xor
from typing import TYPE_CHECKING, Any, TypeVar

import numpy as np

from fmts import string_sanitize

from dgpy.maths import array_info, array_ulp_diff, inf2nan

if TYPE_CHECKING:
    from dgpy import npt

_T = TypeVar("_T")
log = logging.getLogger(__name__)
np.seterr(invalid="ignore")


def cmp_dtype(a: Any, b: Any) -> bool:
    """Return True if a and b are both the same type; False otherwise"""
    return isinstance(a, type(b)) or isinstance(b, type(a))


def is_number(value: Any) -> bool:
    """Check if an object is a number (int/float/numpy-numbers)

    Args:
        value: Value to check

    Returns:
        True if the value is a number, False otherwise

    Examples:
        >>> is_number(1)
        True

    """
    return np.issubdtype(type(value), np.integer) or np.issubdtype(
        type(value), np.float64
    )


def is_int(number: int | float | str | np.integer | np.float64) -> bool:
    """Check if a number is an integer.

    Args:
        number: Number to check

    Returns:
        bool: True if the number is an integer, False otherwise.

    Examples:
        >>> is_int(123)
        True
        >>> is_int(123.0)
        True
        >>> is_int(123.5)
        False
        >>> is_int("123")
        True
        >>> is_int("123.0")
        True
        >>> is_int("123.5")
        False
        >>> is_int("howdy")
        False

    """
    try:
        return isinstance(number, int) or int(float(number)) == float(number)
    except ValueError:
        pass
    return False


def cmp_numbers(
    a: int | float | str | np.integer | np.float64,
    b: int | float | str | np.integer | np.float64,
    rtol: float = 10**-5,
    atol: float = 10**-8,
) -> bool:
    """Compare two numbers for equality/equivalence

    Args:
        a: first number to compare
        b: second number to compare
        rtol: Relative tolerance
        atol: Absolute tolerance

    Returns:
        True if the numbers are equivalent

    Examples:
        >>> a = -0.0146325
        >>> b = -0.01463249
        >>> cmp_numbers(a, b)
        True
        >>> a = 1.2345
        >>> b = 1.23
        >>> cmp_numbers(a, b)
        True
        >>> import numpy as np
        >>> a = np.float64(1.2345)
        >>> b = np.float64(1.23)
        >>> cmp_numbers(a, b)
        True
        >>> cmp_numbers(np.float32(1.2345), float(1.23))
        True
        >>> cmp_numbers(np.float32(1.2345), np.float64(1.23))
        True
        >>> cmp_numbers('-49.15', '-49.149')
        True

    """
    if a == b:
        return True
    a = np.float64(a)
    b = np.float64(b)
    if a.is_integer() and b.is_integer():
        return bool(a == b)
    if xor(a.is_integer(), b.is_integer()):
        return False
    if np.isclose(np.float64(a), np.float64(b), rtol=rtol, atol=atol):
        return True
    a_str = str(a)
    b_str = str(b)
    if a_str in b_str or b_str in a_str:
        return True
    if "." in a_str and "." in b_str:
        min_len = min(len(a_str), len(b_str))
        a_trunc = a_str[:min_len]
        b_trunc = b_str[:min_len]
        a_int = int(a_trunc.replace(".", ""))
        b_int = int(b_trunc.replace(".", ""))
        if abs(a_int - b_int) < 2:
            return True
    return False


def cmp_values(string_a: str | int | float, string_b: str | int | float) -> bool:
    """Compare two ascii string values

    Args:
        string_a: First string to compare
        string_b: Second string to compare

    Returns:
        Same strings will return True; strings that are not unequal should return
        False.

    Examples:
        >>> cmp_values('sheldon', 'sheldon')
        True
        >>> cmp_values('sheldon', 'shelly')
        False
        >>> cmp_values('sheldon', '#$#')
        True
        >>> cmp_values('sheldon', '#@#')
        True
        >>> cmp_values('#$#', 'sheldon')
        True
        >>> cmp_values('#@#', 'sheldon')
        True

        There are times in baselines where there are odd strings that are specific
        to the machine that is being used to run the tests. EX: On some geomechanic
        tests the script.sh file writes out the number of cores it is working on;
        this changes depending on the machine running the test. For this reason
        baseline files are allowed to contain a 'wild-card-string.' There are two
        wild card strings: '#$#' '#@#'. These were selected because:

        1. both sequences are easy to type -- hold shift and hit '343' or '323'.
        2. they have been my (jesse's) personal wild-char sequence for quite some time
           a machines

        If a wild-character sequence is present sheldon will always evaluate the
        string-comparison as True.


        A common problem that sheldon has to deal with is filepaths. Sheldon
        will try to resolve strings that represent paths to a linux-style path
        (forward slashes) and do the comparison with them.

        >>> cmp_values('1.123456', '1.123456')
        True
        >>> cmp_values('-49.15', '-49.149')
        True
        >>> cmp_values('1.123456', '1.1234')
        True
        >>> cmp_values('200e-9', '201e-9')
        True
        >>> cmp_values('9e+7', '8e+7')
        False
        >>> cmp_values('1.123456E-7', '1.123456E-7')
        True

        The function will try to compare values as floats. If the strings can be
        coerced to floats, the comparison will return true if the float values have
        an absolute difference of 0.00001 or less.

        >>> a = '-0.0146325'
        >>> b = '-0.01463249'
        >>> cmp_values(a, b)
        True
        >>> a = '-0.0146325'
        >>> b = 'GRAHAM_BREW'
        >>> cmp_values(a, b)
        False

    """
    if string_a == string_b:
        return True
    if string_a in ("#@#", "#$#") or string_b in ("#@#", "#$#"):
        return True
    try:
        return cmp_numbers(string_a, string_b)
    except ValueError:
        pass
    try:
        return int(string_a) == int(string_b)
    except ValueError:
        pass
    string_a = str(string_a).strip('"')
    string_b = str(string_b).strip('"')

    try:
        float_a, float_b = float(string_a), float(string_b)
        if float_a == float_b:
            return True
        if np.isclose(float_a, float_b, atol=0.00001):
            return True

        if isclose(float_a, float_b, abs_tol=0.00001):
            return True
        if cmp_numbers(float_a, float_b):
            return True
        if len(string_a) != len(string_b):
            a_gt_one, a_lt_one = string_a.split(".")
            b_gt_one, b_lt_one = string_b.split(".")
            decimal_places = min((len(a_lt_one), len(b_lt_one)))
            if np.isclose(
                round(float(string_a), decimal_places),
                round(float(string_b), decimal_places),
                atol=0.00001,
            ):
                return True
        if abs(float_a - float_b) < 0.00001:  # maybe check for rounding error
            return True
    except ValueError:
        pass
    clean_a = string_sanitize(string_a)
    clean_b = string_sanitize(string_b)
    if string_a != clean_a or string_b != clean_b:
        return cmp_values(clean_a, clean_b)
    return False


def array_diff_info(
    a_arr: npt.NDArray, b_arr: npt.NDArray, eq_arr: npt.NDArray
) -> dict[str, str]:
    """Return array info dictionary for the 'difference' array of two given arrays

    Args:
        a_arr: Numpy array to compare
        b_arr: Another numpy array to compare
        eq_arr: Boolean array of the equality of the two other arrays.

    Returns:
        Info dictionary

    """
    _eq_arr_1d = np.invert(np.ravel(eq_arr))
    _a_arr_1d = np.ravel(a_arr)[_eq_arr_1d]
    _b_arr_1d = np.ravel(b_arr)[_eq_arr_1d]
    diff_arr = np.abs(_a_arr_1d - _b_arr_1d)
    return array_info(diff_arr)


def cmp_arr(
    a_arr: npt.ArrayLike,
    b_arr: npt.ArrayLike,
    max_ulp: int = 2,
    rtol: float = 10**-5,
    atol: float = 10**-8,
) -> Any:
    """Compare two numpy arrays for equivalence

    Args:
        a_arr (numpy-array): Array to compare
        b_arr (numpy-array): Array to compare
        max_ulp (int): Maximum allowed Units-(in)-Last-Place/ULP; defaults to 2
        rtol (float): relative tolerance
        atol (float): absolute tolerance

    Returns:
        True/False and a dictionary of information of problems/issues

    """
    try:
        _a_arr: npt.NDArray = np.array(a_arr, dtype=np.float32)
        _b_arr: npt.NDArray = np.array(b_arr, dtype=np.float32)
    except ValueError:
        _a_arr = np.array(a_arr, dtype=np.str_)
        _b_arr = np.array(b_arr, dtype=np.str_)
        _a_arr = _a_arr[np.where(_a_arr != "")]
        _b_arr = _b_arr[np.where(_b_arr != "")]
    try:
        if np.issubdtype(_b_arr.dtype, np.floating) or np.issubdtype(
            _b_arr.dtype, np.integer
        ):
            _b_arr = inf2nan(_b_arr)
        if np.issubdtype(_a_arr.dtype, np.floating) or np.issubdtype(
            _a_arr.dtype, np.integer
        ):
            _a_arr = inf2nan(_a_arr)
    except Exception as e:
        log.debug("cmp_arr exception: {}", str(e), exc_info=True)

    if set(_a_arr.shape) != set(_b_arr.shape):
        problems = {
            "dimensions_not_equal": {"A": array_info(_a_arr), "B": array_info(_b_arr)}
        }
        return False, problems

    try:
        np.testing.assert_equal(_a_arr, _b_arr)
        return True, {}
    except AssertionError:
        pass

    try:
        ulp_arr = array_ulp_diff(_a_arr, _b_arr)
        ulp_arr_max = int(np.max(ulp_arr))
        if ulp_arr_max <= max_ulp:
            return True, {}
        _equality_arr: npt.NDArrayBool = np.isclose(
            inf2nan(_a_arr), inf2nan(_b_arr), rtol=rtol, atol=atol, equal_nan=True
        )
        n_total_values = np.size(_equality_arr)
        n_equal_values = np.count_nonzero(_equality_arr)
        n_not_equal_values = n_total_values - n_equal_values
        # Check if the number of values that are equal are all the values
        if n_not_equal_values == 0:
            return True, {}

        _a_arr_nonequal = _a_arr[~_equality_arr]
        _b_arr_nonequal = _b_arr[~_equality_arr]
        if all(
            cmp_values(*values)
            for values in zip(
                _a_arr_nonequal.ravel(), _b_arr_nonequal.ravel(), strict=False
            )
        ):
            return True, {}

        try:
            return (
                False,
                {
                    "max_ulp_difference": int(str(ulp_arr_max)),
                    "n_total_values": int(n_total_values),
                    "n_equal_values": int(n_equal_values),
                    "n_not_equal_values": int(n_not_equal_values),
                    "A": array_info(_a_arr),
                    "B": array_info(_b_arr),
                    "ALL_VALS_ABS_DIFF": array_info(np.abs(_a_arr - _b_arr)),
                    "NON_EQUAL_VALS_ABS_DIFF": array_diff_info(
                        _a_arr, _b_arr, _equality_arr
                    ),
                },
            )
        except RuntimeWarning as e:
            log.debug(
                "cmp_arr Runtime Warning: %s",
                str(e),
                exc_info=True,
            )
    except TypeError as e:
        log.debug(
            "cmp_arr TypeError: %s",
            str(e),
            exc_info=True,
        )

    n_not_equal_values = np.sum(_a_arr == _b_arr)
    return (
        False,
        {
            "n_not_equal_values": int(n_not_equal_values),
            "A": array_info(_a_arr),
            "B": array_info(_b_arr),
        },
    )


def cmp_set(left: set[_T], right: set[_T]) -> tuple[set[_T], set[_T], set[_T]]:
    """Compare 2 python Set objects

    Args:
        left: set object
        right: set object

    Returns:
        tuple of sets: (common, left-only, right-only)

    """
    left, right = set(left), set(right)
    return left & right, left - right, right - left
