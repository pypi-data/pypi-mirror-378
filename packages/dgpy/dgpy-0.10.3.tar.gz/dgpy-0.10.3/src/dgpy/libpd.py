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
"""dgpy pandas tools"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pandas as pd

if TYPE_CHECKING:
    from typing import TypeGuard


def is_series(obj: Any) -> TypeGuard[pd.Series]:
    """Return True if obj `isinstance` of `pandas.Series`"""
    return isinstance(obj, pd.Series)


def is_dataframe(obj: Any) -> TypeGuard[pd.DataFrame]:
    """Return True if obj `isinstance` of `pandas.DataFrame`"""
    return isinstance(obj, pd.DataFrame)


def is_multindex(obj: Any) -> TypeGuard[pd.MultiIndex]:
    """Return True if obj `isinstance` of `pandas.MultiIndex`"""
    return isinstance(obj, pd.MultiIndex)


def assert_series(obj: Any) -> None:
    """Assert obj `isinstance` of `pandas.Series`"""
    if not is_series(obj):
        raise TypeError(f"Expected pandas.Series, got {type(obj)}")


def assert_dataframe(obj: Any) -> None:
    """Assert obj `isinstance` of `pandas.DataFrame`"""
    if not is_dataframe(obj):
        raise TypeError(f"Expected pandas.DataFrame, got {type(obj)}")


def assert_multindex(obj: Any) -> None:
    """Assert obj `isinstance` of `pandas.MultiIndex`"""
    if not is_multindex(obj):
        raise TypeError(f"Expected pandas.MultiIndex, got {type(obj)}")
