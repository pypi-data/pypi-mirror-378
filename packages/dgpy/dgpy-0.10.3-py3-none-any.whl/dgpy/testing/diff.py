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
"""Testing diff utils for dgpy"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from jsonbourne import JSON
from pydantic import Field

from dgpy.dgpydantic import DgpyBaseModel
from dgpy.testing.cmp import cmp_arr, cmp_set

if TYPE_CHECKING:
    from dgpy.core.py2grd import Py2grd, Py2grdHeader
    from dgpy.core.py3grd import Py3grd

_T = TypeVar("_T")


class DgpyDiff(DgpyBaseModel):
    equal: bool
    equiv: bool
    diff: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_json(cls, json_string: bytes | str) -> DgpyDiff:
        """Return a `DgpyDiff` object from a JSON string"""
        return cls(**JSON.loads(json_string))


def diff_sets(left: set[_T], right: set[_T]) -> dict[str, set[_T]]:
    """Diff python sets"""
    common, left_only, right_only = cmp_set(left, right)
    return {"common": common, "left_only": left_only, "right_only": right_only}


def diff_py3grd(a_py3grd: Py3grd, b_py3grd: Py3grd) -> DgpyDiff:
    _arr_diff = cmp_arr(a_py3grd.array_values, b_py3grd.array_values)
    return _arr_diff


def diff_py2grd_header(a: Py2grdHeader, b: Py2grdHeader) -> bool:
    if a == b:
        return True
    return False


def diff_py2grd(a_py2grd: Py2grd, b_py2grd: Py2grd) -> DgpyDiff:
    _arr_diff = cmp_arr(a_py2grd.array_values, b_py2grd.array_values)
    return _arr_diff
