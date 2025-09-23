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
"""cellgrid"""

from __future__ import annotations

from pydantic import Field

from dgpy.dgpydantic import DgpyBaseModel


class SpaceCorner(DgpyBaseModel):
    """Space corner data model"""

    x: float
    y: float
    z: float


class Pyc3grdAttribute(DgpyBaseModel):
    """Pyc3grd attribute data model"""

    min: float
    max: float
    name: str
    num_null: int
    num_values: int
    units: str | None = None


class DynamicAttribute(Pyc3grdAttribute):
    """Dynamic attribute data model"""

    ...


class StaticAttribute(Pyc3grdAttribute):
    """Static attribute data model"""

    ...


class DiscreteAttribute(DgpyBaseModel):
    """Discrete attribute data model"""

    min: float
    max: float
    name: str


class StringAttribute(DgpyBaseModel):
    """String attribute data model"""

    labels: set[str] = Field(default_factory=set)
    name: str


class Lgrs(DgpyBaseModel):
    """LGR data model"""

    imax: int
    imin: int
    jmax: int
    jmin: int
    kmax: int
    kmin: int
    name: str


class Pyc3grdDump(DgpyBaseModel):
    """Cellgrid dump data model"""

    coordinate_system_id: str | None = None
    description: str = ""
    active_ratio_of_total: float
    cells_right_handed: bool
    directory: str
    file_version: float
    filename: str
    dynamic_attributes: list[DynamicAttribute] = Field(default=[])
    history: list[str] | str = Field(default=[])
    grid_right_handed: bool
    icols: int
    inactive_ratio_of_total: float
    jrows: int
    klayers: int
    name: str
    num_active_cells: int
    num_inactive_cells: int
    sliced: bool = False
    space_corners: list[SpaceCorner] = Field(default_factory=list)
    xyunits: str
    zunits: str
    lgrs: list[Lgrs] = Field(default_factory=list)

    discrete_attributes: list[DiscreteAttribute] = Field(default_factory=list)
    string_attributes: list[StringAttribute] = Field(default_factory=list)
    static_attributes: list[StaticAttribute] = Field(default_factory=list)
    timesteps: list[str] = Field(default_factory=list)
    cell_filename: str | None = None

    elevation_above_msl: float | None = Field(None, alias="elevation_above_MSL")

    parent_filename: str | None = None
    parent_name: str | None = None
