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
"""Py3grd object"""

from __future__ import annotations

from io import BytesIO
from os import path
from pprint import pformat
from struct import pack
from typing import (
    TYPE_CHECKING,
    Any,
    BinaryIO,
    ClassVar,
    Literal,
    TypeVar,
)

import numpy as np
import xarray as xr

from pydantic import Field, field_validator
from shellfish import sh

from dgpy.core.boundingbox import BoundingBox
from dgpy.core.enums import evu_validate
from dgpy.core.py6grd.evg import Evg
from dgpy.core.py6grd.py6grd_base import Py6grdBase, Py6grdHeaderBase
from dgpy.core.py6grd.py6grd_io import PygrdWriterBase, load_3grd_buffer, load_grd
from dgpy.core.pyspace import PySpace
from dgpy.maths import rotation_matrix_3d

if TYPE_CHECKING:
    from collections.abc import Iterable

    from dgpy import npt
    from dgpy._types import FsPath
    from dgpy.core.py6grd.py6grd_dto import PygrdHeaderDTO
    from dgpy.pydat import Pydat
    from dgpy.xtypes import Arr

TPy3grdHeader = TypeVar("TPy3grdHeader", bound="Py3grdHeader")


class Py3grdHeader(Py6grdHeaderBase):
    """Header object for the Py3grd; inherits from the Py6grdHeaderBase

    ```
    from dgpy import Py3grdHeader
    ```
    """

    xcol: int
    yrow: int
    zlev: int = Field(
        default=1,
        title="zlev",
        description="number of z-levels",
    )
    z_influence: float = 1.0
    nulls_in_grid: int
    geometry: int = Field(
        default=0,
        title="geometry",
        description="Grid geometry; used by bordered (py)2grids",
    )
    clamp: tuple[float, float] = (1.0000000200408773e20, 1.0000000200408773e20)
    fspath: str | None = None

    # ATTRS WITH DEFAULT VALUE(S)
    node_range: tuple[float, float] = (0.0, 0.0)
    pclip: tuple[float, float] = (0.0, 0.0)
    trend_coefficients: tuple[int, ...] | None = None
    trend_offsets: tuple[int, ...] | None = None
    seismic_line_and_trace_labels: tuple[int, ...] | None = None
    dat: str = ""
    is_bordered: bool = False
    p_field: str = "p"
    bit_factor: float = 1.0
    bit_shift: float = 0.0
    bpoly: str | None = None
    clip_poly: str | None = None
    trend_order: Any = None
    data_order: Any = None

    # =============
    # 3grd specific
    # =============
    is_2d: Literal[False] = Field(
        default=False,
        title="is_2d",
        description="False for Py3grd; True for Py2grd",
    )
    type: str = "3grd"
    punits: str = "unknown"
    punits_string: str = "unknown"
    alias: str = ""

    date: str | None = None
    dateformat: str | None = None
    line_coloring: str | None = None
    format: str | None = None
    scale_factor_at_central_meridian: float | None = None
    central_meridian: str | None = None
    latitude_of_origin: str | None = None
    false_easting: str | None = None
    false_northing: str | None = None
    std_parallel_1: str | None = None
    std_parallel_2: str | None = None
    use_default_ditto: bool = False
    z_datum_above_msl: str | None = None

    # =========================================================================
    # XFORM ATTRS/FIELDS - Py3grd only
    # =========================================================================
    xform_type: int | None = None
    xform_top: str | None = None
    xform_bottom: str | None = None
    xform_top_shift: float | None = None
    xform_bottom_shift: float | None = None
    xform_top_percent: int | None = None
    xform_bottom_percent: int | None = None
    xform_bottom_grid: tuple[float, ...] | None = None
    xform_x_spacing: tuple[float, ...] | None = None
    xform_z_spacing: tuple[float, ...] | None = None
    xform_divider: tuple[float, ...] | None = None

    # VALIDATE UNITS
    @field_validator("punits", mode="before")
    @classmethod
    def validate_units(cls, v: Any) -> str:
        return evu_validate(v)

    def dump_dict(
        self,
    ) -> dict[str, str | float | int | list[Any] | tuple[float, float] | None]:
        """Return dictionary of dump data"""
        self_dict = self.model_dump()
        _attrs_d = {
            k.strip(" "): v if not isinstance(v, bytes) else v.decode()
            for k, v in self_dict.items()
        }
        return {
            "alias": self.alias,
            "attributes": [],
            "desc": self.desc,
            "type": self.type,
            "node_range": self.node_range,
            "date": self.date,
            **_attrs_d,
            **self.space.dump_dict(),
        }

    # ==================
    # FROM/TO DICTIONARY
    # ==================
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Py3grdHeader:
        """Create and return a Py3grdHeader from a Dictionary

        Args:
            data (dict[str, Any]): Data dictionary

        Returns:
            Py3grdHeader object

        """
        try:
            _ = data.pop("ditto")  # pop ditto fields
        except KeyError:
            pass
        if "field" in data:
            data["p_field"] = data.pop("field")
        return cls(**data)

    @classmethod
    def _from_dto(cls, dto: PygrdHeaderDTO) -> Py3grdHeader:
        """Create and return Py3grdHeader from data transfer object (DTO)"""
        return Py3grdHeader.from_dict(data=dto.py3grd_data_dict())


class Py3grd(Py6grdBase):
    """3grid object class ~ dgpy

    dgpy.Py3grd objects contain:
        head: dgpy.Py3grdHeader
        dataarray: xarray.DataArray
        meta: dict[Any, Any]
    """

    head: Py3grdHeader
    dataarray: xr.DataArray
    meta: dict[str, Any] = Field(default_factory=dict)

    Bounds: ClassVar[type[BoundingBox]] = BoundingBox

    # =======
    # METHODS
    # =======
    @field_validator("dataarray")
    @classmethod
    def _validate_dataarray(cls, v: xr.DataArray) -> xr.DataArray:
        if len(v.shape) != 3:
            raise ValueError(
                f"DataArray must be 3-dimensional; given DataArray has shape: {v.shape}"
            )
        return v

    def deepcopy(self) -> Py3grd:
        """Return a deep copy of the `Py3grd` object"""
        _head_cp = self.head.model_copy(deep=True)
        _dataarray_cp = self.dataarray.copy(deep=True)
        return Py3grd(head=_head_cp, dataarray=_dataarray_cp, meta=self.meta)

    def copy(self, *, deep: bool = True) -> Py3grd:  # type: ignore[override]
        """Return a deep copy of the `Py3grd` object"""
        _head_cp = self.head.model_copy()
        _dataarray_cp = self.dataarray.copy(deep=deep)
        return Py3grd(head=_head_cp, dataarray=_dataarray_cp, meta=self.meta)

    def _get_xyz(self) -> tuple[xr.DataArray, xr.DataArray, xr.DataArray]:
        _x = np.linspace(0, self.head.space.xrange, self.head.xcol)
        _y = np.linspace(0, self.head.space.yrange, self.head.yrow)
        _z = np.linspace(0, self.head.space.zrange, self.head.zlev)
        _xyz_mesh = np.meshgrid(_y, _z, _x)
        _xyz: npt.NDArray = np.stack(_xyz_mesh)
        _rot_axis = [0, 1, 0]
        _shape = _xyz.shape
        rot_mat = rotation_matrix_3d(np.array(_rot_axis), self.head.space.angle_rad)
        _xyz = _xyz.reshape((3, -1)).transpose()
        zyx_coords = np.dot(_xyz, rot_mat)
        z = zyx_coords[:, 1] + self.head.space.zpivot
        z = z.T.reshape(_shape[1:])
        y = zyx_coords[:, 0] + self.head.space.ypivot
        y = y.T.reshape(_shape[1:])
        x = zyx_coords[:, 2] + self.head.space.xpivot
        x = x.T.reshape(_shape[1:])
        dim_order = ["zlevels", "yrows", "xcolumns"]
        return (
            xr.DataArray(x, dims=dim_order),
            xr.DataArray(y, dims=dim_order),
            xr.DataArray(z, dims=dim_order),
        )

    def add_spatial_coordinates(self) -> None:
        """Add spatial coordinates to grid"""
        _x, _y, _z = self._get_xyz()
        self.dataarray["x"] = _x
        self.dataarray["y"] = _y
        self.dataarray["z"] = _z

    @classmethod
    def from_fspath(cls, fspath: FsPath, *, name: str | None = None) -> Py3grd:
        """Return a PyGrd object given a path to a 2/3 grid file

        Args:
            name (str): dataarray name
            fspath (str): fspath to a 3grd

        Returns:
            Py3grd object

        """
        _grd_data = load_grd(fspath, skip_nodes=False)
        _grd_data.fspath = str(fspath)
        _values: Arr = _grd_data.values()
        _dims = _grd_data.dims
        _coords = [
            *zip(_dims, (np.arange(dim_len) for dim_len in _values.shape), strict=False)
        ]
        _head = Py3grdHeader._from_dto(_grd_data)
        _dataarray = xr.DataArray(_values, coords=_coords, name=name or _head.p_field)

        return cls(dataarray=_dataarray, head=_head, meta={})

    @classmethod
    def from_filepath(cls, filepath: FsPath, *, name: str | None = None) -> Py3grd:
        """Return a PyGrd object given a path to a 2/3 grid file

        Args:
            filepath (str): fspath to a 3grd
            name (str): dataarray name

        Returns:
            Py3grd object

        """
        return cls.from_fspath(fspath=filepath, name=name)

    def _update_dimensions(self) -> None:
        self.head.zlev, self.head.yrow, self.head.xcol = self.dataarray.values.shape

    def _update_header(self) -> None:
        self._update_node_range()
        self._update_dimensions()

    def update_obj(self) -> None:
        """Update header values and sanity check"""
        self._update_header()

    @classmethod
    def from_buffer(cls, bites: bytes | BinaryIO) -> Py3grd:
        """Return a PyGrd object given a path to a 2/3 grid file

        Args:
            bites (Union[bytes, BinaryIO]): bytes or buffer with 3grd data

        Returns:
            Py3grd object

        """
        _grd_data = load_3grd_buffer(bites)
        _values: Arr = _grd_data.values()
        _dims = _grd_data.dims
        _filename = path.split("buffer")[-1]
        _coords = [
            *zip(_dims, (np.arange(dim_len) for dim_len in _values.shape), strict=False)
        ]
        _dataarray = xr.DataArray(_values, coords=_coords)
        return cls(
            dataarray=_dataarray,
            head=Py3grdHeader.from_dict(
                data={**_grd_data.model_dump(), "filename": _filename}
            ),
            meta={},
        )

    def to_fspath(self, fspath: FsPath) -> FsPath:
        """Write the Py3grd object to a fspath"""
        self._update_node_range()
        self._update_header()
        _attrs_data = {**self.head.model_dump(), **self.head.dump_dict()}
        _pygrd_io = Py3grdWriter(pygrd=self)
        _pygrd_io.__dict__.update(_attrs_data)
        _pygrd_io.__dict__["values"] = self.nparr
        _pygrd_io.save_grd(str(fspath))
        return fspath

    @classmethod
    def from_dict(cls, dictionary: dict[str, Any]) -> Py3grd:
        """Create a Py3grd object from a dictionary"""
        return cls(**{
            "head": Py3grdHeader.from_dict(dictionary["head"]),
            "dataarray": xr.DataArray.from_dict(dictionary["dataarray"]),
            "meta": dictionary.get("meta", {}),
        })

    @classmethod
    def from_pydat(cls, pydat: Pydat) -> Py3grd:
        """Create and return Py3grd object from Pydat object"""
        raise NotImplementedError

    def to_pydat(
        self, *, multiindex: bool = False, p_field: str | None = None, **kwargs: Any
    ) -> Pydat:
        """Create and return Pydat object from Py3grd"""
        from dgpy import dgio

        return dgio.py3grd_to_pydat(self, multiindex=multiindex, p_field=p_field)

    @classmethod
    def from_dataarray(
        cls,
        dataarray: xr.DataArray,
        *,
        meta: dict[Any, Any] | None = None,
        bounds: BoundingBox | None = None,
    ) -> Py3grd:
        """Create and return a Py3grid given a 3D xarray.DataArray"""
        da_shape = dataarray.shape
        if len(da_shape) != 3:
            if len(da_shape) == 2:
                raise ValueError(
                    "Array given must be 3-dimensional array; "
                    "was given a 2-dimensional array use dgpy.Py2grd"
                )
            raise ValueError("Array given must be 3-dimensional array")
        zlevels, yrows, xcolumns = dataarray.shape

        if bounds:
            ymin, ymax = bounds.ymin, bounds.ymax
            xmin, xmax = bounds.xmin, bounds.xmax
            zmin, zmax = bounds.zmin, bounds.zmax
        else:
            ymin, ymax = 0.0, yrows
            xmin, xmax = 0.0, xcolumns
            zmin, zmax = 0.0, zlevels
        py3grd_obj = Py3grd(
            head=Py3grdHeader(
                xcol=xcolumns,
                yrow=yrows,
                zlev=zlevels,
                nulls_in_grid=0,
                is_2d=False,
                space=PySpace(
                    is_2d=False,
                    space_flag=2,
                    xpivot=xmin,
                    ypivot=ymin,
                    zpivot=zmin,
                    # x axis
                    loc_xaxis_x=xmax,
                    loc_xaxis_y=0,
                    loc_xaxis_z=0,
                    # y axis
                    loc_yaxis_x=0,
                    loc_yaxis_y=ymax,
                    loc_yaxis_z=0,
                    # z axis
                    loc_zaxis_x=0,
                    loc_zaxis_y=0,
                    loc_zaxis_z=zmax,
                ),
            ),
            dataarray=dataarray,
            meta=meta or {},
        )
        py3grd_obj._update_header()
        return py3grd_obj

    @classmethod
    def from_ndarray(
        cls,
        arr: npt.NDArray,
        *,
        meta: dict[Any, Any] | None = None,
        coords: tuple[str, str, str] = ("zlevels", "yrows", "xcolumns"),
        bounds: BoundingBox | None = None,
    ) -> Py3grd:
        """Return a py3grd from a given numpy.ndarray"""
        if len(arr.shape) != 3:
            if len(arr.shape) == 2:
                raise ValueError(
                    "Array given must be 3-dimensional array; "
                    "was given a 2-dimensional array use dgpy.Py2grd"
                )
            raise ValueError("Array given must be 3-dimensional array")
        zlevels, yrows, xcolumns = arr.shape
        da = xr.DataArray(
            data=arr,
            coords={
                "zlevels": np.linspace(
                    bounds.zminboundingbox
                    if bounds.zminboundingbox is not None
                    else 0.0,
                    bounds.zmaxboundingbox
                    if bounds.zmaxboundingbox is not None
                    else float(zlevels - 1),
                    zlevels,
                )
                if bounds
                else range(zlevels),
                "yrows": np.linspace(
                    bounds.yminboundingbox, bounds.ymaxboundingbox, yrows
                )
                if bounds
                else range(yrows),
                "xcolumns": np.linspace(
                    bounds.xminboundingbox, bounds.xmaxboundingbox, xcolumns
                )
                if bounds
                else range(xcolumns),
            },
            dims=coords,
        )
        return Py3grd.from_dataarray(dataarray=da, meta=meta, bounds=bounds)


class Py3grdWriter(PygrdWriterBase):
    """PyGrd reading/writing class"""

    pygrd: Py3grd
    head: Py3grdHeader

    def __init__(self, pygrd: Py3grd, name: str = "") -> None:
        """Py3grdWriter constructor

        Args:
            pygrd (Py3grd): Py3grd object to write
            name (str): Name to use when writing

        """
        self.pygrd = pygrd
        self.head = pygrd.head
        self.name = name

    def __str__(self) -> str:
        """Return string representation of object"""
        return pformat(self.__dict__, compact=True)

    def magic_token_bytes(self) -> bytes:
        """Return Py3grd magic bytes

        Returns:
            bytes

        """
        return pack("I", 0x3D763D76)

    def _bin_gen(self) -> Iterable[bytes]:
        _orig_dict = dict(self.__dict__.items())
        yield self.magic_token_bytes()
        # Tokens to ordered by header tokens then values tokens
        for _token in Py3grdWriter.pygrd_evg_tokens(self.pygrd):
            if _token != Evg.space:
                yield self.pack_token(_token)
            else:
                yield self.pygrd.head.space.pack_bin()
        self.__dict__.update(_orig_dict)

    def write2buffer(self, buf: BinaryIO | BytesIO) -> None:
        """Write Py3grd data to binary file like object"""
        buf.write(b"".join(self._bin_gen()))

    def save_grd(self, filepath: str) -> None:
        """Write out to a grid file

        Args:
            filepath (str): fspath (relative or absolute) of where to write

        Returns:
            None

        """
        if str(filepath).startswith("s3://"):
            bio = BytesIO()
            self.write2buffer(bio)
            sh.write_bytes(filepath, bio.getvalue())
        else:
            with open(filepath, "wb") as f:
                self.write2buffer(f)

    @staticmethod
    def pygrd_evg_tokens(pygrd: Py3grd, node_bits: int = 32) -> Iterable[Evg]:
        """Tokens to write for py3grd

        Previous impl using strings:
        ```
        @staticmethod
        def pygrd_evg_tokens(pygrd: Py3grd, node_bits: int = 32) -> Iterable[str]:
            yield 'Evg_version'
            if pygrd.head.alias:
                yield 'Evg_alias'
            if pygrd.head.desc:
                yield 'Evg_desc'
            yield 'Evg_space'
            if pygrd.head.coordinate_system_id:
                yield 'Evg_coordinateSystemId'
            if pygrd.head.coordinate_system_name:
                yield 'Evg_coordinateSystemName'

            yield 'Evg_xcol'
            yield 'Evg_yrow'
            yield 'Evg_zlev'
            if pygrd.head.dat:
                yield 'Evg_dat'
            if pygrd.head.p_field:
                yield 'Evg_field'

            yield 'Evg_property_node'

            if pygrd.head.trend_order:
                yield 'Evg_trendOrder'
                yield 'Evg_trendCoefficients'
                yield 'Evg_trendOffsets'

            ##############
            # 3grid only #
            ##############
            if pygrd.head.punits and pygrd.head.punits != 'unknown':
                yield 'Evg_punits'
            if pygrd.head.pclip:
                yield 'Evg_pclip'
                if pygrd.head.clip_poly:
                    yield 'Evg_clipPoly'
            if pygrd.head.clamp:
                yield 'Evg_clamp'

            yield 'Evg_zInfluence'
            ## END OF 3grd only

            if pygrd.head.bpoly:
                yield 'Evg_bpoly'

            yield 'Evg_nullsInGrid'
            yield 'Evg_geometry'
            yield 'Evg_nodeRange'
            yield 'Evg_endOfHeader'

            if pygrd.head.date:
                yield 'Evg_date'
            if pygrd.head.seismic_line_and_trace_labels:
                yield 'Evg_seismicLineAndTraceLabels'
            if pygrd.head.history:
                yield 'Evg_history'
            yield 'Evg_endOfHeader'
            if node_bits != 32:
                yield 'Evg_bitFactor'
                yield 'Evg_bitShift'
                if node_bits == 16:
                    yield 'Evg_16bitValues'
                elif node_bits == 8:
                    yield 'Evg_8bitValues'
            else:
                yield 'Evg_values'
        ```
        """
        yield Evg.version
        if pygrd.head.alias:
            yield Evg.alias
        if pygrd.head.desc:
            yield Evg.desc
        yield Evg.space
        if pygrd.head.space.coordinate_system_id:
            yield Evg.coordinate_system_id
        if pygrd.head.space.coordinate_system_name:
            yield Evg.coordinate_system_name

        yield Evg.xcol
        yield Evg.yrow
        yield Evg.zlev
        if pygrd.head.dat:
            yield Evg.dat
        if pygrd.head.p_field:
            yield Evg.field

        yield Evg.property_node

        if pygrd.head.trend_order:
            yield Evg.trend_order
            yield Evg.trend_coefficients
            yield Evg.trend_offsets

        ##############
        # 3grid only #
        ##############
        if pygrd.head.punits and pygrd.head.punits != "unknown":
            yield Evg.punits
        if pygrd.head.pclip:
            yield Evg.pclip
            if pygrd.head.clip_poly:
                yield Evg.clip_poly
        if pygrd.head.clamp:
            yield Evg.clamp
        # TODO: handle xform

        yield Evg.z_influence
        # END OF 3grd only

        if pygrd.head.bpoly:
            yield Evg.bpoly

        yield Evg.nulls_in_grid
        yield Evg.geometry
        yield Evg.node_range

        if pygrd.head.date:
            yield Evg.date
        if pygrd.head.seismic_line_and_trace_labels:
            yield Evg.seismic_line_and_trace_labels
        if pygrd.head.history:
            yield Evg.history
        yield Evg.end_of_header
        if node_bits != 32:
            yield Evg.bit_factor
            yield Evg.bit_shift
            if node_bits == 16:
                yield Evg.values_16bit
            elif node_bits == 8:
                yield Evg.values_8bit
        else:
            yield Evg.values
