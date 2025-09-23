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
"""Testing utils for the Pydat"""

from __future__ import annotations

from typing import Any

from dgpy.ex import DgpyError
from dgpy.pydat import Pydat, PydatHeader
from dgpy.testing.cmp import cmp_set


def cmp_pydat_columns(left: Pydat, right: Pydat) -> tuple[set[str], set[str], set[str]]:
    """Compare the columns of a pydat

    Args:
        left: pydat
        right: pydat

    Returns:
        Tuple of the form: (common-cols, left-only-cols, right-only-cols)

    """
    left_columns = set(left.columns.values)
    right_columns = set(right.columns.values)
    common_cols, left_only_cols, right_only_cols = cmp_set(left_columns, right_columns)
    if len(left_only_cols) == 0 and len(right_only_cols) == 0:
        return common_cols, left_only_cols, right_only_cols
    raise DgpyError(
        msg="Column mismatch",
        info={"left_only_columns": list(left), "right_only_columns": list(right)},
    )


def cmp_pydat(left: Pydat, right: Pydat) -> bool:
    """Compare two pydat objects

    Args:
        left: pydat object
        right: pydat object

    Returns:
        True or False

    """
    left_df = left
    right_df = right
    if isinstance(left, Pydat):
        left_df = left.df
    if isinstance(right, Pydat):
        right_df = right.df
    common_cols_set, left_only, right_only = cmp_pydat_columns(left=left, right=right)
    common_cols = list(common_cols_set)
    _common_cols_a_order = [col for col in left.columns if col in common_cols]
    merged = left_df.merge(right_df, indicator=True, how="outer")
    right_only = (
        merged[merged["_merge"] == "right_only"]
        .sort_values(_common_cols_a_order)[_common_cols_a_order]
        .reset_index(drop=True)
    )
    left_only = (
        merged[merged["_merge"] == "left_only"]
        .sort_values(_common_cols_a_order)[_common_cols_a_order]
        .reset_index(drop=True)
    )
    if not (merged["_merge"] == "both").all():
        raise DgpyError(
            info={
                "left_only_rows_pydat": sorted([
                    tuple(row.tolist()) for row in left_only.values
                ]),
                "right_only_rows_pydat": sorted([
                    tuple(row.tolist()) for row in right_only.values
                ]),
            }
        )
    return True


def diff_header_values(
    key: str, left_value: list | str, right_value: list | str
) -> dict[str, Any | bool]:
    _equal = left_value == right_value or str(left_value) == str(right_value)
    left_val_str = str(left_value)
    right_val_str = str(right_value)
    if key == "desc":
        _equiv = left_val_str.replace("\n", "") == right_val_str.replace("\n", "")
    else:
        _equiv = _equal
    return {
        "left": left_value,
        "right": right_value,
        "eq": _equal,
        "equiv": _equiv,
    }


def diff_headers(
    left: PydatHeader,
    right: PydatHeader,
    *,
    ignore_keys: set[str] | tuple[str, ...] | list[str] | None = None,
    ignore_units: bool = False,
    ignore_ditto: bool = False,
    equiv: bool = False,
) -> dict[str, Any]:
    left_filtered = left
    right_filtered = right
    if ignore_units:
        left_filtered = left_filtered.units_ignored()
        right_filtered = right_filtered.units_ignored()
    if ignore_keys is None:
        ignore_keys = []
        todiff_header_keys = (k for k in left_filtered.model_dump().keys())
    else:
        todiff_header_keys = (
            k for k in left_filtered.model_dump().keys() if k not in ignore_keys
        )
    _other_keys = set(left_filtered.model_dump().keys())
    _self_keys = set(right_filtered.model_dump().keys())
    common, left_only, right_only = cmp_set(_other_keys, _self_keys)
    diffdata: dict[str, Any] = {}
    if left_only or right_only:
        diffdata["keys"] = {
            "common": sorted(common),
            "left_only": sorted(left_only),
            "right_only": sorted(right_only),
        }
    for k in todiff_header_keys:
        a_val = left_filtered.model_dump()[k]
        b_val = right_filtered.model_dump()[k]
        if ignore_ditto and k == "dfields":
            a_val = [{**f, "units": "ignored", "ditto": False} for f in a_val]
            b_val = [{**f, "units": "ignored", "ditto": False} for f in b_val]
        _val_diff = diff_header_values(k, a_val, b_val)
        if equiv:
            if not _val_diff["equiv"]:
                diffdata[k] = _val_diff

        else:
            if not _val_diff["equal"]:
                diffdata[k] = _val_diff
    return diffdata
