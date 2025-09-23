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
"""Numpy, Pandas & XArray utilities and functions"""

from __future__ import annotations

import logging

from functools import wraps
from typing import TYPE_CHECKING, Any, TypeAlias, TypeVar

import numpy as np
import pandas as pd

from dgpy.const import NAN_8BIT_VAL, NAN_16BIT_VAL

if TYPE_CHECKING:
    from collections.abc import Callable

    from dgpy import npt

_BOTTLENECK = False
try:
    import bottleneck as bnp

    _BOTTLENECK = True
except ImportError:
    bnp = np

T = TypeVar("T")
log = logging.getLogger(__name__)
Number: TypeAlias = float | int | np.int_ | np.float64

EPSILON = np.finfo(float).eps * 4.0

__all__ = (
    "EPSILON",
    "abs_diff",
    "angle",
    "arr_bit_factor_shift",
    "arr_inf2nan",
    "array_info",
    "array_ulp_diff",
    "cat_transform_matrices",
    "full_outer_join",
    "inf2nan",
    "integer_repr",
    "invmat",
    "is_multiindex",
    "mag",
    "mktransform",
    "mse",
    "n_inf",
    "n_nan",
    "nanmax",
    "nanmean",
    "nanmin",
    "nanstd",
    "nansum",
    "nanvar",
    "nparray",
    "pack_8_bit_arr",
    "pack_16_bit_arr",
    "pack_816_bit_arr",
    "parallelepiped_bounding_box",
    "parallelepiped_points",
    "quaternion_equiv",
    "quick_maths",
    "ravel_arrays",
    "replace",
    "rm_ditto",
    "rm_inf",
    "rm_inf_nan",
    "rm_nan",
    "rotation_matrix_3d",
    "signed_angle",
    "transform_equiv",
    "unpack_8_bit_arr",
    "unpack_16_bit_arr",
    "unpack_816_bit_arr",
)


# =============================================================================
# NUMPY
# =============================================================================
def ravel_arrays(funk: Callable[..., T]) -> Callable[..., T]:
    """Ravel any args/kwargs for a function that are numpy arrays

    Args:
        funk: function that may receive numpy arrays as args/kwargs

    Returns:
        Wrapped function that ravels all input numpy arrays before executing

    Examples:
        Imports:

        >>> from dgpy.maths import ravel_arrays
        >>> import numpy as np

        Define a function that takes an array as an argument:

        >>> def funk(arr):
        ...     print("Array:")
        ...     print(arr)
        ...     print("Shape:", arr.shape)

        Make an array:

        >>> arr = np.array([[1, 2], [3, 4]])

        There's the array:

        >>> arr
        array([[1, 2],
               [3, 4]])

        Call the function (it will probably print the input array its shape):

        >>> funk(arr)
        Array:
        [[1 2]
         [3 4]]
        Shape: (2, 2)

        Create the same function, but decorate it with `@ravel_arrays`:

        >>> @ravel_arrays
        ... def funk(arr):
        ...     print("Array:")
        ...     print(arr)
        ...     print("Shape:", arr.shape)

        Call the wrapped function:

        >>> funk(arr)
        Array:
        [1 2 3 4]
        Shape: (4,)

        The above shows how the input arrays will be `ravel-ed` before the
        function executes. Below is another way of using the decorator on a
        function:

        >>> def funk(arr):
        ...     print("Array:")
        ...     print(arr)
        ...     print("Shape:", arr.shape)
        >>> raveled_funk = ravel_arrays(funk)
        >>> raveled_funk(arr)
        Array:
        [1 2 3 4]
        Shape: (4,)

    """

    def _ravel_if_ndarray(arg: Any) -> Any:
        if isinstance(arg, np.ndarray):
            return arg.ravel()
        return arg

    @wraps(funk)
    def _funk(*args: Any, **kwargs: Any) -> T:
        args = tuple(_ravel_if_ndarray(arg) for arg in args)
        kwargs = {k: _ravel_if_ndarray(v) for k, v in kwargs.items()}
        return funk(*args, **kwargs)

    return _funk


def nparray(funk: Callable[..., T]) -> Callable[..., T]:
    """Convert list/tuple args and kwargs to numpy arrays

    Args:
        funk: Function to decorate

    Returns:
        Function that takes numpy arrays as arguments

    Examples:
        Imports:

        >>> from dgpy.maths import nparray
        >>> import numpy as np

        Define a function that takes an array as an argument:

        >>> def funk(arr):
        ...     print("Array:")
        ...     print(arr)
        ...     print("type:", type(arr))

        Make an list:

        >>> arr = [1, 2, 3, 4]

        Call the function (it will probably print the input arg and its type):

        >>> funk(arr)
        Array:
        [1, 2, 3, 4]
        type: <class 'list'>

        Create the same function, but decorate it with `@nparray`:

        >>> @nparray
        ... def funk(arr):
        ...     print("Array:")
        ...     print(arr)
        ...     print("type:", type(arr))

        Call the wrapped function:

        >>> funk(arr)
        Array:
        [1 2 3 4]
        type: <class 'numpy.ndarray'>

        It also works with tuples:

        >>> funk((5, 6, 7, 8))
        Array:
        [5 6 7 8]
        type: <class 'numpy.ndarray'>

        The above shows how the input lists and tuples will be converted to
        np.array objects before entering the function. Below is another way of
        using the decorator on a function:

        >>> def funk(arr):
        ...     print("Array:")
        ...     print(arr)
        ...     print("type:", type(arr))
        >>> wrapped_funk = nparray(funk)
        >>> wrapped_funk(arr)
        Array:
        [1 2 3 4]
        type: <class 'numpy.ndarray'>

    """

    def _arrayify(arg: Any) -> Any:
        if isinstance(arg, list) or isinstance(arg, tuple):
            return np.asarray(arg)
        return arg

    @wraps(funk)
    def _funk(*args: Any, **kwargs: Any) -> T:
        args = tuple(_arrayify(arg) for arg in args)
        kwargs = {k: _arrayify(v) for k, v in kwargs.items()}
        return funk(*args, **kwargs)

    return _funk


def parallelepiped_points(
    pivot_point: npt.NDArray,
    loc_x_axis: npt.NDArray,
    loc_y_axis: npt.NDArray,
    loc_z_axis: npt.NDArray,
) -> npt.NDArray:
    """Get the coordinates of points belonging to a parallelpiped

    Args:
        pivot_point: parallelpiped pivot point
        loc_x_axis: parallelpiped local x axis/vector
        loc_y_axis: parallelpiped local y axis/vector
        loc_z_axis: parallelpiped local z axis/vector

    Returns:
        Numpy array with rows as the parallelpiped's points

    """
    points = [
        np.array([0, 0, 0]),
        loc_x_axis,
        loc_y_axis,
        loc_z_axis,
        loc_x_axis + loc_y_axis,
        loc_x_axis + loc_z_axis,
        loc_y_axis + loc_z_axis,
        loc_x_axis + loc_y_axis + loc_z_axis,
    ]
    return np.stack([pivot_point + pt for pt in points])


@nparray
def parallelepiped_bounding_box(
    pivot_point: npt.NDArray,
    loc_x_axis: npt.NDArray,
    loc_y_axis: npt.NDArray,
    loc_z_axis: npt.NDArray,
) -> dict[str, float]:
    """Get the xyz min and max bounding box values for a parallelpiped

    Args:
        pivot_point: parallelpiped pivot point
        loc_x_axis: parallelpiped local x axis/vector
        loc_y_axis: parallelpiped local y axis/vector
        loc_z_axis: parallelpiped local z axis/vector

    Returns:
        Dictionary with the labeled values

    """
    x, y, z = parallelepiped_points(
        pivot_point=pivot_point,
        loc_x_axis=loc_x_axis,
        loc_y_axis=loc_y_axis,
        loc_z_axis=loc_z_axis,
    ).T
    return {
        "xminboundingbox": np.amin(x),
        "xmaxboundingbox": np.amax(x),
        "yminboundingbox": np.amin(y),
        "ymaxboundingbox": np.amax(y),
        "zminboundingbox": np.amin(z),
        "zmaxboundingbox": np.amax(z),
    }


def rotation_matrix_3d(
    axis: npt.NDArray | list[int | float] | tuple[int | float, ...],
    theta: float,
    *,
    degrees: bool = False,
) -> npt.NDArray:
    """Get the 3D clockwise rotation matrix given an axis and theta (radians)

    Args:
        axis: rotation axis
        theta: angle in radians of the rotation
        degrees: False => theta is in radians; True => theta is in degrees

    Returns:
        3x3 rotation matrix

    Examples:
        Radians (default):

        >>> import numpy as np
        >>> rotation_matrix_3d([1, 0, 0], np.pi/6)
        array([[ 1.       ,  0.       ,  0.       ],
               [ 0.       ,  0.8660254, -0.5      ],
               [ 0.       ,  0.5      ,  0.8660254]])

        Degrees:

        >>> rotation_matrix_3d([1, 0, 0], 30, degrees=True)
        array([[ 1.       ,  0.       ,  0.       ],
               [ 0.       ,  0.8660254, -0.5      ],
               [ 0.       ,  0.5      ,  0.8660254]])

        Radians (negative):

        >>> rotation_matrix_3d([1, 0, 0], -np.pi/6)
        array([[ 1.       ,  0.       ,  0.       ],
               [ 0.       ,  0.8660254,  0.5      ],
               [ 0.       , -0.5      ,  0.8660254]])

        Degrees (negative):

        >>> rotation_matrix_3d([1, 0, 0], -30, degrees=True)
        array([[ 1.       ,  0.       ,  0.       ],
               [ 0.       ,  0.8660254,  0.5      ],
               [ 0.       , -0.5      ,  0.8660254]])

    """
    if degrees:
        theta = np.deg2rad(theta)
    _axis: npt.NDArray = np.asarray(axis)
    _axis = _axis / np.sqrt(np.dot(_axis, _axis))
    a = np.cos(theta / 2.0)
    b, c, d = -_axis * np.sin(theta / 2.0)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return np.array([
        [aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
        [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
        [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc],
    ])


def replace(arr: npt.NDArray, old: Any, new: Any) -> npt.NDArray:
    """Replace a value in a numpy array

    Args:
        arr: Input array
        old (Any): old value to be replaced
        new (Any): new value to replace with

    Returns:
        np.ndarray

    """
    if _BOTTLENECK:
        return bnp.replace(arr, old, new)
    if old == np.nan or np.isnan(old):
        arr[np.isnan(arr)] = new
    if old == np.inf or np.isinf(old):
        arr[np.isinf(arr)] = new
    else:
        arr[arr == old] = new
    return arr


@nparray
def arr_inf2nan(arr: npt.NDArray) -> npt.NDArray:
    """Convert all `inf` values in an array to `nan`

    Args:
        arr: input array possibly containing inf(inity) values

    Returns:
        array where all `inf` values have been converted to `nan`

    Examples:
        >>> import numpy as np
        >>> vals = [1, np.inf, 2, np.inf, np.inf, 3, np.inf, np.inf]
        >>> arr = np.array(vals)
        >>> arr
        array([ 1., inf,  2., inf, inf,  3., inf, inf])
        >>> arr_inf2nan(arr)
        array([ 1., nan,  2., nan, nan,  3., nan, nan])

    """
    return replace(arr, np.inf, np.nan)


def inf2nan(arr: npt.NDArray) -> npt.NDArray:
    """Alias function for `dgpy.maths.arr_inf2nan`"""
    return arr_inf2nan(arr)


def rm_nan(arr: npt.NDArray) -> npt.NDArray:
    """Remove `nan` values from an array

    Args:
        arr: Input array possibly containing nan values

    Returns:
        input array excluding all nan values

    Examples:
        >>> import numpy as np
        >>> vals = [1, np.nan, 2, np.nan, np.nan, 3, np.nan, np.nan]
        >>> arr = np.array(vals)
        >>> arr
        array([ 1., nan,  2., nan, nan,  3., nan, nan])
        >>> rm_nan(arr)
        array([1., 2., 3.])

    """
    return arr[~np.isnan(arr)]


def rm_inf(arr: npt.NDArray) -> npt.NDArray:
    """Remove `inf` values from an array

    Args:
        arr: Input numpy array possibly containing `inf` values

    Returns:
        Input array excluding the `np.inf` values

    Examples:
        >>> import numpy as np
        >>> vals = [1, np.inf, 2, np.inf, np.inf, 3, np.inf, np.inf]
        >>> arr = np.array(vals)
        >>> arr
        array([ 1., inf,  2., inf, inf,  3., inf, inf])
        >>> rm_inf(arr)
        array([1., 2., 3.])


    """
    return arr[~np.isinf(arr)]


def rm_inf_nan(arr: npt.NDArray) -> npt.NDArray:
    """Remove `inf` and `nan` values from an array

    Args:
        arr: Input array possibly containing `nan` and/or `inf` values

    Returns:
        Input array excluding `inf` and `nan` values

    Examples:
        >>> import numpy as np
        >>> vals = [1, np.inf, 2, np.inf, np.nan, np.inf, np.inf]
        >>> arr = np.array(vals)
        >>> arr
        array([ 1., inf,  2., inf, nan, inf, inf])
        >>> rm_inf_nan(arr)
        array([1., 2.])

    """
    return rm_nan(rm_inf(arr))


@nparray
@ravel_arrays
def nanmin(
    arr: npt.NDArray, *, inf2nan: bool = False
) -> np.float32 | np.float64 | float:
    """Get the minimum value for an array not counting nulls/nans

    Args:
        arr: input array
        inf2nan (bool): Convert np.inf values to np.nan before computing

    Returns:
        Array minimum


    """
    if inf2nan:
        arr = arr_inf2nan(arr)
    if arr.size == 0:
        return np.nan
    return bnp.nanmin(arr)


@nparray
@ravel_arrays
def nanmax(
    arr: npt.NDArray, *, inf2nan: bool = False
) -> np.float32 | np.float64 | float:
    """Get the maximum value for an array not counting nulls/nans

    Args:
        arr: input array
        inf2nan (bool): Convert np.inf values to np.nan before computing

    Returns:
        Array maximum

    """
    if inf2nan:
        arr = arr_inf2nan(arr)
    if arr.size == 0:
        return np.nan
    return bnp.nanmax(arr)


def nanminmax(
    arr: npt.NDArray, *, inf2nan: bool = False
) -> tuple[np.float32 | np.float64 | float, np.float32 | np.float64 | float]:
    """Return the nanmin and nanmax of an array as a tuple"""
    if inf2nan:
        arr = arr_inf2nan(arr)
    return nanmin(arr), nanmax(arr)


@nparray
@ravel_arrays
def nanvar(
    arr: npt.NDArray, *, inf2nan: bool = False
) -> np.float32 | np.float64 | float:
    """Get the variance for an array not counting nulls/nans

    Args:
        arr: input array
        inf2nan (bool): Convert np.inf values to np.nan before computing

    Returns:
        Array variance

    """
    if inf2nan:
        arr = arr_inf2nan(arr)
    if arr.size == 0:
        return np.nan
    return bnp.nanvar(arr)


@nparray
@ravel_arrays
def nanmean(
    arr: npt.NDArray, *, inf2nan: bool = False
) -> np.float64 | float | np.float32:
    """Get the mean for an array not counting nulls/nans

    Args:
        arr: input array
        inf2nan (bool): Convert np.inf values to np.nan before computing

    Returns:
        Array mean

    """
    if inf2nan:
        arr = arr_inf2nan(arr)
    if arr.size == 0:
        return np.nan
    return float(bnp.nanmean(arr))


@nparray
@ravel_arrays
def nanstd(arr: npt.NDArray, *, inf2nan: bool = False) -> float:
    """Get the standard deviation for an array not counting nulls/nans

    Args:
        inf2nan (bool): Convert `np.inf`/`-np.inf` to `np.nan` before calculating nanstd
        arr: input array

    Returns:
        Array standard deviation

    """
    if inf2nan:
        arr = arr_inf2nan(arr)
    if arr.size == 0:
        return np.nan
    return float(bnp.nanstd(arr))


@nparray
@ravel_arrays
def nansum(arr: npt.NDArray, *, inf2nan: bool = False) -> float:
    """Get the standard deviation for an array not counting nulls/nans

    Args:
        arr: input array
        inf2nan (bool): Convert np.inf values to np.nan before computing

    Returns:
        Array standard deviation

    """
    if inf2nan:
        arr = arr_inf2nan(arr)
    if arr.size == 0:
        return float(np.nan)
    return float(bnp.nansum(arr))


@nparray
def n_nan(arr: npt.NDArray) -> int:
    """Get the number of nan values in an array

    Args:
        arr: input array possibly containing nan values

    Returns:
        int: The number of nans in the array

    """
    return int(np.count_nonzero(np.isnan(arr.ravel())))


@nparray
def n_inf(arr: npt.NDArray) -> int:
    """Get the number of inf(inity) values in an array

    Args:
        arr: input array possibly containing (inf)inity values

    Returns:
        int: The number of inf(inity) values in the array

    """
    return int(np.count_nonzero(np.isinf(arr.ravel())))


def unpack_816_bit_arr(
    arr: npt.NDArray, factor: float, shift: float, nan_value: int
) -> npt.NDArray:
    """Unpack an 8/16 bit array to an array with a dtype 32-bit float

    Args:
        nan_value ():
        arr: Array to unpack
        factor: The factor to multiply by
        shift: The shift to add to each node in the array

    Returns:
        Unpacked array

    Examples:
        >>> import numpy as np
        >>> arr = np.array(list(range(0, 20, 3)))
        >>> arr
        array([ 0,  3,  6,  9, 12, 15, 18])
        >>> unpacked_array = unpack_816_bit_arr(arr, 1.5, 10, nan_value=NAN_16BIT_VAL)
        >>> unpacked_array
        array([10. , 14.5, 19. , 23.5, 28. , 32.5, 37. ])
        >>> unpacked_array.dtype
        dtype('float64')

    """
    arr = arr.astype(dtype=np.float64)
    replace(arr, nan_value, np.nan)
    arr *= factor
    arr += shift
    return arr


def unpack_8_bit_arr(arr: npt.NDArray, factor: float, shift: float) -> npt.NDArray:
    """Unpack an 8 bit array with a factor and shift

    This function takes an 8 bit array, factor and shift to create a new array
    of alternate bit size

    Args:
        arr: Numpy 8 bit array to unpack
        factor: Numerical divisor for creating new array of alternate bit size
        shift: Scalar shift for creating new array of alternate bit size

    Returns:
        Unpacked array of alternate bit size

    """
    return unpack_816_bit_arr(arr, factor, shift, NAN_8BIT_VAL)


def unpack_16_bit_arr(arr: npt.NDArray, factor: float, shift: float) -> npt.NDArray:
    """Unpack a 16 bit array with a factor and shift to a 32 bit array

    Args:
        arr: Numpy 16 bit array to unpack
        factor: Numerical divisor for creating new array of alternate bit size
        shift: Scalar shift for creating new array of alternate bit size

    Returns:
        Unpacked array of alternate bit size

    """
    return unpack_816_bit_arr(arr, factor, shift, NAN_16BIT_VAL)


def pack_816_bit_arr(
    arr: npt.ArrayLike, factor: float, shift: float, nan_value: float
) -> npt.NDArray:
    """Pack an 32 bit float array to integers

    Args:
        arr: Array to pack
        factor: The factor to divide by
        shift: The shift to subtract from each node in the array
        nan_value (float): The nan value to pack the array with

    Returns:
        Packed array

    """
    if not isinstance(arr, np.ndarray):
        return pack_816_bit_arr(np.array(arr), factor, shift, nan_value)
    arr = np.array(arr)
    nan_indices = np.where(np.isnan(arr_inf2nan(arr)))
    _arr = np.floor((arr - shift) / factor)
    _arr[nan_indices] = nan_value
    return _arr


def pack_16_bit_arr(arr: npt.ArrayLike, factor: float, shift: float) -> npt.NDArray:
    """Pack an 32 bit float array to an array with 16-bit integers

    Args:
        arr: Array to pack
        factor: The factor to divide by
        shift: The shift to subtract from each node in the array

    Returns:
        Packed array with 16-bit integers

    """
    return pack_816_bit_arr(arr, factor, shift, nan_value=NAN_16BIT_VAL).astype(
        dtype=np.uint16
    )


def pack_8_bit_arr(arr: npt.ArrayLike, factor: float, shift: float) -> npt.NDArray:
    """Pack an 32 bit float array to an array with 8-bit integers

    Args:
        arr: Array to pack
        factor: The factor to divide by
        shift: The shift to subtract from each node in the array

    Returns:
        Packed array with 8-bit integers

    """
    return pack_816_bit_arr(arr, factor, shift, nan_value=NAN_8BIT_VAL).astype(
        dtype=np.uint8
    )


def arr_bit_factor_shift(arr: npt.ArrayLike, bits: int = 16) -> tuple[float, float]:
    """Get factor and shift for creating alternate bit size array from original

    Args:
        arr: Numpy array for which you want to resize as different bit size
        bits: Target bit size for array

    Returns:
        factor: Divisor for creating shifted array
        shift: Scalar shift before dividing to create shifted array

    """
    if not isinstance(arr, np.ndarray):
        return arr_bit_factor_shift(np.array(arr), bits=bits)

    max_val = (1 << bits) - 2
    _gmin = nanmin(arr, inf2nan=True)
    _gmax = nanmax(arr, inf2nan=True)
    if _gmin == np.nan:
        factor = 1.0
        shift = 0.0
    elif _gmin == _gmax:
        factor = 1.0
        shift = float(_gmin)
    else:
        factor = abs(float(_gmax - _gmin)) / float(max_val)
        shift = float(_gmin)
    return factor, shift


@nparray
def array_info(arr: npt.NDArray) -> dict[str, str]:
    """Get info about a numpy array

    Args:
        arr: Array for which one/you want to get the info

    Returns:
        Dictionary containing info on the array given as a parameter

    """
    try:
        arr = np.array(arr, dtype=np.float32)
    except ValueError as e:
        log.debug("Unable to convert array to float32: %s -- %s", arr, e)
    try:
        info_dict = {
            "dtype": str(arr.dtype),
            "dimensions": str(tuple(arr.shape)),
            "n_nulls": str(n_nan(arr)),
            "n_inf": str(n_inf(arr)),
            "sum": str(nansum(arr)),
            "min": str(nanmin(arr)),
            "max": str(nanmax(arr)),
            "variance": str(nanvar(arr)),
            "stddev": str(nanstd(arr)),
            "mean": str(nanmean(arr)),
        }

    except TypeError as e:
        log.debug("Array Info TypeError: %s", e, exc_info=True)
        info_dict = {"dtype": str(arr.dtype), "dimensions": str(tuple(arr.shape))}
    return info_dict


@nparray
def mse(a_arr: npt.NDArray, b_arr: npt.NDArray) -> np.float32:
    """Mean squared error (mse) between of two arrays of the same shape

    The mean squared error of two arrays is the sum of the squared difference
    of the arrays.

    Args:
        a_arr: first array
        b_arr: second array

    Returns:
        mean squared error as a float; lower is better

    """
    return np.square(np.subtract(a_arr, b_arr)).mean()


def _integer_repr(x: npt.NDArray, vdt: npt.DTypeLike, comp: np.int_) -> npt.NDArray:
    """Get the integer representation array

    Ripped from the private numpy methods

    Reinterpret binary representation of the float as sign-magnitude:
    take into account two-complement representation

    Args:
        x: input array
        vdt: array integer-datatype
        comp: power-of-two-complement integer value

    Returns:
        integer repr array

    """
    rx = x.view(vdt)
    if not (rx.size == 1):
        rx[rx < 0] = comp - rx[rx < 0]
    else:
        if rx < 0:
            rx = comp - rx
    return rx


def integer_repr(x: npt.NDArray) -> npt.NDArray:
    """Get the integer representation for an array

    This returns the signed-magnitude interpretation of the binary
        representation of the input array

    Ripped from the private numpy methods

    """
    if x.dtype == np.float16:
        comp = np.int_(-(2**15))
        return _integer_repr(x, np.int16, comp)
    elif x.dtype == np.float32:
        return _integer_repr(x, np.int32, np.int_(-(2**31)))
    elif x.dtype == np.float64:
        return _integer_repr(x, np.int64, np.int_(-(2**63)))
    raise ValueError(f"Unsupported dtype {x.dtype}")


def abs_diff(
    a_arr: npt.NDArray, b_arr: npt.NDArray, dtype: npt.DTypeLike | None = None
) -> npt.NDArray:
    """Get an array of the absolute differences between two arrays

    Args:
        a_arr: numpy array
        b_arr: numpy array
        dtype: data type of the numpy arrays

    Returns:
       np.ndarray: absolute difference array

    """
    return np.abs(np.array(a_arr - b_arr, dtype=dtype))


def array_ulp_diff(
    a_arr: npt.NDArray, b_arr: npt.NDArray, dtype: Any | None = None
) -> npt.NDArray | np.float32:
    """Return the maximum ulp difference for two arrays

    Args:
        a_arr (numpy.array): Array to compare
        b_arr (numpy.array): Array compare
        dtype (numpy.dtype): Datatype of the arrays

    Returns:
        The maximum ulp difference for two arrays.

    """
    if dtype:
        a_arr = np.array(a_arr, dtype=dtype)
        b_arr = np.array(b_arr, dtype=dtype)
    else:
        a_arr = np.array(a_arr)
        b_arr = np.array(b_arr)

    t = np.common_type(a_arr, b_arr)
    if np.iscomplexobj(a_arr) or np.iscomplexobj(b_arr):
        raise NotImplementedError("_nulp not implemented for complex array")

    a_arr = np.array(a_arr, dtype=t)
    b_arr = np.array(b_arr, dtype=t)

    if not a_arr.shape == b_arr.shape:
        raise ValueError(
            f"x and y do not have the same shape: {a_arr.shape} - {b_arr.shape}"
        )

    rx = integer_repr(a_arr)
    ry = integer_repr(b_arr)
    return abs_diff(rx, ry, t)


def mag(vector: npt.NDArray) -> float | npt.NDArray:
    """Return the magnitude of `vector`.

    For stacked inputs, compute the magnitude of each one.

    Args:
        vector (np.arraylike): A `3x1` vector or a `kx3` stack of vectors.

    Returns:
        object: For `3x1` inputs, a `float` with the magnitude. For `kx1`
            inputs, a `kx1` array.

    """
    if vector.ndim > 2:
        ValueError("Too many dimensions!")
    if vector.ndim == 2:
        return np.linalg.norm(vector, axis=1)
    return float(np.linalg.norm(vector))


def uvector(v: npt.ArrayLike) -> npt.NDArray:
    """Return the unit vector of `v`.

    Args:
        v (np.arraylike): Arraylike

    Returns:
        np.ndarray: Unit vector

    Examples:
        >>> uvector(np.array([1, 0, 0]))
        array([1., 0., 0.])
        >>> uvector(np.array([1, 1, 0]))
        array([0.70710678, 0.70710678, 0.        ])
        >>> uvector([1, 0, 0])
        array([1., 0., 0.])
        >>> uvector([1, 1, 0])
        array([0.70710678, 0.70710678, 0.        ])

    """
    if not isinstance(v, np.ndarray):
        v = np.array(v)
    return v / mag(v)


def angle(v1: npt.NDArray, v2: npt.NDArray, *, norm: bool = True) -> float:
    """Return unsigned angle between two vectors in radians

    Args:
        v1: Vector
        v2: Another vector
        norm (bool): Flag to normalize the vectors

    Returns:
        float: The angle between the two vectors in radians

    Examples:
        >>> v1 = np.array([1, 0, 0])
        >>> v2 = np.array([0, 1, 0])
        >>> angle(v1, v2)
        1.5707963267948966
        >>> angle(np.array((1, 0, 0)), np.array((1, 0, 0)))
        0.0
        >>> angle(np.array((1, 0, 0)), np.array((-1, 0, 0)))
        3.141592653589793

    """
    v1_u = v1 / np.linalg.norm(v1)
    v2_u = v2 / np.linalg.norm(v2)
    # Clip, because the dot product can slip past 1 or -1 due to rounding and
    # we can't compute arccos(-1.00001).
    return float(np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0)))


def signed_angle(v1: npt.NDArray, v2: npt.NDArray, look: npt.NDArray) -> float:
    """Return signed angle between two vectors given a 'look' vector/param

    Args:
        v1: A `3x1` vector or a `kx3` stack of vectors.
        v2: A `3x1` vector or a `kx3` stack of vectors.
        look: A `3x1` vector specifying the normal of the viewing plane.

    Returns:
        object: For `3x1` inputs, a `float` with the angle. For `kx1` inputs,
            a `kx1` array.

    """
    # The sign of (A x B) dot look gives the sign of the angle.
    # > 0 means clockwise, < 0 is counterclockwise.
    sign: npt.NDArray = np.array(np.sign(np.cross(v1, v2).dot(look)))

    # 0 means collinear: 0 or 180. Let's call that clockwise.
    sign[sign == 0] = 1

    return float(sign * angle(v1, v2))


def mktransform(arr: npt.NDArray) -> npt.NDArray:
    """Return a transform matrix from a 2D array

    Examples:
        >>> a = np.arange(9).reshape(3, 3)
        >>> a
        array([[0, 1, 2],
               [3, 4, 5],
               [6, 7, 8]])
        >>> mktransform(a)
        array([[0., 1., 2., 0.],
               [3., 4., 5., 0.],
               [6., 7., 8., 0.],
               [0., 0., 0., 1.]])
        >>> a = np.arange(4).reshape(2, 2)
        >>> a
        array([[0, 1],
               [2, 3]])
        >>> mktransform(a)
        array([[0., 1., 0.],
               [2., 3., 0.],
               [0., 0., 1.]])

    """
    if len(arr.shape) != 2:
        raise ValueError(f"Array (shape {arr.shape!s}) is not 2D")

    shape = arr.shape
    i, j = shape
    if i != j:
        raise ValueError(f"Array (shape {arr.shape!s}) is not square")

    tmat_side_len = i + 1
    tmat = np.zeros(tmat_side_len**2).reshape(tmat_side_len, tmat_side_len)
    tmat[i, j] = 1
    tmat[:i, :j] = arr
    return tmat


def invmat(matrix: npt.NDArray) -> npt.NDArray:
    """Return inverse of square transformation matrix.

    Examples:
        >>> import numpy as np
        >>> M0 = np.array([
        ...     [-0.5205994152612939, 0.24651214957419254, 0.8174399115176048, 0.0],
        ...     [0.36198387459603754, -0.8033808170109316, 0.472807505641871, 0.0],
        ...     [0.7732683385229469, 0.5420433773888937, 0.3290061605301676, 0.0],
        ...     [0.0, 0.0, 0.0, 1.0],
        ... ])
        >>> M1 = invmat(M0.T)
        >>> np.allclose(M1, np.linalg.inv(M0.T))
        True

    """
    return np.linalg.inv(matrix)


def cat_transform_matrices(*matrices: npt.NDArray) -> npt.NDArray:
    """Return concatenation of series of transformation matrices.

    Examples:
        >>> import numpy as np
        >>> M = np.random.rand(16).reshape((4, 4)) - 0.5
        >>> np.allclose(M, cat_transform_matrices(M))
        True
        >>> np.allclose(np.dot(M, M.T), cat_transform_matrices(M, M.T))
        True

    """
    M = np.identity(4)
    for i in matrices:
        M = np.dot(M, i)
    return M


def transform_equiv(mat_a: npt.NDArray, mat_b: npt.NDArray) -> bool:
    """Return True if two matrices repr the same/equiv transformations

    Examples:
        >>> import numpy as np
        >>> transform_equiv(np.identity(4), np.identity(4))
        True
        >>> transform_mat = np.array([
        ...     [-0.5205994152612939, 0.24651214957419254, 0.8174399115176048, 0.0],
        ...     [0.36198387459603754, -0.8033808170109316, 0.472807505641871, 0.0],
        ...     [0.7732683385229469, 0.5420433773888937, 0.3290061605301676, 0.0],
        ...     [0.0, 0.0, 0.0, 1.0],
        ... ])
        >>> transform_equiv(np.identity(4), transform_mat)
        False

    """
    mat_a = np.array(mat_a, dtype=np.float64, copy=True)
    mat_a /= mat_a[3, 3]
    mat_b = np.array(mat_b, dtype=np.float64, copy=True)
    mat_b /= mat_b[3, 3]
    return bool(np.allclose(mat_a, mat_b))


def quaternion_equiv(qa: npt.NDArray, qb: npt.NDArray) -> bool:
    """Return True if two quaternions are equiv"""
    qa = np.array(qa)
    qb = np.array(qb)
    return bool(np.allclose(qa, qb) or np.allclose(qa, -qb))


# =============================================================================
# PANDAS
# =============================================================================
def full_outer_join(left: pd.DataFrame, right: pd.DataFrame) -> pd.DataFrame:
    """Full outer join on two dataframe objects"""
    return left.merge(right, indicator=True, how="outer")


def rm_ditto(series: pd.Series) -> pd.Series:
    """Remove ditto-ed fields with pandas forward-fill method"""
    return series.fillna(method="ffill")


def is_multiindex(df: pd.DataFrame) -> bool:
    """Return True if dataframe is pandas.MultiIndex; False otherwise"""
    return isinstance(df.index, pd.MultiIndex)


def quick_maths() -> int:
    """Perform quick maths

    Maths citation: https://www.youtube.com/watch?v=3M_5oYU-IsU

    """
    four = 2 + 2  # two plus two is 4
    three = four - 1  # Minus 1 is three
    log.debug("Two plus two is four, minus 1 is 3; Quick maths!")
    return three


# =============================================================================
# XARRAY
# =============================================================================

if __name__ == "__main__":
    import doctest

    doctest.testmod()
