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
"""dgpy xarray lib tools"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import xarray as xr

if TYPE_CHECKING:
    from typing import TypeGuard


def is_dataarray(obj: Any) -> TypeGuard[xr.DataArray]:
    """Return True if obj `isinstance` of `xarray.DataArray`"""
    return isinstance(obj, xr.DataArray)


def is_dataset(obj: Any) -> TypeGuard[xr.Dataset]:
    """Return True if obj `isinstance` of `xarray.Dataset`"""
    return isinstance(obj, xr.Dataset)


def assert_dataarray(obj: Any) -> None:
    """Assert obj `isinstance` of `xarray.DataArray`"""
    if not is_dataarray(obj):
        raise TypeError(f"Expected xarray.DataArray, got {type(obj)}")


def assert_dataset(obj: Any) -> None:
    """Assert obj `isinstance` of `xarray.Dataset`"""
    if not is_dataset(obj):
        raise TypeError(f"Expected xarray.Dataset, got {type(obj)}")
