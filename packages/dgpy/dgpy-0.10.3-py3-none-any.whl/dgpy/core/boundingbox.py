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
"""BoundingBox object"""

from __future__ import annotations

from pydantic import Field

from dgpy.dgpydantic import DgpyBaseModel


class BoundingBox(DgpyBaseModel):
    """Object representation of a BoundingBox

    A bounding box has a min and max value for x, y and z
    """

    xmin: float = Field(..., title="xmin")
    xmax: float = Field(..., title="xmax")
    ymin: float = Field(..., title="ymin")
    ymax: float = Field(..., title="ymax")
    zmin: float = Field(..., title="zmin")
    zmax: float = Field(..., title="zmax")

    @property
    def xminboundingbox(self) -> float:
        return self.xmin

    @property
    def xmaxboundingbox(self) -> float:
        return self.xmax

    @property
    def yminboundingbox(self) -> float:
        return self.ymin

    @property
    def ymaxboundingbox(self) -> float:
        return self.ymax

    @property
    def zminboundingbox(self) -> float:
        return self.zmin

    @property
    def zmaxboundingbox(self) -> float:
        return self.zmax
