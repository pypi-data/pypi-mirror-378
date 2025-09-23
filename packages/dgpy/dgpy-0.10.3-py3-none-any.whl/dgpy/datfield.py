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
"""Data field object"""

from __future__ import annotations

from pydantic import Field

from dgpy.dgpydantic import DgpyBaseModel

__all__ = ("DatField",)


class DatField(DgpyBaseModel):
    r"""Field object for dgpy objects that are field based

    Examples:
        >>> f = DatField(name="fname", ditto=False)
        >>> f
        DatField(name='fname', ditto=False, units='unknown')
        >>> print(f)
        DatField(name='fname', ditto=False, units='unknown')
        >>> fdict = f.model_dump()
        >>> fdict
        {'name': 'fname', 'ditto': False, 'units': 'unknown'}
        >>> parsed = DatField(**fdict)
        >>> parsed
        DatField(name='fname', ditto=False, units='unknown')
        >>> parsed == f
        True
        >>> fjson = f.model_dump_json(indent=2)
        >>> fjson
        '{\n  "name": "fname",\n  "ditto": false,\n  "units": "unknown"\n}'
        >>> print(fjson)
        {
          "name": "fname",
          "ditto": false,
          "units": "unknown"
        }
        >>> parsed = DatField.model_validate_json(fjson)
        >>> parsed
        DatField(name='fname', ditto=False, units='unknown')
        >>> parsed == f
        True

    """

    name: str = Field(..., title="Field name")
    ditto: bool = Field(default=False, title="ditto")
    units: str = Field(default="unknown", title="units")
