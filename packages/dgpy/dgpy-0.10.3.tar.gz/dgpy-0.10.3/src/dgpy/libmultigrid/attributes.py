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
"""multigrid attribute(s)"""

from __future__ import annotations

from typing import Any

from pydantic import ConfigDict, Field, field_validator

from dgpy.dgpydantic import DgpyBaseModel


class AttributeDump(DgpyBaseModel):
    name: str = Field(..., description="Attribute name")
    units: str = Field(..., description="Attribute units")
    temporal: bool = Field(False, description="Is this attribute temporal?")
    model_config = ConfigDict(extra="ignore")

    @classmethod
    def from_hdf5_dictionary(cls, data: Any) -> AttributeDump:
        """Return an Attribute object from a dictionary"""
        if "unit" in data and "units" not in data:
            data["units"] = data.pop("unit")
        if data["units"] in ("feet", "meters") and data["name"] != "z":
            data["type"] = "numeric"
        return cls.model_validate(data)


class AttributeTimestep(DgpyBaseModel):
    key: str = Field(..., description="hdf5 key")


class Attribute(DgpyBaseModel):
    key: str = Field(..., description="hdf5 key")

    name: str = Field(..., description="Attribute name")
    units: str = Field(..., description="Attribute units")

    temporal: bool = Field(False, description="Is this attribute temporal?")
    type: str = Field("property", description="Attribute type")

    time_steps: list[str] = Field([], description="Time steps")

    # TODO - add support for overviews
    overviews: list[str] | None = Field(None, description="Overviews")

    # Optional Fields
    color_file: str | None = Field(None, description="Color file")
    color_priority: int | None = Field(None, description="Color priority")
    description: str | None = Field(None, description="Attribute description")
    uses_lut: bool = Field(False, description="Attribute uses a look-up-table")

    @field_validator("type", mode="before")
    @classmethod
    def _validate_type(cls, v: Any) -> Any:
        if isinstance(v, str):
            if v == "k":
                return "spatial"
            if v == "numeric":
                return "property"
        return v

    @classmethod
    def from_hdf5_dictionary(cls, data: Any) -> Attribute:
        """Return an Attribute object from a dictionary"""
        if "unit" in data and "units" not in data:
            data["units"] = data.pop("unit")
        return cls.model_validate(data)

    def to_attribute_dump(self) -> AttributeDump:
        """Return a DumpAttribute object"""
        return AttributeDump(
            name=self.name,
            units=self.units,
            temporal=self.temporal,
        )

    def __getattribute__(self, name: str) -> Any:
        return super().__getattribute__(name)

    def __setattr__(self, name: str, value: Any) -> None:
        return super().__setattr__(name, value)
