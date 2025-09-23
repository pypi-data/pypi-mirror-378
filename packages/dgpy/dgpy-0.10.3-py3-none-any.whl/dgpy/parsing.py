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
"""parsing utilities"""

from __future__ import annotations

from io import StringIO
from itertools import takewhile
from typing import TYPE_CHECKING, TextIO

from shellfish import file_lines_gen, read_str

if TYPE_CHECKING:
    from collections.abc import Iterable

    from dgpy._types import FsPath


def header_lines_ix(lines: Iterable[str]) -> int:
    """Get the index for the first non header line for a dgi ascii file

    Args:
        lines: ascii file lines

    Returns:
        index of the first non-header line

    """
    ix = 0
    for ix, line in enumerate(lines):
        if not line.startswith("# "):
            return ix
    return ix


def head_body_lines(lines: list[str] | str) -> tuple[list[str], list[str]]:
    """Split an ascii dgi file lines into header and body lines

    Args:
        lines: file lines

    Returns:
        two lists: header-lines and body-lines

    """
    if isinstance(lines, str):
        lines = lines.splitlines(keepends=False)
    ix = header_lines_ix(lines)
    if lines[-1].lower().startswith("# ") and all(
        line.startswith("# ") for line in lines
    ):
        return lines, []
    if ix - 1 == len(lines):
        return lines, []

    return (
        lines[:ix],
        [line for line in lines[ix:] if not line.startswith("# ") and line != ""],
    )


def head_body_strings(lines: list[str] | str) -> tuple[str, str]:
    """Split an ascii dgi file lines into header and body lines

    Args:
        lines: file lines

    Returns:
        two lists: header-lines and body-lines

    """
    if isinstance(lines, str):
        return head_body_strings(lines.splitlines(keepends=False))
    head, body = head_body_lines(lines)
    return "\n".join(head), "\n".join(body)


def head_body_buffers(lines: list[str]) -> tuple[TextIO, TextIO]:
    """Split an ascii dgi file lines into header and body lines

    Args:
        lines: file lines

    Returns:
        two lists: header-lines and body-lines

    """
    head_str, body_str = head_body_strings(lines)
    return StringIO(head_str), StringIO(body_str)


def _is_header_line(string: str) -> bool:
    """Determine if a line is a header line"""
    return bool(str(string).startswith("#"))


def header_lines_gen(filepath: FsPath) -> Iterable[str]:
    """Yield header lines from a given fspath

    Args:
        filepath: Path to file with headerlines

    Returns:
        Header lines

    """
    return takewhile(_is_header_line, file_lines_gen(filepath))


def header_lines(filepath: str) -> list[str]:
    """Return a list of the header lines for a file given the fspath

    Args:
        filepath: Filepath with headerlines

    Returns:
        List of header lines

    """
    return list(header_lines_gen(filepath))


def header_string(filepath: str) -> str:
    """Return a list of the header lines for a file given the fspath

    Args:
        filepath: Filepath with header lines/string

    Returns:
        str: File header as a single string

    """
    return "\n".join(header_lines_gen(filepath))


def count_head_and_body_lines(filepath: FsPath) -> tuple[int, int]:
    """Count the number of header and body lines given a fspath

    Args:
        filepath: Filepath for file containing header and body lines

    Returns:
        The number of header lines and the number of body lines

    """
    file_string = (
        read_str(filepath).replace("\r\n", "\n").replace("\n\n", "\n").strip("\n")
    )
    file_lines = file_string.split("\n")
    hlines, blines = head_body_lines(file_lines)
    return len(hlines), len(blines)
