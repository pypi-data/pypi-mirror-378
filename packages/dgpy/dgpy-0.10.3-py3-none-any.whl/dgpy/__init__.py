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
"""Dynamic Graphics Python ~ dgpy

The official dgi python package!

```
Dynamic Graphics Python
    _
  _| |___ ___ _ _
 | . | . | . | | |
 |___|_  |  _|_  |
     |___|_| |___|
```
"""

from __future__ import annotations

from dgpy.__about__ import __version__
from dgpy.core.boundingbox import BoundingBox
from dgpy.core.config import DgiConfig, __config__, config
from dgpy.core.enums.evu import Evu
from dgpy.core.pyspace import PySpace
from dgpy.datfield import DatField
from dgpy.ex import DgpyError
from dgpy.pydat import Pydat, PydatHeader
from dgpy.pygrd import Py2grd, Py2grdHeader, Py3grd, Py3grdHeader

__all__ = (
    "BoundingBox",
    "DatField",
    "DgiConfig",
    "DgpyError",
    "Evu",
    "Py2grd",
    "Py2grdHeader",
    "Py3grd",
    "Py3grdHeader",
    "PySpace",
    "Pydat",
    "PydatHeader",
    "__config__",
    "__version__",
    "config",
)
