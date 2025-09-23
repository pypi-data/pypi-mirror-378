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
"""DGI prefix => cv/ev/wa"""

from __future__ import annotations

from enum import Enum

from dgpy.core._cv import __CV__
from dgpy.core._ev import __EV__
from dgpy.core._wa import __WA__

__all__ = (
    "DgiPref",
    "dgi_module_functions",
    "prefix2enum",
)


class DgiPref(str, Enum):
    """DGI module prefixes"""

    cv = "cv"
    ev = "ev"
    wa = "wa"


def prefix2enum(prefix: str | DgiPref) -> DgiPref:
    """Return enum value for prefix"""
    try:
        return DgiPref.__members__[prefix.lower()]
    except KeyError:
        pass
    raise ValueError("Invalid prefix; prefix param must be ('cv'/'ev'/'wa')")


def dgi_module_functions(prefix: str | DgiPref) -> tuple[str, ...]:
    """Return list of exe functions from a dgi prefix (cv/ev/wa)"""
    _prefix = prefix2enum(prefix)
    if _prefix == "cv":
        return __CV__
    if _prefix == "ev":
        return __EV__
    if prefix == "wa":
        return __WA__
    raise ValueError("Invalid prefix; prefix param must be ('cv'/'ev'/'wa')")
