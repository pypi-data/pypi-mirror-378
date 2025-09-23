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
"""Dgpy geo-space object"""

from __future__ import annotations

import logging

from struct import calcsize, error as struct_error, pack, unpack
from typing import TYPE_CHECKING, Any, TypeAlias, TypedDict, TypeVar, cast

import numpy as np

from jsonbourne import JSON
from pydantic import field_validator

from dgpy import maths
from dgpy.core.boundingbox import BoundingBox
from dgpy.core.enums.eve import Eve
from dgpy.core.enums.evp import Evp
from dgpy.core.enums.evu import evu_string_to_enum, evu_validate
from dgpy.dgpydantic import DgpyBaseModel

if TYPE_CHECKING:
    from collections.abc import Callable

    from dgpy import npt

__all__ = ("PySpace", "TProjParms")

log = logging.getLogger(__name__)
TPySpace = TypeVar("TPySpace", bound="PySpace")
TProjParms: TypeAlias = tuple[
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
]


class PySpaceProperties(TypedDict):
    """TypedDict for PySpace properties"""

    angle: float
    xmin: float
    xmax: float
    ymin: float
    ymax: float
    zmin: float
    zmax: float
    xrange: float
    yrange: float
    zrange: float


class PySpace(DgpyBaseModel):
    """DGPY implementation of `GeoSpace`"""

    # pivot
    xpivot: float
    ypivot: float
    zpivot: float

    # s/x axis
    loc_xaxis_x: float
    loc_xaxis_y: float
    loc_xaxis_z: float

    # t/y axis
    loc_yaxis_x: float
    loc_yaxis_y: float
    loc_yaxis_z: float

    # u/z axis
    loc_zaxis_x: float
    loc_zaxis_y: float
    loc_zaxis_z: float

    is_2d: bool

    coordinate_system_id: str = ""
    coordinate_system_name: str = ""
    msl: float = 1.0e20

    projection: Evp | None = None
    proj_parms: TProjParms | None = None
    ellipsoid: Eve | None = None
    downward: bool = False
    zone: int | None = None
    xyunits: str = "unknown"
    zunits: str = "unknown"
    space_flag: int = -1
    space_version: int = 2

    @field_validator("xyunits", "zunits", mode="before")
    @classmethod
    def validate_units(cls: Any, v: Any) -> str:
        return evu_validate(v)

    @property
    def xmin(self) -> float:
        """Return the xmin value for the PySpace object"""
        return self.boundingbox().xmin

    @property
    def xmax(self) -> float:
        """Return the xmax value for the PySpace object"""
        return self.boundingbox().xmax

    @property
    def ymin(self) -> float:
        """Return the ymin value for the PySpace object"""
        return self.boundingbox().ymin

    @property
    def ymax(self) -> float:
        """Return the ymax value for the PySpace object"""
        return self.boundingbox().ymin

    @property
    def zmin(self) -> float:
        """Return the zmin value for the PySpace object"""
        return self.boundingbox().zmin

    @property
    def zmax(self) -> float:
        """Return the zmax value for the PySpace object"""
        return self.boundingbox().zmax

    @property
    def pivot(self) -> npt.NDArray:
        """Return the pivot point as a numpy array with shape 3x1"""
        return np.array([self.xpivot, self.ypivot, self.zpivot])

    @property
    def loc_xaxis(self) -> npt.NDArray:
        """Return the local x axis as a numpy array with shape 3x1"""
        return np.array([self.loc_xaxis_x, self.loc_xaxis_y, self.loc_xaxis_z])

    @property
    def loc_yaxis(self) -> npt.NDArray:
        """Return the local y axis as a numpy array with shape 3x1"""
        return np.array([self.loc_yaxis_x, self.loc_yaxis_y, self.loc_yaxis_z])

    @property
    def loc_zaxis(self) -> npt.NDArray:
        """Return the local z axis as a numpy array with shape 3x1"""
        return np.array([self.loc_zaxis_x, self.loc_zaxis_y, self.loc_zaxis_z])

    @property
    def angle_rad(self) -> float:
        """Return PySpace angle as radians"""
        return maths.signed_angle(
            self.loc_xaxis, np.array([1, 0, 0]), np.array([0, 0, 1])
        )

    @property
    def ijk2xyz(self) -> npt.NDArray:
        """Return the ijk2xyz transformation matrix (shape is 4x4)"""
        return np.array([
            [self.loc_xaxis_x, self.loc_yaxis_x, self.loc_zaxis_x, self.xpivot],
            [self.loc_xaxis_y, self.loc_yaxis_y, self.loc_zaxis_y, self.ypivot],
            [self.loc_xaxis_z, self.loc_yaxis_z, self.loc_zaxis_z, self.zpivot],
            [0, 0, 0, 1],
        ])

    @property
    def angle_deg(self) -> float:
        """Return angle as degrees"""
        r = float(np.rad2deg(self.angle_rad))
        if r == 360:
            return 0.0
        elif r > 360:
            return r % 360
        return r

    @property
    def angle(self) -> float:
        """Return angle as degrees"""
        return self.angle_deg

    @property
    def xrange(self) -> float:
        """Return the xrange for the PySpace object"""
        _loc_xaxis = self.loc_xaxis
        return float(np.sqrt(np.dot(_loc_xaxis, _loc_xaxis)))

    @property
    def yrange(self) -> float:
        """Return the yrange for the PySpace object"""
        _loc_yaxis = self.loc_yaxis
        return float(np.sqrt(np.dot(_loc_yaxis, _loc_yaxis)))

    @property
    def zrange(self) -> float:
        """Return the zrange for the PySpace object"""
        _loc_zaxis = self.loc_zaxis
        return float(np.sqrt(np.dot(_loc_zaxis, _loc_zaxis)))

    def boundingbox(self) -> BoundingBox:
        """Calculate and return the BoundingBox for the PySpace object

        Returns:
            BoundingBox object

        """
        corner_pts: npt.NDArray = np.array([
            self.pivot,
            self.loc_xaxis + self.pivot,
            self.loc_yaxis + self.pivot,
            self.loc_zaxis + self.pivot,
            self.loc_xaxis + self.loc_yaxis + self.pivot,
            self.loc_xaxis + self.loc_zaxis + self.pivot,
            self.loc_yaxis + self.loc_zaxis + self.pivot,
            self.loc_xaxis + self.loc_yaxis + self.loc_zaxis + self.pivot,
        ])
        x = corner_pts[:, 0]
        y = corner_pts[:, 1]
        z = corner_pts[:, 2]
        return BoundingBox(
            xmin=float(np.amin(x)),
            xmax=float(np.amax(x)),
            ymin=float(np.amin(y)),
            ymax=float(np.amax(y)),
            zmin=float(np.amin(z)),
            zmax=float(np.amax(z)),
        )

    def properties_dict(self) -> PySpaceProperties:
        """Return all the PySpace properties and values as a dictionary"""
        _bbox = self.boundingbox()
        return {
            "angle": self.angle_deg,
            "xmin": _bbox.xmin,
            "xmax": _bbox.xmax,
            "ymin": _bbox.ymin,
            "ymax": _bbox.ymax,
            "zmin": _bbox.zmin,
            "zmax": _bbox.zmax,
            "xrange": self.xrange,
            "yrange": self.yrange,
            "zrange": self.zrange,
        }

    def dump_dict(self) -> dict[str, str | float | int]:
        """Return a dictionary of the header dump data for a PySpace"""
        return {
            **cast("dict[str, float]", self.properties_dict()),
            **self.model_dump(),
            **self.boundingbox().model_dump(),
        }

    def _xyunits_enum(self) -> int:
        """Return the xyunits enum value for the PySpace"""
        return evu_string_to_enum(self.xyunits)

    def _zunits_enum(self) -> int:
        """Return the zunits enum value for the PySpace"""
        zunits_enum_int = evu_string_to_enum(self.zunits)
        if self.downward:
            zunits_enum_int += 4096
        return zunits_enum_int

    @classmethod
    def from_bytes(cls, buffer: bytes) -> PySpace:
        """Unpack a the evg_space binary data for a dgi-grid

        Args:
            buffer: bytes containing space data

        Returns:
            dictionary with grid space data

        NOTE: For some reason, ALL values in Evg_space are written as Big Endian,
              NOT in native byte order.

        """
        unpacked_space_data = unpack_space_bytes(buffer)

        return cls(**{
            k: v for k, v in unpacked_space_data.items() if k in cls.__pydantic_fields__
        })

    def _proj_parms_iterable(self) -> list[float]:
        return [*self.proj_parms] if self.proj_parms is not None else []

    def to_bytes(self) -> bytes:
        """Return the packed up version of the PySpace as bytes for IO"""
        # SANITIZE DATA FOR WRITING
        if self.xyunits in ("unknown", "-1", None):
            self.xyunits = "unknown"
        if self.projection in ("unknown", "-1", None):
            self.projection = Evp.LocalRect
        if self.zunits in ("unknown", "-1", None):
            self.zunits = "unknown"

        def _pack_evg_space_flag_1() -> bytes:
            space_length = "4"
            _bbox = self.boundingbox()
            if self.projection == -1 or self.projection is None:
                return pack(
                    f">ii{space_length}diiid",  # fmt string
                    self.space_version,
                    self.space_flag,
                    _bbox.xmin,
                    _bbox.xmax,
                    _bbox.ymin,
                    _bbox.ymax,
                    self.projection,
                    self._xyunits_enum(),
                    self._zunits_enum(),
                    self.msl,
                )
            else:
                projection_length = "15"
                tmp_bin = pack(
                    f">ii{space_length}diii{projection_length}diid",
                    self.space_version,
                    self.space_flag,
                    _bbox.xmin,
                    _bbox.xmax,
                    _bbox.ymin,
                    _bbox.ymax,
                    int(self.projection),
                    self.zone,
                    self.ellipsoid,
                    *self._proj_parms_iterable(),
                    self._xyunits_enum(),
                    self._zunits_enum(),
                    self.msl,
                )
                return tmp_bin

        def _pack_evg_space_flag_2() -> bytes:
            # non-rotated 3D grid
            space_length = "6"
            _bbox = self.boundingbox()
            if self.projection == -1 or self.projection is None:
                return pack(
                    f">ii{space_length}diiid",
                    self.space_version,
                    self.space_flag,
                    _bbox.xmin,
                    _bbox.xmax,
                    _bbox.ymin,
                    _bbox.ymax,
                    _bbox.zmin,
                    _bbox.zmax,
                    -1,  # None/null projection is -1
                    self._xyunits_enum(),
                    self._zunits_enum(),
                    self.msl,
                )

            else:
                projection_length = "15"
                return pack(
                    f">ii{space_length}diii{projection_length}diid",
                    self.space_version,
                    self.space_flag,
                    _bbox.xmin,
                    _bbox.xmax,
                    _bbox.ymin,
                    _bbox.ymax,
                    _bbox.zmin,
                    _bbox.zmax,
                    self.projection,
                    self.zone,
                    self.ellipsoid,
                    *self._proj_parms_iterable(),
                    self._xyunits_enum(),
                    self._zunits_enum(),
                    float(self.msl),
                )

        def _pack_evg_space_flag_4() -> bytes:
            # rotated 2D grid (in XY plane)
            space_length = "5"
            if self.projection == -1 or self.projection is None:
                return pack(
                    f">ii{space_length}diiid",
                    self.space_version,
                    self.space_flag,
                    self.xpivot,
                    self.ypivot,
                    self.xrange,
                    self.yrange,
                    self.angle_rad,
                    -1,  # None/null projection is -1
                    self._xyunits_enum(),
                    self._zunits_enum(),
                    self.msl,
                )
            else:
                projection_length = "15"
                return pack(
                    f">ii{space_length}diii{projection_length}diid",
                    self.space_version,
                    self.space_flag,
                    self.xpivot,
                    self.ypivot,
                    self.xrange,
                    self.yrange,
                    self.angle_rad,
                    self.projection,
                    self.zone,
                    self.ellipsoid,
                    *self._proj_parms_iterable(),
                    self._xyunits_enum(),
                    self._zunits_enum(),
                    self.msl,
                )

        def _pack_evg_space_flag_5() -> bytes:
            # rotated 3D grid (in XY plane)
            space_length = "7"
            _bbox = self.boundingbox()
            if self.projection == -1 or self.projection is None:
                return pack(
                    f">ii{space_length}diiid",
                    self.space_version,
                    self.space_flag,
                    self.xpivot,
                    self.ypivot,
                    self.xrange,
                    self.yrange,
                    self.angle_rad,
                    _bbox.zmin,
                    _bbox.zmax,
                    self.projection,
                    self._xyunits_enum(),
                    self._zunits_enum(),
                    self.msl,
                )
            else:
                projection_length = "15"
                return pack(
                    f">ii{space_length}diii{projection_length}diid",
                    self.space_version,
                    self.space_flag,
                    self.xpivot,
                    self.ypivot,
                    self.xrange,
                    self.yrange,
                    self.angle_rad,
                    _bbox.zmin,
                    _bbox.zmax,
                    self.projection,
                    self.zone,
                    self.ellipsoid,
                    *self._proj_parms_iterable(),
                    self._xyunits_enum(),
                    self._zunits_enum(),
                    self.msl,
                )

        def _pack_evg_space_flag_8() -> bytes:
            if self.projection == -1 or self.projection is None:
                space_length = "12"
                return pack(
                    f">ii{space_length}diiid",
                    self.space_version,
                    self.space_flag,
                    self.xpivot,
                    self.ypivot,
                    self.zpivot,
                    self.loc_xaxis_x,
                    self.loc_xaxis_y,
                    self.loc_xaxis_z,
                    self.loc_yaxis_x,
                    self.loc_yaxis_y,
                    self.loc_yaxis_z,
                    self.loc_zaxis_x,
                    self.loc_zaxis_y,
                    self.loc_zaxis_z,
                    self.projection,
                    self._xyunits_enum(),
                    self._zunits_enum(),
                    self.msl,
                )
            else:
                fmt_str = ">iiddddddddddddiii15diid"
                return pack(
                    fmt_str,
                    self.space_version,
                    self.space_flag,
                    self.xpivot,
                    self.ypivot,
                    self.zpivot,
                    self.loc_xaxis_x,
                    self.loc_xaxis_y,
                    self.loc_xaxis_z,
                    self.loc_yaxis_x,
                    self.loc_yaxis_y,
                    self.loc_yaxis_z,
                    self.loc_zaxis_x,
                    self.loc_zaxis_y,
                    self.loc_zaxis_z,
                    self.projection,
                    self.zone,
                    self.ellipsoid,
                    *self._proj_parms_iterable(),
                    self._xyunits_enum(),
                    self._zunits_enum(),
                    self.msl,
                )

        _space_flag_functions = {
            1: _pack_evg_space_flag_1,
            2: _pack_evg_space_flag_2,
            4: _pack_evg_space_flag_4,
            5: _pack_evg_space_flag_5,
            8: _pack_evg_space_flag_8,
        }
        log.debug("Space flag: {} -- Space flag: {}", self.space_flag, self.space_flag)
        return _space_flag_functions[self.space_flag]()

    def pack_bin(self) -> bytes:
        """Return the PySpace as bytes for writing of a Py2grd/Py3grd"""
        space_data_bin = self.to_bytes()
        return b"".join([
            pack("=I", 73),  # evg space token
            pack("=q", len(space_data_bin)),  # length of the space data
            space_data_bin,  # space data packed bytes
        ])

    def equiv(self, other: PySpace) -> bool:
        """Return True if this PySpace object is equiv to another PySpace obj"""
        self_dict = self.model_dump()
        other_dict = other.model_dump()
        for k, v in self_dict.items():
            if v != other_dict[k] and not np.isclose(v, other_dict[k]):
                log.debug(
                    "Key: {} -- self.value: {} -- other.value: {} -- np.isclose(): {}",
                    k,
                    v,
                    other_dict[k],
                    np.isclose(v, other_dict[k]),
                )
                return False
        return True

    @classmethod
    def from_json(cls, json_string: bytes | str) -> PySpace:
        """Create object from JSON string"""
        return cls(**JSON.loads(json_string))

    def to_json(
        self,
        *,
        fmt: bool = False,
        pretty: bool = False,
        sort_keys: bool = False,
        append_newline: bool = False,
        default: Callable[[Any], Any] | None = None,
        **kwargs: Any,
    ) -> str:
        return JSON.dumps(
            self.model_dump(),
            fmt=fmt,
            pretty=pretty,
            sort_keys=sort_keys,
            append_newline=append_newline,
            default=default,
            **kwargs,
        )


def unpack_space_bytes(buffer: bytes) -> dict[str, Any]:
    """Unpack bytes and return a data dictionary used to create a PySpace"""
    ellipsoid = None
    proj_parms = None
    angle = 0.0

    # Get space version
    buffer_count_start = 0
    buffer_count_end = buffer_count_start + calcsize("i")  # Add Integer length
    space_version = unpack(">i", buffer[buffer_count_start:buffer_count_end])[0]

    # Get space flag
    buffer_count_start = buffer_count_end
    buffer_count_end = buffer_count_start + calcsize("i")  # Add Integer length
    space_flag = unpack(">i", buffer[buffer_count_start:buffer_count_end])[0]
    buffer_count_start = buffer_count_end

    # Get space values
    if space_flag == 1:  # unrotated, 2D grid
        # UNPACKED SPACE STRUCTURE:
        # XMIN, XMAX, YMIN, YMAX
        buffer_count_end = buffer_count_start + 32
        _unpacked_space = unpack(">4d", buffer[buffer_count_start:buffer_count_end])
        assert len(_unpacked_space) == 4
        xmin, xmax, ymin, ymax = _unpacked_space
        xpivot = xmin
        xrange = abs(xmax - xmin)
        ypivot = ymin
        yrange = abs(ymax - ymin)
        angle = 0.0
        # x axis
        loc_xaxis_x = xrange
        loc_xaxis_y = 0.0
        loc_xaxis_z = 0.0
        # y axis
        loc_yaxis_x = 0.0
        loc_yaxis_y = yrange
        loc_yaxis_z = 0.0
        # z axis
        loc_zaxis_x = 0.0
        loc_zaxis_y = 0.0
        loc_zaxis_z = 1.0
        zrange = 0.0
        zmin = 0.0
        zmax = 0.0
        zpivot = 0.0

    elif space_flag == 2:  # unrotated, 3D grid
        # UNPACKED SPACE STRUCTURE:
        # XMIN, XMAX, YMIN, YMAX, ZMIN, ZMAX
        buffer_count_end = buffer_count_start + 48
        space_buffer = buffer[buffer_count_start:buffer_count_end]
        _unpacked_space = unpack(">6d", space_buffer)
        assert len(_unpacked_space) == 6
        xmin, xmax, ymin, ymax, zmin, zmax = _unpacked_space
        xpivot = xmin
        xrange = abs(xmax - xmin)
        ypivot = ymin
        yrange = abs(ymax - ymin)
        zpivot = zmin
        zrange = abs(zmax - zmin)
        angle = 0.0

        _xmax = max((xmax, xmin))
        _xmin = min((xmax, xmin))
        loc_xaxis_x = abs(_xmax - _xmin)
        loc_xaxis_y = 0.0
        loc_xaxis_z = 0.0

        loc_yaxis_x = 0.0
        loc_yaxis_y = ymax - ymin
        loc_yaxis_z = 0.0

        loc_zaxis_x = 0.0
        loc_zaxis_y = 0.0
        loc_zaxis_z = zmax - zmin

    elif space_flag == 4:  # rotated in XY plane, 2D grid
        # UNPACKED SPACE STRUCTURE:
        # XPIVOT, YPIVOT, XRANGE, YRANGE, ANGLE-RADS
        buffer_count_end = buffer_count_start + 40
        _unpacked_space = unpack(">5d", buffer[buffer_count_start:buffer_count_end])
        assert len(_unpacked_space) == 5
        xpivot, ypivot, xrange, yrange, angle = _unpacked_space
        zmin = 0.0
        zmax = 0.0
        zpivot = 0.0
        xmin = xpivot
        ymin = ypivot

        zrange = 0.0

        loc_xaxis_x = np.cos(angle) * xrange
        loc_xaxis_y = -np.sin(angle) * xrange
        loc_xaxis_z = 0.0

        loc_yaxis_x = np.sin(angle) * yrange
        loc_yaxis_y = np.cos(angle) * yrange
        loc_yaxis_z = 0.0

        xmax = loc_xaxis_x
        ymax = loc_yaxis_x

        loc_zaxis_x = 0.0
        loc_zaxis_y = 0.0
        loc_zaxis_z = zrange
    elif space_flag == 5:  # rotated in XY plane, 3D grid
        # UNPACKED SPACE STRUCTURE:
        # XPIVOT, YPIVOT, XRANGE, YRANGE, ANGLE-RADS, ZMIN, ZMAX
        buffer_count_end = buffer_count_start + 56
        xmin = xmax = ymin = ymax = None
        _unpacked_space = unpack(">7d", buffer[buffer_count_start:buffer_count_end])
        assert len(_unpacked_space) == 7
        xpivot, ypivot, xrange, yrange, angle, zmin, zmax = _unpacked_space
        zrange = abs(zmax - zmin)
        zpivot = zmin
        loc_xaxis_x = np.cos(angle) * xrange
        loc_xaxis_y = -np.sin(angle) * xrange
        loc_xaxis_z = 0.0

        loc_yaxis_x = np.sin(angle) * yrange
        loc_yaxis_y = np.cos(angle) * yrange
        loc_yaxis_z = 0.0

        loc_zaxis_x = 0.0
        loc_zaxis_y = 0.0
        loc_zaxis_z = zrange
    elif space_flag == 8:  # Rotated in 3D - currently invalid
        # UNPACKED SPACE STRUCTURE:
        #     XPIVOT, YPIVOT, ZPIVOT,
        #     LOC_X_AX_x, LOC_X_AX_y, LOC_X_AX_z,
        #     LOC_Y_AX_x, LOC_Y_AX_y, LOC_Y_AX_z,
        #     LOC_Z_AX_x, LOC_Z_AX_y, LOC_Z_AX_z
        # Add double lengths
        buffer_count_end = buffer_count_start + 96
        _unpacked_space = unpack(">12d", buffer[buffer_count_start:buffer_count_end])
        xmin = xmax = ymin = ymax = zmin = zmax = None  # type: ignore
        assert len(_unpacked_space) == 12
        """
        ==================
        UNPACKING VERSIONS
        ==================
        ----
        FULL
        ----
        ```
        (
            xpivot,
            ypivot,
            zpivot,
            loc_xaxis_x,
            loc_xaxis_y,
            loc_xaxis_z,
            loc_yaxis_x,
            loc_yaxis_y,
            loc_yaxis_z,
            loc_zaxis_x,
            loc_zaxis_y,
            loc_zaxis_z,
        ) = _unpacked_space
        ```
        -------
        CHUNKED
        -------
        ```
        pivot, loc_xaxis, loc_yaxis, loc_zaxis = [
            _unpacked_space[(i * 3) : (i * 3) + 3] for i in range(4)
        ]
        xpivot, ypivot, zpivot = pivot
        loc_xaxis_x, loc_xaxis_y, loc_xaxis_z = loc_xaxis
        loc_yaxis_x, loc_yaxis_y, loc_yaxis_z = loc_yaxis
        loc_zaxis_x, loc_zaxis_y, loc_zaxis_z = loc_zaxis
        ```
        """
        (
            xpivot,
            ypivot,
            zpivot,
            loc_xaxis_x,
            loc_xaxis_y,
            loc_xaxis_z,
            loc_yaxis_x,
            loc_yaxis_y,
            loc_yaxis_z,
            loc_zaxis_x,
            loc_zaxis_y,
            loc_zaxis_z,
        ) = _unpacked_space
        xrange = 0
        yrange = 0
        zrange = 0
    else:
        raise ValueError(f"Invalid grid space: {space_flag!s}")

    is_2d = space_flag == 4 or space_flag == 1
    # new style grid header
    # Get projection information:
    buffer_count_start = buffer_count_end
    buffer_count_end = buffer_count_start + 4  # add integer length
    projection, *_rest = unpack(">i", buffer[buffer_count_start:buffer_count_end])
    zone = 0
    if projection != -1:
        # zone
        buffer_count_start = buffer_count_end

        b2len = calcsize(">ii") + (15 * calcsize("d"))
        buffer_count_end += b2len
        buff2 = buffer[buffer_count_start : buffer_count_start + b2len]

        zone, ellipsoid, *proj_parms = unpack(">ii" + "15d", buff2)

    # XY units
    buffer_count_start = buffer_count_end
    buffer_count_end = buffer_count_start + calcsize("i")  # Add Integer length
    xyunits = unpack(">i", buffer[buffer_count_start:buffer_count_end])[0]

    # Z units and downward
    buffer_count_start = buffer_count_end
    buffer_count_end = buffer_count_start + calcsize("i")  # Add Integer length
    zunits = unpack(">i", buffer[buffer_count_start:buffer_count_end])[0]
    downward = False
    if zunits > 4096:
        zunits -= 4096
        downward = True
    # Get Zdatum Above MSL information:
    buffer_count_start = buffer_count_end
    buffer_count_end = buffer_count_start + calcsize("d")  # Add double length

    msl = 1.0e20
    try:
        msl = unpack(">d", buffer[buffer_count_start:buffer_count_end])[0]
        if msl > 1.0e20:
            msl = 1.0e20
    except struct_error as se:
        log.debug(
            "Error unpacking MSL datum from space bytes: {} -- buffer length: {}",
            se,
            len(buffer),
        )

    return {
        # space meta data
        "space_version": space_version,
        "space_flag": space_flag,
        # min/max vals
        "xmin": xmin,
        "xmax": xmax,
        "ymin": ymin,
        "ymax": ymax,
        "zmin": zmin,
        "zmax": zmax,
        # rotation angle; default is 0.0
        "angle": angle,
        # range
        "xrange": xrange,
        "yrange": yrange,
        "zrange": zrange,
        # units
        "xyunits": xyunits,
        "zunits": zunits,
        "downward": downward,
        "msl": msl,
        # pivot
        "xpivot": xpivot,
        "ypivot": ypivot,
        "zpivot": zpivot,
        # local x axis
        "loc_xaxis_x": loc_xaxis_x,
        "loc_xaxis_y": loc_xaxis_y,
        "loc_xaxis_z": loc_xaxis_z,
        # local y axis
        "loc_yaxis_x": loc_yaxis_x,
        "loc_yaxis_y": loc_yaxis_y,
        "loc_yaxis_z": loc_yaxis_z,
        # local z axis
        "loc_zaxis_x": loc_zaxis_x,
        "loc_zaxis_y": loc_zaxis_y,
        "loc_zaxis_z": loc_zaxis_z,
        # misc
        "is_2d": is_2d,
        "projection": projection,
        "zone": zone,
        "ellipsoid": ellipsoid,
        "proj_parms": proj_parms,
    }
