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
"""Zipping and unzipping utilities; thus the name YKK

This will hopefully eventually be moved to its own package
"""

from __future__ import annotations

import sys
import tarfile

from typing import TYPE_CHECKING

from shellfish import fs

if TYPE_CHECKING:
    from dgpy._types import FsPath


def targz(dirpath: FsPath) -> str:
    """Convert a directory to a tar.gz archive"""
    if not fs.isdir(dirpath):
        raise FileNotFoundError(str(dirpath))
    targz_path = str(dirpath) + ".tar.gz"
    with tarfile.open(targz_path, "w:gz") as tar_file:
        for filepath in fs.files_gen(dirpath):
            tar_file.add(filepath)
    return str(targz_path)


def untargz(fspath: FsPath) -> str:
    """Extract a tar.gz archive"""
    if not fs.isfile(fspath):
        raise FileNotFoundError(str(fspath))
    with tarfile.open(str(fspath)) as tar_file:
        # if python is 3.12+ add filter = 'data'
        if sys.version_info >= (3, 12):
            tar_file.extractall(filter="data")
        else:
            tar_file.extractall()
    return str(fspath).replace(".tar.gz", "")
