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
"""rasterio library tools"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import rasterio as rio

try:
    HAS_RASTERIO = True
except ImportError:
    HAS_RASTERIO = False


__all__ = ("HAS_RASTERIO", "rio_info_dictionary", "rio_profile_dictionary")


def rio_profile_dictionary(dataset: rio.DatasetReader) -> dict[str, Any]:
    return dict(dataset.profile)


def rio_info_dictionary(dataset: rio.DatasetReader) -> dict[str, Any]:
    return {
        **rio_profile_dictionary(dataset),
        "bounds": dataset.bounds,
        "colorinterp": [c.name for c in dataset.colorinterp],
        "count": dataset.count,
        "crs": dataset.crs.to_string(),
        "descriptions": dataset.descriptions,
        "driver": dataset.driver,
        "dtype": dataset.dtypes[0],
        "height": dataset.height,
        "indexes": dataset.indexes,
        "lnglat": dataset.lnglat(),
        "mask_flags": [[f.name for f in m] for m in dataset.mask_flag_enums],
        "res": dataset.res,
        "shape": dataset.shape,
        "transform": dataset.transform.to_gdal(),
    }
