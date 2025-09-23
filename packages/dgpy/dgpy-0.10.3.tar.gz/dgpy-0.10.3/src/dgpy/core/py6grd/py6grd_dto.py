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
"""Py2grd/Py3grd DTO (Data Transfer Object)"""

from __future__ import annotations

from typing import Annotated, Any, Final

from pydantic import (
    BeforeValidator,
    Field,
    field_validator,
)

from dgpy.core.enums import evu_validate
from dgpy.core.py6grd.evg import EvgNodeType
from dgpy.core.pyspace import PySpace, TProjParms
from dgpy.core.validators import _empty_string_if_none
from dgpy.dgpydantic import DgpyBaseModel
from dgpy.xtypes import Arr

_DEFAULT_CLAMP: Final[tuple[float, float]] = (
    1.0000000200408773e20,
    1.0000000200408773e20,
)


class PygrdHeaderDTO(DgpyBaseModel):
    """Py2grd/Py3grd Data Transfer Object"""

    xcol: int = 0
    yrow: int = 0
    zlev: int = 1

    xmin: float | None = None
    xmax: float | None = None
    ymin: float | None = None
    ymax: float | None = None
    zmin: float | None = None
    zmax: float | None = None

    space: PySpace | None = None

    property_node: int = EvgNodeType.standard
    nulls_in_grid: int | None = None

    geometry: int = 0
    is_bordered: bool = False
    dims: list[str] = Field(default_factory=list)

    node_range: tuple[float, float] = (0.0, 0.0)
    vfault: str | None = None
    nvfault: str | None = None
    vf: tuple[int, ...] | None = None
    nvf: tuple[int, ...] | None = None
    msl: float | None = None
    clamp: tuple[float, float] | None = _DEFAULT_CLAMP
    z_influence: float | None = None
    angle: float = 0.0
    fspath: str | None = None

    alias: str | None = ""
    date: str | None = None
    punits: Annotated[str | None, BeforeValidator(evu_validate)] = "unknown"
    punits_string: str | None = "unknown"

    xyunits: Annotated[str | None, BeforeValidator(evu_validate)] = "unknown"
    zunits: Annotated[str | None, BeforeValidator(evu_validate)] = "unknown"

    coordinate_system_id: str = ""
    coordinate_system_name: str = ""
    desc: str = ""
    downward: bool = False
    dat: str = ""
    history: list[str] = Field(default_factory=list)
    p_field: str = "p"
    field: str = "p"
    pclip: tuple[float, float] = (0.0, 0.0)
    clip_poly: str | None = None
    bpoly: str | None = None

    # Array o' data related
    bit_factor: float = 1.0  # default factor is 1 b/c default is arr as is
    bit_shift: float = 0.0  # default shift is 0 b/c default has no shift

    # 2grd
    projection: str | int | None = None
    zone: int | None = None
    proj_parms: TProjParms | None = None
    rotation: float | None = None

    # trend related
    trend_coefficients: tuple[int, ...] | None = None
    trend_offsets: tuple[int, ...] | None = None
    trend_order: Any = None
    data_order: int | None = None

    version: int | None = 80
    seismic_line_and_trace_labels: tuple[int, ...] | None = None
    values_32: Arr | None = Field(default=None)
    values_16: Arr | None = Field(default=None)
    values_8: Arr | None = Field(default=None)

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

    padding: int | None = None

    RESERVED: bytes | None = None

    def nparr(self) -> Arr:
        if self.values_32 is None:
            raise ValueError("Grid DTO values is None")
        return self.values_32

    def values(self) -> Arr:
        return self.nparr()

    def ensure_space_2d(self) -> bool:
        """Ensure that DTO has pyspace object"""
        if self.space:
            return True
        if self.angle == 0:
            if self.xmax and self.xmin and self.ymax and self.ymin:
                xrange = abs(self.xmax - self.xmin)
                yrange = abs(self.ymax - self.ymin)
                self.space = PySpace(
                    xpivot=self.xmin,
                    ypivot=self.ymin,
                    zpivot=0.0,
                    # x axis
                    loc_xaxis_x=xrange,
                    loc_xaxis_y=0.0,
                    loc_xaxis_z=0.0,
                    # y axis
                    loc_yaxis_x=0.0,
                    loc_yaxis_y=yrange,
                    loc_yaxis_z=0.0,
                    # z axis
                    loc_zaxis_x=0.0,
                    loc_zaxis_y=0.0,
                    loc_zaxis_z=1.0,
                    coordinate_system_id=self.coordinate_system_id,
                    coordinate_system_name=self.coordinate_system_name,
                    downward=self.downward,
                    # TODO: add projection typing
                    projection=self.projection,
                    proj_parms=self.proj_parms,
                    zone=self.zone,
                    xyunits=self.xyunits or "unknown",
                    zunits=self.zunits or "unknown",
                    space_flag=1,
                    is_2d=True,
                )
                return True
        raise ValueError("Unable to determine geo-space")

    def update_space(self) -> None:
        """Update the space object"""
        if self.space is None:
            raise ValueError("Space is not defined")
        if self.msl and not self.space.msl:
            self.space.msl = self.msl
        if self.xyunits and not self.space.xyunits:
            self.space.xyunits = self.xyunits
        if self.zunits and not self.space.zunits:
            self.space.zunits = self.zunits

    @field_validator(
        "coordinate_system_id",
        "coordinate_system_name",
        "alias",
    )
    @classmethod
    def validate_empty_string_if_none(cls, value: Any) -> Any:
        """Validate that the value is an empty string if None"""
        _empty_string_if_none(value)
        if value is None:
            return ""
        return value

    def py2grd_data_dict(self) -> dict[str, Any]:
        return self.model_dump(
            exclude={
                "seismic_line_and_trace_labels",
                "values_32",
                "values_16",
                "values_8",
                "dims",
                "clamp",
                "p_field",
                "punits_string",
                "z_influence",
                "xmin",
                "xmax",
                "ymin",
                "ymax",
                "zmin",
                "zmax",
                "xyunits",
                "zunits",
                "msl",
                "zone",
                "projection",
                "proj_parms",
                "RESERVED",
                "xform_type",
                "xform_top",
                "xform_bottom",
                "xform_top_shift",
                "xform_bottom_shift",
                "xform_top_percent",
                "xform_bottom_percent",
                "xform_bottom_grid",
                "xform_x_spacing",
                "xform_z_spacing",
                "xform_divider",
                "rotation",
                "coordinate_system_id",
                "coordinate_system_name",
            }
        )

    def py3grd_data_dict(self) -> dict[str, Any]:
        return self.model_dump(
            exclude={
                "msl",
                "proj_parms",
                "projection",
                "zone",
                "xyunits",
                "zunits",
                "values_32",
                "values_16",
                "values_8",
                "dims",
                "vfault",
                "nvfault",
                "vf",
                "nvf",
                "xmin",
                "xmax",
                "ymin",
                "ymax",
                "zmin",
                "zmax",
                "RESERVED",
                "rotation",
                "coordinate_system_id",
                "coordinate_system_name",
            },
        )
