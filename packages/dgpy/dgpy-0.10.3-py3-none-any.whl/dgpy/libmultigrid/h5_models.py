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
"""lib-multigrid models as stored in HDF5 files"""

from __future__ import annotations

from dgpy.dgpydantic import DgpyBaseModel

__all__ = (
    "AttrPropertyInfo",
    "CsXy",
    "CsZ",
    "MetaGeneral",
    "MetaM2grd",
    "MetaM3grd",
    "MetaM6grd",
)


class CsXy(DgpyBaseModel):
    id: str = "LCS1D3"
    unit: str


class CsZ(DgpyBaseModel):
    unit: str
    datum: float | None = None


class MetaGeneral(DgpyBaseModel):
    history: str
    type: str
    description: str = ""


class MetaM6grd(DgpyBaseModel):
    """Multigrid metadata for `/meta/m2grd` or `/meta/m3grd`"""

    oldest_compatible_software_version: int
    version: int


class MetaM2grd(MetaM6grd):
    """Multigrid metadata `/meta/m2grd`"""

    ...


class MetaM3grd(MetaM6grd):
    """Multigrid metadata `/meta/m3grd`"""

    ...


class AttrPropertyInfo(DgpyBaseModel):
    max: float
    min: float
    null_count: int = 0
    null_value: float = float("inf")
