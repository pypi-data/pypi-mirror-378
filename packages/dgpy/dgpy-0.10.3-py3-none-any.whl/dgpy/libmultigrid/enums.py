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
"""lib-multigrid dgpy"""

from __future__ import annotations

from enum import Enum


class TimestepPrecision(str, Enum):
    ms = "ms"
    second = "second"
    day = "day"
    minute = "minute"

    @staticmethod
    def is_timestep_precision(value: str) -> bool:
        """Return True if value is a valid TimestepPrecision"""
        return value in TimestepPrecision.__members__.values()

    @staticmethod
    def as_timestep_precision(value: str) -> TimestepPrecision:
        """Return TimestepPrecision enum value"""
        if not TimestepPrecision.is_timestep_precision(value):
            raise ValueError(f"Invalid TimestepPrecision: {value}")
        return TimestepPrecision(value)


class MultigridAttributeType(str, Enum):
    """Multigrid attribute types"""

    k = "k"
    spatial = "spatial"
    numeric = "numeric"
    discrete = "discrete"
    seismic = "seismic"
    property = "property"

    @staticmethod
    def is_multigrid_attribute_type(value: str) -> bool:
        """Return True if value is a valid MultigridAttributeType"""
        return value in MultigridAttributeType.__members__.values()
