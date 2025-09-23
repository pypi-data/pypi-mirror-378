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
"""dgpy + numpy = dgnumpy"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, Literal, TypeAlias, TypeGuard, TypeVar

import numpy as np
import numpy.typing as npt

from typing_extensions import TypedDict

__all__ = ("__numpy_version__",)
N = TypeVar("N", bound=float | int)
Number: TypeAlias = float | int

__numpy_version__ = np.__version__
DTypesTuple = tuple[
    type[np.bool_],
    type[np.int8],
    type[np.uint8],
    type[np.short],
    type[np.ushort],
    type[np.intc],
    type[np.uintc],
    type[np.int_],
    type[np.uint],
    type[np.longlong],
    type[np.ulonglong],
    type[np.half],
    type[np.half],
    type[np.single],
    type[np.float64],
    type[np.longdouble],
    type[np.complex64],
    type[np.complex128],
    type[np.clongdouble],
]
dtypes: DTypesTuple = (
    np.bool_,
    np.int8,
    np.uint8,
    np.short,
    np.ushort,
    np.intc,
    np.uintc,
    np.int_,
    np.uint,
    np.longlong,
    np.ulonglong,
    np.half,
    np.half,
    np.single,
    np.float64,
    np.longdouble,
    np.complex64,
    np.complex128,
    np.clongdouble,
)


def as_dtype(array: npt.NDArray[Any], dtype: npt.DTypeLike) -> npt.NDArray[Any]:
    return array.astype(dtype)


def is_dtype(array: npt.NDArray[Any], dtype: npt.DTypeLike) -> bool:
    return array.dtype == np.dtype(dtype)


def assert_dtype(array: npt.NDArray[Any], dtype: npt.DTypeLike) -> None:
    if not is_dtype(array, dtype):
        raise ValueError(f"Array dtype must be {dtype}, got {array.dtype}")


def is_array_shape(array: npt.NDArray[Any], shape: tuple[int, ...]) -> bool:
    return array.shape == shape


def assert_shape(array: npt.NDArray[Any], shape: tuple[int, ...]) -> None:
    if not is_array_shape(array, shape):
        raise ValueError(f"Array shape must be {shape}, got {array.shape}")


def nan_array_type(array: npt.NDArray[Any]) -> TypeGuard[npt.NDArray[np.floating]]:
    """Returns True if the array could contain NaNs"""
    return array.dtype.kind in "fc"


def array_dtype_supports_nan(
    array: npt.NDArray[Any],
) -> TypeGuard[npt.NDArray[np.floating]]:
    """Returns True if the array could contain NaNs"""
    return array.dtype.kind in "fc"


def is_2x2(array: npt.NDArray[Any]) -> bool:
    return is_array_shape(array, (2, 2))


def assert_2x2(array: npt.NDArray[Any]) -> None:
    assert_shape(array, (2, 2))


def is_3x3(array: npt.NDArray[Any]) -> bool:
    return is_array_shape(array, (3, 3))


def assert_3x3(array: npt.NDArray[Any]) -> None:
    assert_shape(array, (3, 3))


def is_4x4(array: npt.NDArray[Any]) -> bool:
    return is_array_shape(array, (4, 4))


def is_array_shape_dtype(
    array: npt.NDArray[Any], shape: tuple[int, ...], dtype: npt.DTypeLike
) -> bool:
    return is_array_shape(array, shape) and is_dtype(array, dtype)


def assert_shape_dtype(
    array: npt.NDArray[Any], shape: tuple[int, ...], dtype: npt.DTypeLike
) -> None:
    assert_shape(array, shape)
    assert_dtype(array, dtype)


def is_array_bool_(array: npt.NDArray[Any]) -> TypeGuard[npt.NDArray[np.bool_]]:
    return array.dtype == np.bool_


def is_array_byte(array: npt.NDArray[Any]) -> TypeGuard[npt.NDArray[np.byte]]:
    return array.dtype == np.byte


def is_array_ubyte(array: npt.NDArray[Any]) -> TypeGuard[npt.NDArray[np.ubyte]]:
    return array.dtype == np.ubyte


def is_array_short(array: npt.NDArray[Any]) -> TypeGuard[npt.NDArray[np.short]]:
    return array.dtype == np.short


def is_array_ushort(array: npt.NDArray[Any]) -> TypeGuard[npt.NDArray[np.ushort]]:
    return array.dtype == np.ushort


def is_array_intc(array: npt.NDArray[Any]) -> TypeGuard[npt.NDArray[np.intc]]:
    return array.dtype == np.intc


def is_array_uintc(array: npt.NDArray[Any]) -> TypeGuard[npt.NDArray[np.uintc]]:
    return array.dtype == np.uintc


def is_array_int_(array: npt.NDArray[Any]) -> TypeGuard[npt.NDArray[np.int_]]:
    return array.dtype == np.int_


def is_array_uint(array: npt.NDArray[Any]) -> TypeGuard[npt.NDArray[np.uint]]:
    return array.dtype == np.uint


def is_array_longlong(array: npt.NDArray[Any]) -> TypeGuard[npt.NDArray[np.longlong]]:
    return array.dtype == np.longlong


def is_array_ulonglong(array: npt.NDArray[Any]) -> TypeGuard[npt.NDArray[np.ulonglong]]:
    return array.dtype == np.ulonglong


def is_array_float16(array: npt.NDArray[Any]) -> TypeGuard[npt.NDArray[np.float16]]:
    return array.dtype == np.float16


def is_array_half(array: npt.NDArray[Any]) -> TypeGuard[npt.NDArray[np.half]]:
    return array.dtype == np.half


def is_array_single(array: npt.NDArray[Any]) -> TypeGuard[npt.NDArray[np.single]]:
    return array.dtype == np.single


def is_array_double(array: npt.NDArray[Any]) -> TypeGuard[npt.NDArray[np.double]]:
    return array.dtype == np.double


def is_array_longdouble(
    array: npt.NDArray[Any],
) -> TypeGuard[npt.NDArray[np.longdouble]]:
    return array.dtype == np.longdouble


def is_array_csingle(array: npt.NDArray[Any]) -> TypeGuard[npt.NDArray[np.csingle]]:
    return array.dtype == np.csingle


def is_array_cdouble(array: npt.NDArray[Any]) -> TypeGuard[npt.NDArray[np.cdouble]]:
    return array.dtype == np.cdouble


def is_array_clongdouble(
    array: npt.NDArray[Any],
) -> TypeGuard[npt.NDArray[np.clongdouble]]:
    return is_dtype(array, np.clongdouble)


def n_nan(array: npt.NDArray[Any]) -> int:
    """Count the number of NaNs in an array"""
    if not array_dtype_supports_nan(array):
        return 0
    return int(np.count_nonzero(np.isnan(array)))


def n_neginf(array: npt.NDArray[Any]) -> int:
    """Count the number of negative infs in an array"""
    if not array_dtype_supports_nan(array):
        return 0
    return np.isneginf(array).sum()


def n_inf(array: npt.NDArray[Any]) -> int:
    """Count the number of infs in an array"""
    if not array_dtype_supports_nan(array):
        return 0
    return np.isinf(array).sum()


def neginf2nan(array: npt.NDArray[Any]) -> npt.NDArray[Any]:
    """Convert infs to NaNs"""
    if not array_dtype_supports_nan(array):
        return array
    return np.where(np.isneginf(array), np.nan, array)


def posinf2nan(array: npt.NDArray[Any]) -> npt.NDArray[Any]:
    """Convert infs to NaNs"""
    if not array_dtype_supports_nan(array):
        return array
    return np.where(np.isposinf(array), np.nan, array)


def inf2nan(array: npt.NDArray[Any]) -> npt.NDArray[Any]:
    """Convert infs to NaNs"""
    if not array_dtype_supports_nan(array):
        return array
    return posinf2nan(array)


def count(array: npt.NDArray[Any]) -> int:
    if not array_dtype_supports_nan(array):
        return array.size
    return int(np.count_nonzero(~np.isnan(array)))


# ==============================================================================
# DEV ~ UNDER CONSTRUCTION ~ DEV ~ UNDER CONSTRUCTION ~ DEV ~ UNDER CONSTRUCTION
# ==============================================================================
class ArrayStatsDict(TypedDict):
    stype: Literal["arr", "nan", "inf"]
    max: Number
    mean: float
    median: Number
    min: Number
    std: float
    sum: Number
    var: float


class ArrayInfoDict(TypedDict):
    dtype: str
    shape: tuple
    ndim: int
    n_inf: int
    n_nan: int
    arrmax: Number
    arrmean: float
    arrmedian: Number
    arrmin: Number
    arrstd: float
    arrsum: float
    arrvar: float

    inf_stats: ArrayStatsDict | None
    nan_stats: ArrayStatsDict | None


@dataclass
class ArrayStatistics(Generic[N]):
    """Statistics for an array

    stype is the type of statistics:
        'arr' = array statistics
        'nan' = nan statistics; where nan is not included in the calculation
        'inf' = inf statistics; where inf AND nan are not included in the calculation

    """

    __slots__ = ("max", "mean", "median", "min", "std", "stype", "sum", "var")
    stype: Literal["arr", "nan", "inf"]
    max: N
    mean: float
    median: N
    min: N
    std: float
    sum: N
    var: float

    def asdict(self) -> ArrayStatsDict:
        return {
            "stype": self.stype,
            "max": self.max,
            "mean": self.mean,
            "median": self.median,
            "min": self.min,
            "std": self.std,
            "sum": self.sum,
            "var": self.var,
        }


@dataclass
class ArrayInfo(Generic[N]):
    dtype: str
    shape: tuple[int, ...]
    ndim: int
    n_inf: int
    n_nan: int
    count: int

    # statistics
    arrmax: N
    arrmean: float
    arrmedian: N
    arrmin: N
    arrstd: float
    arrsum: N
    arrvar: float

    inf_stats: ArrayStatistics[N] | None
    nan_stats: ArrayStatistics[N] | None

    __slots__ = (
        "arrmax",
        "arrmean",
        "arrmedian",
        "arrmin",
        "arrstd",
        "arrsum",
        "arrvar",
        "count",
        "dtype",
        "inf_stats",
        "n_inf",
        "n_nan",
        "nan_stats",
        "ndim",
        "shape",
    )

    def asdict(self) -> ArrayInfoDict:
        return {
            "dtype": self.dtype,
            "shape": self.shape,
            "ndim": self.ndim,
            "n_inf": self.n_inf,
            "n_nan": self.n_nan,
            "arrmax": self.arrmax,
            "arrmean": self.arrmean,
            "arrmedian": self.arrmedian,
            "arrmin": self.arrmin,
            "arrstd": self.arrstd,
            "arrsum": self.arrsum,
            "arrvar": self.arrvar,
            "inf_stats": self.inf_stats.asdict() if self.inf_stats else None,
            "nan_stats": self.nan_stats.asdict() if self.nan_stats else None,
        }

    def __json_interface__(self) -> ArrayInfoDict:
        return self.asdict()

    def _stats(self, arr: npt.NDArray) -> ArrayStatistics:
        return ArrayStatistics(
            stype="arr",
            max=arr.max(),
            mean=arr.mean(),
            median=float(np.median(arr)),
            min=arr.min(),
            std=arr.std(),
            sum=arr.sum(),
            var=arr.var(),
        )

    @property
    def nanmean(self) -> float:
        if self.nan_stats:
            return self.nan_stats.mean
        return self.arrmean

    @property
    def nanmedian(self) -> N:
        if self.nan_stats:
            return self.nan_stats.median
        return self.arrmedian

    @property
    def nanmax(self) -> N:
        if self.nan_stats:
            return self.nan_stats.max
        return self.arrmax

    @property
    def nanmin(self) -> N:
        if self.nan_stats:
            return self.nan_stats.min
        return self.arrmin

    @property
    def nanstd(self) -> float:
        if self.nan_stats:
            return self.nan_stats.std
        return self.nanstd

    @property
    def nansum(self) -> N:
        if self.nan_stats:
            return self.nan_stats.sum
        return self.arrsum

    @property
    def nanvar(self) -> float:
        if self.nan_stats:
            return self.nan_stats.var
        return self.arrvar


def is_boolean_dtype(arr: npt.NDArray) -> bool:
    return arr.dtype == np.bool_


def is_integer_dtype(arr: npt.NDArray) -> bool:
    return arr.dtype == np.int_


def is_float_dtype(arr: npt.NDArray) -> bool:
    return arr.dtype == np.float64


def where_not_inf(arr: npt.NDArray) -> npt.NDArray:
    return np.where(np.isfinite(arr), arr, np.nan)


def arr_stats(arr: npt.NDArray) -> ArrayStatistics:
    if is_float_dtype(arr):
        return ArrayStatistics(
            stype="arr",
            max=float(np.amax(arr)),
            mean=float(np.mean(arr)),
            median=float(np.median(arr)),
            min=float(np.amin(arr)),
            std=float(np.std(arr)),
            sum=float(np.sum(arr)),
            var=float(np.var(arr)),
        )
    return ArrayStatistics(
        stype="arr",
        max=int(np.amax(arr)),
        mean=float(np.mean(arr)),
        median=int(np.median(arr)),
        min=int(np.amin(arr)),
        std=float(np.std(arr)),
        sum=int(np.sum(arr)),
        var=float(np.var(arr)),
    )


def nan_stats(arr_nan: npt.NDArray) -> ArrayStatistics:
    return ArrayStatistics(
        stype="nan",
        max=float(np.nanmax(arr_nan)),
        mean=float(np.nanmean(arr_nan)),
        median=float(np.nanmedian(arr_nan)),
        min=float(np.nanmin(arr_nan)),
        std=float(np.nanstd(arr_nan)),
        sum=float(np.nansum(arr_nan)),
        var=float(np.nanvar(arr_nan)),
    )


def inf_stats(arr_inf: npt.NDArray) -> ArrayStatistics:
    arr_nan = np.where(np.isinf(arr_inf), arr_inf, np.nan)
    return ArrayStatistics(
        stype="inf",
        max=float(np.nanmax(arr_nan)),
        mean=float(np.nanmean(arr_nan)),
        median=float(np.nanmedian(arr_nan)),
        min=float(np.nanmin(arr_nan)),
        std=float(np.nanstd(arr_nan)),
        sum=float(np.nansum(arr_nan)),
        var=float(np.nanvar(arr_nan)),
    )


def nonfloat_array_describe(arr: npt.NDArray) -> ArrayInfo[int]:
    n_nan = int(np.isnan(arr).sum())
    n_inf = int(np.isinf(arr).sum())
    _count = int(arr.size)
    dtype_str = str(arr.dtype.name)
    shape = arr.shape
    ndim = arr.ndim
    _arr_stats = arr_stats(arr)
    _nan_stats = _arr_stats
    _inf_stats = _arr_stats
    return ArrayInfo(
        dtype=dtype_str,
        shape=shape,
        ndim=ndim,
        count=_count,
        n_inf=n_inf,
        n_nan=n_nan,
        arrmax=_arr_stats.max,
        arrmin=_arr_stats.min,
        arrmean=_arr_stats.mean,
        arrmedian=_arr_stats.median,
        arrstd=_arr_stats.std,
        arrvar=_arr_stats.var,
        arrsum=_arr_stats.sum,
        nan_stats=_arr_stats,
        inf_stats=_arr_stats,
    )


def float_array_describe(arr: npt.NDArray) -> ArrayInfo[float]:
    dtype_str = str(arr.dtype.name)
    shape = arr.shape
    ndim = arr.ndim
    num_nans = int(np.isnan(arr).sum())
    num_infs = int(np.isinf(arr).sum())
    arr_count = int(arr.size) - num_nans
    _arr_stats = arr_stats(arr)
    _nan_stats = nan_stats(arr) if num_nans > 0 else _arr_stats
    _inf_stats = inf_stats(arr) if num_infs > 0 else _nan_stats
    return ArrayInfo(
        dtype=dtype_str,
        shape=shape,
        ndim=ndim,
        n_inf=num_infs,
        n_nan=num_nans,
        count=arr_count,
        arrmax=_arr_stats.max,
        arrmin=_arr_stats.min,
        arrmean=_arr_stats.mean,
        arrmedian=_arr_stats.median,
        arrstd=_arr_stats.std,
        arrvar=_arr_stats.var,
        arrsum=_arr_stats.sum,
        inf_stats=_inf_stats,
        nan_stats=_nan_stats,
    )


# TODO: add support for percentiles like pandas does...
#  would look like: `percentiles: Optional[Sequence[float]] = (25, 50, 75)`
def array_describe(arr: npt.NDArray) -> ArrayInfo:
    """Describe an array with info and statistics

    Example:
        >>> import json
        >>> arr_i64 = np.array([1, 2, 3, 4, 5], dtype=np.int64)
        >>> info_i64 = array_describe(arr_i64)
        >>> print(json.dumps(info_i64.asdict(), indent=2, sort_keys=True))
        {
          "arrmax": 5,
          "arrmean": 3.0,
          "arrmedian": 3,
          "arrmin": 1,
          "arrstd": 1.4142135623730951,
          "arrsum": 15,
          "arrvar": 2.0,
          "dtype": "int64",
          "inf_stats": {
            "max": 5,
            "mean": 3.0,
            "median": 3,
            "min": 1,
            "std": 1.4142135623730951,
            "stype": "arr",
            "sum": 15,
            "var": 2.0
          },
          "n_inf": 0,
          "n_nan": 0,
          "nan_stats": {
            "max": 5,
            "mean": 3.0,
            "median": 3,
            "min": 1,
            "std": 1.4142135623730951,
            "stype": "arr",
            "sum": 15,
            "var": 2.0
          },
          "ndim": 1,
          "shape": [
            5
          ]
        }
        >>> arr_f64 = np.array([1.0, 2.0, 3.0, 4.0, 5.0], dtype=np.float64)
        >>> info_f64 = array_describe(arr_f64)
        >>> print(json.dumps(info_f64.asdict(), indent=2, sort_keys=True))
        {
          "arrmax": 5.0,
          "arrmean": 3.0,
          "arrmedian": 3.0,
          "arrmin": 1.0,
          "arrstd": 1.4142135623730951,
          "arrsum": 15.0,
          "arrvar": 2.0,
          "dtype": "float64",
          "inf_stats": {
            "max": 5.0,
            "mean": 3.0,
            "median": 3.0,
            "min": 1.0,
            "std": 1.4142135623730951,
            "stype": "arr",
            "sum": 15.0,
            "var": 2.0
          },
          "n_inf": 0,
          "n_nan": 0,
          "nan_stats": {
            "max": 5.0,
            "mean": 3.0,
            "median": 3.0,
            "min": 1.0,
            "std": 1.4142135623730951,
            "stype": "arr",
            "sum": 15.0,
            "var": 2.0
          },
          "ndim": 1,
          "shape": [
            5
          ]
        }

    """
    if arr.dtype.kind == "f":
        return float_array_describe(arr)
    return nonfloat_array_describe(arr)


def arrdesc(arr: npt.NDArray) -> ArrayInfo:
    """Return stats/info for a numpy array (alias for `array_describe`)"""
    return array_describe(arr)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
