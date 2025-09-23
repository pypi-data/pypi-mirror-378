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
"""Current running process info"""

from __future__ import annotations

import warnings

from shellfish.process import (
    ENV as ENV,
    PYTHON_IMPLEMENTATION as PYTHON_IMPLEMENTATION,
    SYS_PATH_SEP as SYS_PATH_SEP,
    Env as Env,
    env as env,
    env_dict as env_dict,
    is_cpython as is_cpython,
    is_mac as is_mac,
    is_notebook as is_notebook,
    is_pypy as is_pypy,
    is_win as is_win,
    is_wsl as is_wsl,
    ismac as ismac,
    iswin as iswin,
    iswsl as iswsl,
    opsys as opsys,
    sys_path_sep as sys_path_sep,
)

__all__ = (
    "ENV",
    "PYTHON_IMPLEMENTATION",
    "SYS_PATH_SEP",
    "Env",
    "env",
    "env_dict",
    "is_cpython",
    "is_mac",
    "is_notebook",
    "is_pypy",
    "is_win",
    "is_wsl",
    "ismac",
    "iswin",
    "iswsl",
    "opsys",
    "sys_path_sep",
)
warnings.warn(
    "dgpy.process is deprecated; import directly from shellfish.process",
    DeprecationWarning,
    stacklevel=2,
)
