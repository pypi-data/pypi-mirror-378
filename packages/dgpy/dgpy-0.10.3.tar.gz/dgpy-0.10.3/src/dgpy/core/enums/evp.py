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
"""Projection enum"""

from __future__ import annotations

from enum import IntEnum

__all__ = ("Evp",)


class Evp(IntEnum):
    """Projection enum used by geospace"""

    Evp_unknown = -2
    Evp_LocalRect = -1
    Evp_Geographic = 0
    Evp_UTM = 1
    Evp_StatePlane = 2
    Evp_Albers = 3
    Evp_Lambert = 4
    Evp_Mercator = 5
    Evp_PolarStereo = 6
    Evp_Polyconic = 7
    Evp_TransverseMercator = 9
    Evp_LambertAzimuthalEqualArea = 11
    Evp_ObliqueMercator = 20
    Evp_Amersfoort = 21
    Evp_NewAmersfoort = 22
    Evp_Cassini = 23
    Evp_LambertTangential = 24
    Evp_RectifiedSkewOrthomorphic = 25
    Evp_AzimuthalEquidistant = 26
    Evp_ObliqueStereo = 27

    unknown = -2
    LocalRect = -1
    Geographic = 0
    UTM = 1
    StatePlane = 2
    Albers = 3
    Lambert = 4
    Mercator = 5
    PolarStereo = 6
    Polyconic = 7
    TransverseMercator = 9
    LambertAzimuthalEqualArea = 11
    ObliqueMercator = 20
    Amersfoort = 21
    NewAmersfoort = 22
    Cassini = 23
    LambertTangential = 24
    RectifiedSkewOrthomorphic = 25
    AzimuthalEquidistant = 26
    ObliqueStereo = 27
