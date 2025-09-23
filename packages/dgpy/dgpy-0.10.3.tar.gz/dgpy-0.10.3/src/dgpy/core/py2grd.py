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
"""Dynamic Graphics Python 2grid"""

from __future__ import annotations

from io import BytesIO
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
from shellfish import fs

from dgpy.core.boundingbox import BoundingBox
from dgpy.core.enums import evu_validate
from dgpy.core.py6grd.evg import Evg
from dgpy.core.py6grd.py6grd_base import Py6grdBase, Py6grdHeaderBase
from dgpy.core.py6grd.py6grd_io import PygrdWriterBase, load_grd
from dgpy.core.pyspace import PySpace
from dgpy.maths import rotation_matrix_3d
from dgpy.utils.builtins import replace_keys

if TYPE_CHECKING:
    from collections.abc import Iterable

    from dgpy import npt
    from dgpy._types import FsPath
    from dgpy.core.py6grd.py6grd_dto import PygrdHeaderDTO
    from dgpy.pydat import Pydat

TPy2grdHeader = TypeVar("TPy2grdHeader", bound="Py2grdHeader")


class Py2grdHeader(Py6grdHeaderBase):
    """Header object for the Py2grd; inherits from the Py6grdHeaderBase

    ```
    from dgpy import Py2grdHeader
    ```
    """

    xcol: int
    yrow: int

    nulls_in_grid: int | None = None
    geometry: int = Field(
        default=0,
        title="geometry",
        description="Grid geometry; used by bordered (py)2grids",
    )
    fspath: str | None = Field(
        default=None, title="filepath", description="Optional file system path to 2grd"
    )

    dat: str = ""
    is_bordered: bool = False
    vfault: str | None = None
    nvfault: str | None = None
    vf: tuple[int, ...] | None = None
    nvf: tuple[int, ...] | None = None
    node_range: tuple[float, float] = (0.0, 0.0)
    z_field: str = "z"
    bit_factor: float = 1.0
    bit_shift: float = 0.0
    bpoly: str | None = None
    pclip: tuple[float, float] = (0.0, 0.0)
    clip_poly: str | None = None
    trend_order: Any = None
    trend_coefficients: tuple[int, ...] | None = None
    trend_offsets: tuple[int, ...] | None = None
    data_order: int | None = None

    # =============
    # 2grd specific
    # =============
    is_2d: Literal[True] = Field(default=True, title="is_2d")
    zlev: int = Field(
        default=1,
        title="zlev",
        description="number of z-levels; will be 1 for Py2grdHeader",
    )
    type: str = "2grd"
    punits: str = "unknown"
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

    @field_validator("punits", mode="before")
    @classmethod
    def validate_units(cls, v: Any) -> str:
        return evu_validate(v)

    def dump_dict(self) -> dict[str, str | float | int | list[Any] | None]:
        """Return dictionary of dump data"""
        _attrs_d = {
            k.strip(" "): v if not isinstance(v, bytes) else v.decode()
            for k, v in self.model_dump().items()
        }
        return {
            "alias": "",
            "attributes": [],
            "desc": self.desc,
            "type": self.type,
            **self.model_dump(),
            **_attrs_d,
            **self.space.dump_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any], *, sanitize: bool = False) -> Py2grdHeader:
        """Create and return a Py2grdHeader from dictionary

        Args:
            data (dict[str, Any]): Data dictionary

        Returns:
            Py2grdHeader object

        """
        if "field" in data:
            data["z_field"] = data.pop("field")
        return cls(**data)

    def to_dict(self) -> dict[str, Any]:
        """Return dictionary of Py2grdHeader data"""
        _d: dict[str, str | float | int | bool | tuple[Any, ...] | None] = {
            **self.model_dump()
        }
        _d = replace_keys(_d, {"z_field": "field"})
        return _d

    @classmethod
    def _from_dto(cls, dto: PygrdHeaderDTO) -> Py2grdHeader:
        """Create and return Py2grdHeader from data transfer object (DTO)"""
        return Py2grdHeader.from_dict(dto.py2grd_data_dict())


class Py2grd(Py6grdBase):
    """2grid object class

    ```
    from dgpy import Py2grd
    ```

    dgpy.Py2grd objects contain:

        head: dgpy.Py2grdHeader
        dataarray: xarray.DataArray
        meta: dict[Any, Any]

    """

    head: Py2grdHeader
    dataarray: xr.DataArray
    meta: dict[str, Any] = Field(default_factory=dict)
    Bounds: ClassVar[type[BoundingBox]] = BoundingBox

    def deepcopy(self) -> Py2grd:
        """Return a deep copy of the Pygrd object"""
        return Py2grd(
            head=self.head.model_copy(deep=True),
            dataarray=self.dataarray.copy(deep=True),
        )

    def copy(self, *, deep: bool = True) -> Py2grd:  # type: ignore[override]
        """Return a deep copy of the Pygrd object"""
        return Py2grd(
            head=self.head.model_copy(), dataarray=self.dataarray.copy(deep=deep)
        )

    def is_bordered(self) -> bool:
        """Return True if `Py2grd` is bordered; False if not bordered

        Returns:
            bool

        """
        self.head.is_bordered = self.head.geometry == 8
        return self.head.is_bordered

    @field_validator("dataarray")
    @classmethod
    def _validate_dataarray(cls, v: xr.DataArray) -> xr.DataArray:
        if len(v.shape) != 2:
            raise ValueError(
                f"DataArray must be 2-dimensional; given DataArray has shape: {v.shape}"
            )
        return v

    def _get_xyz(self) -> tuple[xr.DataArray, ...]:
        """Return data arrays for X and Y spatial components of a 2grd"""
        _x = np.linspace(0, self.head.space.xrange, self.head.xcol)
        _y = np.linspace(0, self.head.space.yrange, self.head.yrow)
        _z: npt.NDArray = np.array([0])

        _xyz_mesh = np.meshgrid(_y, _z, _x)
        _xyz: npt.NDArray = np.stack(_xyz_mesh)
        _rot_axis = [0, 1, 0]
        _shape = _xyz.shape
        rot_mat = rotation_matrix_3d(np.array(_rot_axis), self.head.angle_rad)
        _xyz = _xyz.reshape((3, -1)).transpose()
        zyx_coords = np.dot(_xyz, rot_mat)
        z = zyx_coords[:, 1]
        z = z.T.reshape(_shape[1:])
        y = zyx_coords[:, 0] + self.head.space.ypivot
        y = y.T.reshape(_shape[1:])[0]
        x = zyx_coords[:, 2] + self.head.space.xpivot
        x = x.T.reshape(_shape[1:])[0]
        dim_order = ["yrows", "xcolumns"]
        return (xr.DataArray(x, dims=dim_order), xr.DataArray(y, dims=dim_order))

    def add_spatial_coordinates(self) -> None:
        """Add spatial coordinates to grid DataArray"""
        _x, _y = self._get_xyz()
        self.dataarray["x"] = _x
        self.dataarray["y"] = _y

    @classmethod
    def from_fspath(cls, fspath: FsPath, *, name: str | None = None) -> Py2grd:
        """Return a PyGrd object given a path to a 2/3 grid file

        Args:
            fspath (FsPath): path to a 2grd

        Returns:
            Py2grd object

        """
        _grd_data = load_grd(fspath, skip_nodes=False)
        _grd_data.ensure_space_2d()
        _grd_data.fspath = str(fspath)
        _values = _grd_data.values()
        _dims = _grd_data.dims
        _coords = [
            *zip(_dims, (np.arange(dim_len) for dim_len in _values.shape), strict=False)
        ]
        _head = Py2grdHeader._from_dto(dto=_grd_data)
        _dataarray = xr.DataArray(
            _values, coords=_coords, name=name or _head.z_field or "z"
        )
        return cls(dataarray=_dataarray, head=_head, meta={})

    @classmethod
    def from_filepath(cls, filepath: FsPath, *, name: str | None = None) -> Py2grd:
        """Return a PyGrd object given a path to a 2/3 grid file

        Args:
            filepath (FsPath): path to a 2grd/3grd/m3grd/c3grd file

        Returns:
            PyGrd object

        """
        return cls.from_fspath(fspath=filepath, name=name)

    def _update_dimensions(self) -> None:
        self.head.yrow, self.head.xcol = self.dataarray.values.shape

    def _update_header(self) -> None:
        self._update_node_range()
        self._update_dimensions()

    def update_obj(self) -> None:
        """Update header values and sanity check"""
        self._update_node_range()
        self._update_dimensions()

    def to_fspath(self, fspath: FsPath) -> FsPath:
        """Write Py2grd to fspath"""
        self._update_header()
        self._update_node_range()
        _attrs_data = {
            **self.head.model_dump(),
            **self.head.space.model_dump(),
            **self.head.dump_dict(),
        }
        _pygrd_io = Py2grdWriter(pygrd=self)
        _pygrd_io.__dict__.update(_attrs_data)
        _pygrd_io.__dict__["values"] = self.nparr
        _pygrd_io.save_grd(str(fspath))
        return fspath

    @classmethod
    def from_dict(cls, dictionary: dict[str, Any]) -> Py2grd:
        """Return a Py2grd object from a dictionary of data"""
        dataarray = xr.DataArray.from_dict(dictionary["dataarray"])
        dataarray.values = np.array(dataarray.values, dtype=np.float64)
        return cls(**{
            "head": Py2grdHeader.from_dict(dictionary["head"]),
            "dataarray": dataarray,
            "meta": dictionary.get("meta", {}),
        })

    def to_pydat(
        self, *, multiindex: bool = False, z_field: str | None = None, **kwargs: Any
    ) -> Pydat:
        """Return the py2grd as a Pydat object"""
        from dgpy import dgio

        return dgio.py2grd_to_pydat(self, multiindex=multiindex, z_field=z_field)

    @classmethod
    def from_dataarray(
        cls,
        dataarray: xr.DataArray,
        *,
        meta: dict[Any, Any] | None = None,
        bounds: BoundingBox | None = None,
    ) -> Py2grd:
        """Create and return a Py2grid given a 2D xarray.DataArray"""
        da_shape = dataarray.shape

        if len(da_shape) != 2:
            if len(da_shape) == 3:
                raise ValueError(
                    "Array given must be 2-dimensional array; "
                    "was given a 3-dimensional array use dgpy.Py3grd"
                )
            raise ValueError("Array given must be 2-dimensional array")

        yrows, xcolumns = dataarray.shape

        if bounds:
            ymin, ymax = bounds.ymin, bounds.ymax
            xmin, xmax = bounds.xmin, bounds.xmax
        else:
            ymin, ymax = 0.0, yrows
            xmin, xmax = 0.0, xcolumns
        py2grd_obj = Py2grd(
            head=Py2grdHeader(
                xcol=xcolumns,
                yrow=yrows,
                nulls_in_grid=0,
                is_2d=True,
                space=PySpace(
                    is_2d=True,
                    space_flag=1,
                    xpivot=xmin,
                    ypivot=ymin,
                    zpivot=0,
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
                    loc_zaxis_z=1,
                ),
            ),
            dataarray=dataarray,
            meta=meta or {},
        )
        py2grd_obj._update_header()
        return py2grd_obj

    @classmethod
    def from_ndarray(
        cls,
        arr: npt.NDArray,
        *,
        meta: dict[Any, Any] | None = None,
        coords: tuple[str, str] = ("yrows", "xcolumns"),
        bounds: BoundingBox | None = None,
    ) -> Py2grd:
        """Return a py2grd from a given numpy.ndarray"""
        if len(arr.shape) != 2:
            if len(arr.shape) == 3:
                raise ValueError(
                    "Array given must be 2-dimensional array; "
                    "was given a 3-dimensional array use dgpy.Py3grd"
                )
            raise ValueError("Array given must be 2-dimensional array")

        yrows, xcolumns = arr.shape
        da = xr.DataArray(
            data=arr,
            coords={
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
        return Py2grd.from_dataarray(dataarray=da, meta=meta, bounds=bounds)


class Py2grdWriter(PygrdWriterBase):
    """PyGrd reading/writing class"""

    pygrd: Py2grd
    head: Py2grdHeader

    def __init__(self, pygrd: Py2grd, name: str = "") -> None:
        """Py2grdWriter constructor

        Args:
            pygrd (Py2grd): Py2grd object to write
            name (str): Name to use when writing

        """
        self.pygrd = pygrd
        self.head = pygrd.head
        self.name = name

    def __str__(self) -> str:
        """Return string representation of object"""
        return pformat(self.__dict__, compact=True)

    def magic_token_bytes(self) -> bytes:
        """Return 2grd magic token bytes"""
        return pack("I", 0x2D762D76)

    def _bin_gen(self) -> Iterable[bytes]:
        """Yield byte chunks to write"""
        _orig_dict = dict(self.__dict__.items())
        yield self.magic_token_bytes()

        # Tokens to ordered by header tokens then values tokens
        for _token in Py2grdWriter.pygrd_evg_tokens(self.pygrd):
            if _token != Evg.space:
                yield self.pack_token(_token)
            else:
                yield self.pygrd.head.space.pack_bin()
        self.__dict__.update(_orig_dict)

    def write2buffer(self, buf: BinaryIO | BytesIO) -> None:
        """Write Py2grd data to binary file like object"""
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
            fs.write_bytes(filepath, bio.getvalue())
        else:
            with open(filepath, "wb") as f:
                self.write2buffer(f)

    @staticmethod
    def pygrd_evg_tokens(pygrd: Py2grd, node_bits: int = 32) -> Iterable[Evg]:
        """Tokens to write

        Previous iml using strings:
        ```python
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
        if pygrd.head.dat:
            yield 'Evg_dat'
        if pygrd.head.p_field:
            yield 'Evg_field'

        ##############
        # py2grid only #
        ##############
        if pygrd.head.vfault:
            yield 'Evg_vfault'
        if pygrd.head.nvfault:
            yield 'Evg_nvfault'

        yield 'Evg_property_node'

        if pygrd.head.trend_order:
            yield 'Evg_trendOrder'
            yield 'Evg_trendCoefficients'
            yield 'Evg_trendOffsets'

        if pygrd.head.bpoly:
            yield 'Evg_bpoly'

        yield 'Evg_nullsInGrid'
        # yield 'Evg_geometry'
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
        if pygrd.head.dat:
            yield Evg.dat
        if pygrd.head.z_field:
            yield Evg.field

        ##############
        # py2grid only #
        ##############
        if pygrd.head.vfault:
            yield Evg.vfault
        if pygrd.head.nvfault:
            yield Evg.nvfault
        if pygrd.head.vf:
            yield Evg.vf
        if pygrd.head.nvf:
            yield Evg.nvf

        yield Evg.property_node

        if pygrd.head.trend_order:
            yield Evg.trend_order
            yield Evg.trend_coefficients
            yield Evg.trend_offsets

        if pygrd.head.bpoly:
            yield Evg.bpoly

        yield Evg.nulls_in_grid
        # yield 'Evg_geometry'
        yield Evg.node_range

        if pygrd.head.date:
            yield Evg.date
        # if pygrd.head.seismic_line_and_trace_labels:
        #     yield Evg.seismicLineAndTraceLabels
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
