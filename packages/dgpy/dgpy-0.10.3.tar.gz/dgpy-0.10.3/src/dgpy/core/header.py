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
"""Header parsing for dgpy"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from shellfish import sh

from dgpy.datfield import DatField
from dgpy.utils import replace_keys

if TYPE_CHECKING:
    from collections.abc import Iterator

    from dgpy._types import FsPath

HEADER_BASE = {
    "alias": "",
    "coordinate_system_id": "",
    "coordinate_system_name": "",
    "downward": False,
    "desc": "",
    "dfields": [],
    "type": "",
    "xyunits": "unknown",
    "zunits": "unknown",
}
HEADER_REPLACEMENTS = {
    "zdatum_above_msl": "z_datum_above_msl",
    "elev_above_msl": "z_datum_above_msl",
    "description": "desc",
    "units": "xyunits",
    "1st_standard_parallel": "std_parallel_1",
    "2nd_standard_parallel": "std_parallel_2",  # typos:ignore
}
DEFAULT_DITTO = {"wellid", "lineid"}


def parse_ditto_fields(header_lines: list[str]) -> Iterator[str]:
    """Parse the ditto fields given a dgi file ascii header

    Args:
        header_lines: header lines

    Yields:
        ditto field names as strings

    """
    _ditto_lines = [
        line.replace("# ", "") for line in header_lines if " ditto:" in line.lower()
    ]
    for dline in _ditto_lines:
        yield from (
            field.lower()
            for field in (el.strip(",") for el in sh.shplit(dline))
            if "ditto" not in field.lower() and field != ""
        )


def _fixed_fmt_field(field_val: str) -> DatField:
    name, start, stop, *units = sh.shplit(field_val)
    try:
        _units = " ".join(units)
    except IndexError:
        _units = "unknown"
    if _units == "":
        _units = "unknown"

    return DatField(
        ditto=True if name in DEFAULT_DITTO else False,
        name=name,
        units=_units,
    )


def _free_fmt_field(field_val: str) -> DatField:
    ix, name, *units = sh.shplit(field_val)
    try:
        _units = " ".join(units)
        if _units == "":
            _units = "unknown"
    except IndexError:
        _units = "unknown"
    return DatField(
        ditto=True if name in DEFAULT_DITTO else False,
        name=name,
        units=_units,
    )


def field_dict(field_val: str, fmt: str | None = None) -> DatField:
    """Get the fields data as a dictionary

    Args:
        field_val: Field info as a string
        fmt: 'fixed'/'free' formatted field line

    Returns:
        Dictionary of the field info

    """
    return _fixed_fmt_field(field_val) if fmt == "fixed" else _free_fmt_field(field_val)


def parse_header_line(line: str) -> tuple[str, Any]:
    """Parse a single multiple header line"""
    line = line.strip("# ")
    key = line.split(":")[0]
    val = line.replace(key + ":", "").strip()
    return key.lower(), val


def parse_header_lines(
    hlines: list[str], filepath: FsPath | None = None
) -> dict[str, Any]:
    """Parse multiple header lines"""
    _fields = []
    _field_fmt = None
    d = {}
    _desc = []
    for line in hlines:
        key, val = parse_header_line(line)
        if key == "field":
            _fields.append(field_dict(val, fmt=_field_fmt))
        elif key.lower().startswith("desc"):
            _desc.append(val)
        else:
            if "end" in key.lower():
                break
            if key == "format":
                _field_fmt = val
            d[key] = val
    d["desc"] = "\n".join(_desc)

    d = {
        **HEADER_BASE,
        **replace_keys(d, HEADER_REPLACEMENTS),
        "dfields": _fields,
        **file_type(filepath),
    }
    if any(
        "downward" in str(f.units) and "unknown" not in str(f.units) and f.name == "z"
        for f in _fields
    ):
        d["downward"] = True
    if d["xyunits"] != "" or d["xyunits"] != "unknown":
        for f in d["dfields"]:
            if f.name == "x" or f.name == "y":
                f.units = d["xyunits"]
    return {k: v for k, v in d.items() if k.strip("\n") not in {"end"}}


def parse_header_string(string: str, filepath: FsPath | None = None) -> dict[str, Any]:
    """Parse a header string"""
    _header_lines = string.splitlines(keepends=False)
    return parse_header_lines(hlines=_header_lines, filepath=filepath)


def file_type(filepath: FsPath | None = None) -> dict[str, str]:
    """Get the file_type from the fspath"""
    if filepath is None:
        return {"type": "unknown"}
    ext = str(filepath).split(".")[-1]
    ext2type = {
        "pdat": "property scattered data",
        "path": "well path data",
        "dat": "scattered data",
        "prod": "production data",
    }
    try:
        return {"type": ext2type[ext]}
    except KeyError:
        return {}
