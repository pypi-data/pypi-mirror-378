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
"""Web and networking utilities"""

from __future__ import annotations

import socket

from typing import Final

from dgpy.ex import DgpyError

_MIN_PORT: Final[int] = 1025  # 2**10 + 1
_MAX_PORT: Final[int] = 65535  # 2**16 - 1


def _port_valid(port: int) -> bool:
    """Return True if the given port is valid; False otherwise"""
    return _MIN_PORT <= port <= _MAX_PORT


def port_in_use(port: int) -> bool:
    """Return True if the given port is in use; False otherwise"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        res = sock.connect_ex(("localhost", port))
        return res == 0


def get_unused_port(range_min: int = _MIN_PORT, range_max: int = _MAX_PORT) -> int:
    """Return an unused port integer given min and max values for the port"""
    if not _port_valid(range_min) or not _port_valid(range_max):
        raise DgpyError(f"Min port {range_min} is not valid!")
    tried: set[int] = set()
    for port_num in range(range_min, range_max):
        if port_num not in tried and not port_in_use(port_num):
            return port_num
        tried.add(port_num)
    raise DgpyError("No unused port found!")
