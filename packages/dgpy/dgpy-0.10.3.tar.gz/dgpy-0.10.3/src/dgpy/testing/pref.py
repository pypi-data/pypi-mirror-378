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
"""CV/EV/WA exe wrapper functions based on the PREF env variable"""

from __future__ import annotations

from os import environ
from sys import modules

from dgpy.core._cv import __CV__
from dgpy.core._ev import __EV__
from dgpy.core._wa import __WA__
from dgpy.core.exe import funkify_mod


def _pref() -> tuple[str, tuple[str, ...], str]:
    try:
        PREF = environ["PREF"].strip('"').lower()
    except KeyError:
        PREF = "cv"
    PREF = PREF.lower()
    if PREF == "ev":
        return "EVHOME", __EV__, "ev"
    elif PREF == "wa":
        return "WAHOME", __WA__, "wa"
    elif PREF == "cv":
        return "COVIZHOME", __CV__, "cv"
    raise ValueError(f"ENV variable 'PREF' unrecognized: {PREF}")


__ENV_VAR__, __FUNCTIONS__, _PREFIX = _pref()
funkify_mod(modules[__name__], prefix=_PREFIX)
