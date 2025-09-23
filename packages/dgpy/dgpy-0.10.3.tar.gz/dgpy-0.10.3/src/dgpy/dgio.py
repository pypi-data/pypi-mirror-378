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
"""Dynamic Graphics IO utils"""

from __future__ import annotations

from os import path
from typing import TYPE_CHECKING, Any

import xarray as xr

from shellfish import fs
from typing_extensions import deprecated

from dgpy.core.py2grd import Py2grd, Py2grdHeader
from dgpy.core.py3grd import Py3grd, Py3grdHeader
from dgpy.pydat import Pydat, PydatHeader

if TYPE_CHECKING:
    import pandas as pd

    from dgpy._types import FsPath
    from dgpy.npt import NDArray

__all__ = (
    "l2grd",
    "l3grd",
    "lbdat",
    "lfile",
    "lpy2grd",
    "lpy3grd",
    "lpydat",
    "ndarray_to_py2grd",
    "ndarray_to_py3grd",
    "py2grd_to_pydat",
    "py3grd_to_pydat",
    "pydat_to_py2grd",
    "pydat_to_py3grd",
    "read_2grd",
    "read_3grd",
    "read_bdat",
    "read_file",
    "read_pydat",
)


def read_3grd(filepath: FsPath) -> Py3grd:
    """Load and return a Py3grd from a 3grd-fspath"""
    return Py3grd.from_fspath(str(filepath))


def read_2grd(filepath: FsPath) -> Py2grd:
    """Load and return a Py2grd from a 2grd-fspath"""
    return Py2grd.from_fspath(str(filepath))


def read_bdat(filepath: FsPath) -> Pydat:
    """Load and return a Pydat from a bdat-fspath"""
    return Pydat.from_bdat(filepath)


def read_pydat(filepath: FsPath) -> Pydat:
    """Load and return a Pydat from a fspath"""
    if str(filepath).endswith(".bdat"):
        return read_bdat(filepath)
    return Pydat.from_scattered_data(str(filepath))


def read_file(filepath: FsPath) -> Py2grd | Py3grd | Pydat | Any:
    """Read `dgpy` supported file

    Args:
        filepath: Filepath to read

    Returns:
        one of: Py3grd, Py2grd, Pydat, dictionary (json)

    """
    _, extension = path.splitext(str(filepath))
    filepath_str = str(filepath)
    if filepath_str.endswith(".3grd"):
        return read_3grd(filepath)
    if filepath_str.endswith(".2grd"):
        return read_2grd(filepath)
    if filepath_str.endswith(".json"):
        return fs.read_json(filepath)
    if filepath_str.endswith((".dat", ".pdat", ".bdat", ".prod", ".path", ".ann")):
        return read_pydat(filepath)
    raise ValueError(f"Unrecognized extension: {extension} -- fspath={filepath}")


# --------------------------------------------------------------------------------
# DEPRECATED READ FUNCTIONS
# --------------------------------------------------------------------------------
@deprecated(
    "l3grd is deprecated, use read_3grd instead",
)
def l3grd(filepath: FsPath) -> Py3grd:
    """Load and return a Py3grd from a 3grd-fspath"""
    return read_3grd(filepath)


@deprecated(
    "l2grd is deprecated, use read_2grd instead",
)
def l2grd(filepath: FsPath) -> Py2grd:
    """Load and return a Py2grd from a 2grd-fspath"""
    return read_2grd(filepath)


@deprecated(
    "lbdat is deprecated, use read_bdat instead",
)
def lpy3grd(filepath: FsPath) -> Py3grd:
    """Load and return a Py3grd from a 3grd-fspath"""
    return read_3grd(filepath)


@deprecated(
    "lpy2grd is deprecated, use read_2grd instead",
)
def lpy2grd(filepath: FsPath) -> Py2grd:
    """Load and return a Py2grd from a 2grd-fspath"""
    return read_2grd(filepath)


@deprecated(
    "lbdat is deprecated, use read_bdat instead",
)
def lbdat(filepath: FsPath) -> Pydat:
    """Load and return a Pydat from a bdat-fspath"""
    return read_bdat(filepath)


@deprecated("lpydat is deprecated, use read_pydat instead")
def lpydat(filepath: FsPath) -> Pydat:
    """Load and return a Pydat from a fspath"""
    return read_pydat(filepath)


@deprecated(
    "lfile is deprecated, use read_2grd, read_3grd, read_bdat, or read_pydat instead",
)
def lfile(filepath: FsPath) -> Py2grd | Py3grd | Pydat | Any:
    """Load a file

    Args:
        filepath: Filepath to load

    Returns:
        One of the following: Py3grd, Py2grd, Pydat, dictionary, string

    """
    return read_file(filepath)


# =============================================================================
# CONVERT ~ CONVERT ~ CONVERT ~ CONVERT ~ CONVERT ~ CONVERT ~ CONVERT ~ CONVERT
# =============================================================================
def py2grd_to_pydat(
    py2grd: Py2grd, *, multiindex: bool = False, z_field: str | None = None
) -> Pydat:
    """Return a Pydat object given a Py2grd object"""
    _name = z_field or py2grd.head.z_field
    py2grd.add_spatial_coordinates()
    _head = py2grd.head
    _df = py2grd.dataarray.to_dataframe(name=_name)
    if not multiindex:
        try:
            _df.reset_index(["xcolumns", "yrows", "zlevels"], inplace=True)
        except KeyError:
            _df.reset_index(["xcolumns", "yrows"], inplace=True)
    pydat_header = PydatHeader.model_validate(_head.model_dump())
    return Pydat(dataframe=_df, head=pydat_header)


def py3grd_to_pydat(
    py3grd: Py3grd, *, multiindex: bool = False, p_field: str | None = None
) -> Pydat:
    """Return a Pydat object given a Py3grd object"""
    _name = p_field or py3grd.head.p_field
    py3grd.add_spatial_coordinates()
    _head = py3grd.head
    _df = py3grd.dataarray.to_dataframe(name=_name)
    if not multiindex:
        try:
            _df.reset_index(["xcolumns", "yrows", "zlevels"], inplace=True)
        except KeyError:
            _df.reset_index(["xcolumns", "yrows"], inplace=True)
    pydat_header = PydatHeader.model_validate(_head.model_dump())
    return Pydat(dataframe=_df, head=pydat_header)


def ndarray_to_py2grd(
    arr: NDArray,
    *,
    meta: dict[Any, Any] | None = None,
    coords: tuple[str, str] = ("yrows", "xcolumns"),
) -> Py2grd:
    """Create and return a Py2grd object from a numpy ndarray

    Args:
        arr: 2D numpy array
        meta: Dictionary of metadata
        coords (tuple[str, str]): Coordinate names to use in xr.DataArray

    Returns:
        Py2grd object

    """
    return Py2grd.from_ndarray(arr=arr, meta=meta, coords=coords)


def ndarray_to_py3grd(
    arr: NDArray,
    *,
    meta: dict[Any, Any] | None = None,
    coords: tuple[str, str, str] = ("zlevels", "yrows", "xcolumns"),
) -> Py3grd:
    """Create and return a Py3grd object from a numpy ndarray

    Args:
        arr: 3D numpy array
        meta: Dictionary of metadata
        coords (tuple[str, str, str]): Coordinate names to use in xr.DataArray

    Returns:
        Py3grd object

    """
    return Py3grd.from_ndarray(arr=arr, coords=coords, meta=meta)


def pydat_to_py2grd(pydat: Pydat) -> Py2grd:
    """Convert pydat object to a Py2grd object

    Args:
        pydat (Pydat): Pydat object

    Returns:
        Py2grd object

    """
    # header is identical to pydat except for dfields
    df = pydat.dataframe
    py2grd_header = Py2grdHeader.model_validate(
        pydat.head.model_dump(exclude={"dfields"})
    )
    _xcol = py2grd_header.xcol
    _yrow = py2grd_header.yrow
    data = df.loc[:, "p"].values.reshape(_yrow, _xcol)
    da = xr.DataArray(
        data=data,
        coords={
            "yrows": range(py2grd_header.yrow),
            "xcolumns": range(py2grd_header.xcol),
        },
        dims=["yrows", "xcolumns"],
    )
    return Py2grd(head=py2grd_header, dataarray=da)


def pydat_to_py3grd(pydat: Pydat) -> Py3grd:
    """Convert pydat object to a Py3grd object

    Args:
        pydat (Pydat): Pydat object

    Returns:
        Py3grd object

    """
    # header is identical to pydat except for dfields and filepath
    df = pydat.dataframe
    header: dict[str, Any] = (
        pydat.head.model_dump()
        if hasattr(pydat.head, "model_dump")
        else dict(pydat.head)
    )
    header.pop("dfields", None)
    header.pop("filepath", None)
    data = (
        df.loc[:, "p"]
        .to_numpy()
        .reshape(header["zlev"], header["yrow"], header["xcol"])
    )
    da = xr.DataArray(
        data=data,
        coords={
            "zlevels": range(header["zlev"]),
            "yrows": range(header["yrow"]),
            "xcolumns": range(header["xcol"]),
        },
        dims=["zlevels", "yrows", "xcolumns"],
    )
    py3grd_header = Py3grdHeader.from_dict(header)
    return Py3grd(head=py3grd_header, dataarray=da)


# ----------------------------------------------------------------------------
# NOT IMPLEMENTED (YET)
# ----------------------------------------------------------------------------


def dataarray_to_py2grd(da: xr.DataArray) -> Py2grd:
    """Create and return a Py2grd object from a 2D-xr.DataArray

    Args:
        da (xr.DataArray): 2D xarray DataArray object

    Returns:
        Py2grd object

    """
    raise NotImplementedError()


def dataarray_to_py3grd(da: xr.DataArray) -> Py3grd:
    """Create and return a Py3grd object from a 3D-xr.DataArray

    Args:
        da (xr.DataArray): 3D xarray DataArray object

    Returns:
        Py3grd object

    """
    raise NotImplementedError()


def dataframe_to_pydat(df: pd.DataFrame) -> Pydat:
    """Create and return a Pydat object from a pandas DataFrame

    Args:
        df (pd.DataFrame): pandas DataFrame object

    Returns:
        Pydat object

    """
    raise NotImplementedError()
