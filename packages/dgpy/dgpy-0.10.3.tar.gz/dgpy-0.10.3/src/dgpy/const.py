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
"""dgpy.const ~ constants (tho nothing in python is really constant)"""

from __future__ import annotations

from typing import Final

__all__ = (
    "DGI_ENV_VARS",
    "DGPY_PORT",
    "MAX_8BIT_VAL",
    "MAX_16BIT_VAL",
    "NAN_8BIT_VAL",
    "NAN_16BIT_VAL",
)

NAN_16BIT_VAL: Final[int] = (1 << 16) - 1  # 65535
"""NaN 16 bit value"""
MAX_16BIT_VAL: Final[int] = (1 << 16) - 2  # 65534
"""Max 16 bit value"""
NAN_8BIT_VAL: Final[int] = (1 << 8) - 1  # 255
"""NaN 8 bit value"""
MAX_8BIT_VAL: Final[int] = (1 << 8) - 2  # 254
"""MAX 8 bit value"""
DGPY_PORT: Final[int] = 3479
"""DGPY port (it spells out 'dgpy' on a numpad)"""

# COLORS
DGI_PURPLE_HEX: Final[str] = "644692"
"""DGI purple hex color code"""
DGI_PURPLE_RGB: Final[tuple[int, int, int]] = (100, 70, 146)
"""DGI purple RGB color values"""
DGI_TEAL_HEX: Final[str] = "0e6c66"
"""DGI teal hex color code"""
DGI_TEAL_RBG: Final[tuple[int, int, int]] = (14, 108, 102)
"""DGI teal RGB color values"""
DGI_ENV_VARS = {"cv": "COVIZHOME", "ev": "EVHOME", "wa": "WAHOME"}

PG_DEFAULT_PORT: Final[int] = 5432
"""Postgres default port"""
MYSQL_DEFAULT_PORT: Final[int] = 3306
"""Mysql default port"""
REDIS_DEFAULT_PORT: Final[int] = 6379
"""Redis default port"""
