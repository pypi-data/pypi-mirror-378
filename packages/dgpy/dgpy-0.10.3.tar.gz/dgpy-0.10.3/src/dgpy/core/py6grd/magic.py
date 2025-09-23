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
"""Magic number for 2grid and 3grid io"""

from __future__ import annotations

from dgpy.dgpydantic import DgpyBaseModel


class MagicNumber(DgpyBaseModel):
    """Evg token magic number mapping"""

    byte_order: str
    is_2d: bool
    is8fmt: bool
    bin_length: int
    bin_length_flag: str


MAGIC_NUM_DATA: dict[int, MagicNumber] = {
    # 2D: Pre-EV 8.0 rotated & non-rotated grids
    0x2D2D2D2D: MagicNumber(
        byte_order=">",  # Always Big Endian so read as Big Endian
        is_2d=True,
        is8fmt=False,
        bin_length=4,  # Length of "length" info after Token
        bin_length_flag="i",  # unpack flag
    ),
    # 2D: EV 8.0+ rotated & non-rotated grids
    0x2D762D76: MagicNumber(
        byte_order="=",  # Native Format written on Linux/Windows
        is_2d=True,
        is8fmt=True,
        bin_length=8,  # Length of "length" info after Token
        bin_length_flag="q",  # unpack flag
    ),
    # 2D: EV 8.0+ Byte-swapped (Sun/SGI)
    0x762D762D: MagicNumber(
        byte_order=">",  # Native Format written on Sun/SGI, read as Big Endian
        is_2d=True,
        is8fmt=True,
        bin_length=8,  # Length of "length" info after Token
        bin_length_flag="q",  # unpack flag
    ),
    # 3D: Pre-EV 8.0 rotated & non-rotated grids
    0x3D3D3D3D: MagicNumber(
        byte_order=">",  # Always Big Endian so read as Big Endian
        is_2d=False,
        is8fmt=False,
        bin_length=4,  # Length of "length" info after Token
        bin_length_flag="i",  # unpack flag
    ),
    # 3D: EV 8.0+ rotated & non-rotated grids
    0x3D763D76: MagicNumber(
        byte_order="=",  # Native Format written on Linux/Windows
        is_2d=False,
        is8fmt=True,
        bin_length=8,  # Length of "length" info after Token
        bin_length_flag="q",  # unpack flag
    ),
    # 3D: EV 8.0+ Byte-swapped (Sun/SGI)
    0x763D763D: MagicNumber(
        byte_order=">",  # Native Format written on Sun/SGI, read as Big Endian
        is_2d=False,
        is8fmt=True,
        bin_length=8,  # Length of "length" info after Token
        bin_length_flag="q",  # unpack flag
    ),
}
