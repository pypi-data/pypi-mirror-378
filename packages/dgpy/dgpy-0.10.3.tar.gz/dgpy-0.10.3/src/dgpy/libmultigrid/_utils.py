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
"""lib-multigrid utils"""

from __future__ import annotations

import datetime
import re

from typing import Any

_MATCH_DATETIME_PATTERN = re.compile(
    r"(\w+)/(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3})"
)


def get_datetime_precision(level: str, timestamp: str) -> str:
    if level == "ms":
        return timestamp
    elif level == "second":
        return timestamp[:19]
    elif level == "day":
        return timestamp[:10]
    elif level == "minute":
        return timestamp[:16]
    raise ValueError(
        f"Invalid datetime precision level: {level} (must be 'ms', 'second' or 'day')"
    )


def match_datetimes(
    attrs_dict: dict[str, dict[str, Any]],
) -> tuple[set[str], list[str]]:
    timestep_properties: set[str] = set()
    time_steps: set[str] = set()
    for item in attrs_dict.keys():
        if "precision" in attrs_dict[item].keys():
            precision_level = attrs_dict[item]["precision"]
            for match in _MATCH_DATETIME_PATTERN.findall(item):
                timestep_properties.add(match[0])
                match_day = match[1][:10]
                time_steps_days = [j[1][:10] for j in time_steps]
                if match_day not in time_steps_days:
                    time_steps.add(get_datetime_precision(precision_level, match[1]))

    return timestep_properties, sorted(time_steps)


def iso8601_to_datetime(iso8601: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(iso8601)


def strip_downward_suffix(units: str) -> str:
    """Strip downward suffix from units"""
    return units[:-9] if units.endswith(" downward") else units


def units_string(units: str, *, downward: bool = False) -> str:
    if "downward" in units:
        return units_string(strip_downward_suffix(units), downward=downward)
    if downward:
        return f"{units} downward"
    return strip_downward_suffix(units)
