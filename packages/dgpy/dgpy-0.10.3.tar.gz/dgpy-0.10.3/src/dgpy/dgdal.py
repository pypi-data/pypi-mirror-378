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
"""Module Docstring"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dataclasses import dataclass
else:
    from pydantic.dataclasses import dataclass

try:
    from osgeo import gdal
except ImportError:
    from warnings import warn

    warn("GDAL is not installed", stacklevel=1)

__all__ = ("gdal_drivers",)


@dataclass
class GdalDriver:
    """GDAL Driver"""

    short_name: str
    long_name: str
    metadata: dict[str, str]


def gdal_drivers() -> dict[str, GdalDriver]:
    """Return a list of GDAL drivers"""
    return {
        driver.ShortName: GdalDriver(
            short_name=driver.ShortName,
            long_name=driver.LongName,
            metadata=driver.GetMetadata(),
        )
        for driver in [gdal.GetDriver(i) for i in range(gdal.GetDriverCount())]
    }
