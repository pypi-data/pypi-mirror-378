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
"""Ellipsoid enum"""

from __future__ import annotations

from enum import IntEnum

__all__ = ("Eve",)


class Eve(IntEnum):
    """Elipsoid enum ~ Eve"""

    Eve_unknown = -1
    Eve_Clarke_1866 = 0
    Eve_Bessel_1841 = 1
    Eve_Airy_1830 = 2
    Eve_Everest_1830 = 3
    Eve_Clarke_1880 = 4
    Eve_HayfordIntl_1924 = 5
    Eve_Krasovsky_1940 = 6
    Eve_Australian_1965 = 7
    Eve_WGS_1972 = 8
    Eve_GRS_1980 = 9
    Eve_userDefined = 10
    Eve_WGS_1984 = 11
    Eve_AiryModified_1849 = 12
    Eve_Indonesian_Natl = 13
    Eve_GRS_1967 = 14
    Eve_Helmert_1906 = 15
    Eve_Everest_1830_1967 = 16
    Eve_Clarke_1880_IGN = 17
    Eve_Everest_1830_1975 = 18
    Eve_Everest_1830_Modified = 19
    Eve_Everest_1830_1962 = 20
    Eve_GRS_1967_2dp_Flattening = 21
    Eve_Clarke_1880_RGS = 22
    Eve_Clarke_1880_Benoit = 23
    Eve_Xian_1980 = 24
    Eve_Clarke_1866_Authalic_Sphere = 25

    unknown = -1
    Clarke_1866 = 0
    Bessel_1841 = 1
    Airy_1830 = 2
    Everest_1830 = 3
    Clarke_1880 = 4
    HayfordIntl_1924 = 5
    Krasovsky_1940 = 6
    Australian_1965 = 7
    WGS_1972 = 8
    GRS_1980 = 9
    userDefined = 10
    WGS_1984 = 11
    AiryModified_1849 = 12
    Indonesian_Natl = 13
    GRS_1967 = 14
    Helmert_1906 = 15
    Everest_1830_1967 = 16
    Clarke_1880_IGN = 17
    Everest_1830_1975 = 18
    Everest_1830_Modified = 19
    Everest_1830_1962 = 20
    GRS_1967_2dp_Flattening = 21
    Clarke_1880_RGS = 22
    Clarke_1880_Benoit = 23
    Xian_1980 = 24
    Clarke_1866_Authalic_Sphere = 25
