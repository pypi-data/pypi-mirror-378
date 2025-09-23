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
"""Metadata"""

from __future__ import annotations

from typing import TYPE_CHECKING

from shellfish.fs import read_str
from shellfish.sh import files_gen

from dgpy.__about__ import __pkgroot__

if TYPE_CHECKING:
    from dgpy._types import FsPath

ENCODING = "# -*- coding: utf-8 -*-"
COPYRIGHT = """
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
"""
DGPY_SRC_HEADER = f"{ENCODING}{COPYRIGHT}"


def filepath_line_count(filepath: FsPath) -> int:
    """Return the number of lines in a file given the file's fspath"""
    file_string = read_str(str(filepath))
    return len(file_string.splitlines())


def _dgpy_source_files() -> list[str]:
    """Return a list of all the files in the dgpy package"""
    return [
        filepath
        for filepath in files_gen(__pkgroot__)
        if filepath.endswith(".py")
        or filepath.endswith(".pyx")
        or filepath.endswith(".pxd")
        or filepath.endswith(".pyi")
    ]


def _dgpy_lines_count() -> int:
    """Return the total number of python lines in the dgpy source code"""
    return sum(filepath_line_count(fp) for fp in _dgpy_source_files())


def dgpy_stats() -> dict[str, int]:
    """Return a dictionary with statistic on dgpy"""
    return {
        "total_python_lines": _dgpy_lines_count(),
        "number_of_python_files": len(_dgpy_source_files()),
    }
