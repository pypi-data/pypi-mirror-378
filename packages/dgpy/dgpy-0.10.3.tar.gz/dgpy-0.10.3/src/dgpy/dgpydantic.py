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
"""dgpydantic = dgpy + pydantic"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict

__all__ = ("DgpyBaseModel", "StringEnum")


class DgpyBaseModel(BaseModel):
    """Base object for dgpy. Allows for adding methods to all pydantic models under DGPY/Sheldon."""

    def __str__(self) -> str:
        """Return a string representation of the model."""
        return f"{self.__repr_name__()}({self.__repr_str__(', ')})"  # type: ignore[misc]

    model_config = ConfigDict(
        extra="forbid",
        arbitrary_types_allowed=True,
        populate_by_name=True,
        use_enum_values=True,
        validate_default=True,
    )


class StringEnum(str, Enum):
    """String enum base class -- based on usage with pydantic"""
