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
"""DGI cv/ev/wa exe enum objects"""

from __future__ import annotations

from dgpy.core._cv import __CV__
from dgpy.core._ev import __EV__
from dgpy.core._wa import __WA__
from dgpy.core.exe import exe_function_name
from dgpy.dgpydantic import StringEnum

ModEnum = type[StringEnum]
CV = StringEnum(  # type: ignore[call-overload]
    "CV",
    dict(exe_function_name(exe_name) for exe_name in __CV__),
)
EV = StringEnum(  # type: ignore[call-overload]
    "EV",
    dict(exe_function_name(exe_name) for exe_name in __EV__),
)
WA = StringEnum(  # type: ignore[call-overload]
    "WA",
    dict(exe_function_name(exe_name) for exe_name in __WA__),
)
