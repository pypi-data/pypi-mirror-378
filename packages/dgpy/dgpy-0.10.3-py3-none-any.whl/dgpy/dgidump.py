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
"""Dump methods and utilities for dgpy"""

from __future__ import annotations

import logging

from os import path
from shlex import split as shplit
from typing import TYPE_CHECKING, Any

from fmts import multi_replace, rm_dunderscore, rm_whitespace
from jsonbourne import JSON
from shellfish.sh import do

if TYPE_CHECKING:
    from collections.abc import Generator

log = logging.getLogger(__name__)

DUMP_VALS = {
    "no": False,
    "'no'": False,
    "yes": True,
    "null": None,
    "(null)": None,
    "unknown": None,
    "none": None,
    None: None,
    "nan": "nan",
    "-nan": "nan",
}


def _clean_json_dump_string_value(val: str) -> bool | str | None:
    if val == "yes" or val.lower().strip() in {"yes", '"yes"', "'yes'"}:
        return True
    if val.lower().strip() in {"nan", "-nan"}:
        return "nan"
    if val.lower().strip() in {"null", "'null'", '"null"', "none", "unknown"}:
        return None
    return val


def _clean_json_dump_value(val: Any) -> Any:
    if isinstance(val, dict):
        return _clean_json_dump_dict(val)
    if isinstance(val, str):
        return _clean_json_dump_string_value(val)
    return val


def _clean_json_dump_dict(dump_dict: dict[str, Any]) -> dict[str, Any]:
    return {k: _clean_json_dump_value(v) for k, v in dump_dict.items()}


def _celldump(
    filepath: str, prefix: str = "cv", env: dict[str, str] | None = None
) -> str:
    """Return the celldump string for a cellgrid

    Args:
        filepath: Filepath to cellgrid
        prefix: Prefix to use with _celldump exe
        env: Environment dictionary

    Returns:
        str: celldump string

    """
    dump_args = [f"{prefix}_celldump", filepath]
    sub_proc = do(args=dump_args, env=env)
    if sub_proc.returncode == 1:
        raise ValueError(
            "\n".join((
                f"Dump string failed: {filepath}",
                f"STDOUT: {sub_proc.stdout}",
                f"STDERR: {sub_proc.stderr}",
            ))
        ) from None
    return str(sub_proc.stdout)


def dump(
    filepath: str,
    *,
    prefix: str = "cv",
    J: bool = False,
    K: bool = False,
    env: dict[str, str] | None = None,
) -> str:
    """Run cv/ev/wa_dump given a fspath

    Args:
        filepath: fspath to cv/ev/wa_dump
        K: True attaches the '-K' flag to cv/ev/wa_dump
        J: True attaches the '-J' flag to cv/ev/wa_dump
        prefix: Which dgi prefix to use: cv, ev, or wa (Default value = "cv")
        env: Environment dictionary

    Returns:
        cv/ev/wa_dump string

    """
    if not path.exists(filepath):
        raise FileNotFoundError(filepath) from None
    if K and J:
        raise ValueError("Cannot give both K=True and json=True") from None
    if filepath.endswith(".c3grd"):
        return _celldump(filepath=filepath, prefix=prefix, env=env)
    dump_args = [
        f"{prefix}_dump",
        "-K" if K else None,
        "-J" if J else None,
        filepath,
    ]
    dump_args_filtered = list(filter(None, dump_args))
    _proc = do(args=dump_args_filtered, env=env)
    return str(_proc.stdout)


def _clean_dump_k_key(key: str) -> str:
    """Clean up keys parsed from output of `cv/ev/wa_dump -K`

    Args:
        key: Key to parse

    Returns:
        cleaned key

    """
    sub_patterns = {
        "-": "_",
        "number_of_": "num_",
        "x_and_y_": "xy",
        "z_units": "zunits",
        "xcolumns": "xcol",
        "yrows": "yrow",
    }
    key = key.lower()
    key = rm_whitespace(key, join_str="_")
    key = rm_dunderscore(key)
    patters_in_key = (p for p in sub_patterns if p in key)
    for pattern in patters_in_key:
        key = key.replace(pattern, sub_patterns[pattern])
    return key.strip("_")


def _parse_dump_val(
    val: str,
) -> (
    float
    | str
    | bool
    | int
    | list[list[int | float]]
    | list[int | float]
    | list[int]
    | None
):
    """Parse a dump value

    Args:
        val: Value to parse

    Returns:
        parsed value

    """
    val = val.strip('"')
    if val in DUMP_VALS:
        return DUMP_VALS[val]
    elif " to " in val:
        try:
            vals = (sub_val.strip() for sub_val in val.split(","))
            return [
                list(map(float, sub_val.replace(" ", "").split("to")))
                for sub_val in vals
            ]
        except ValueError:
            return _parse_dump_val(val[: val.find("(")])
    elif " by " in val:
        try:
            return [int(v) for v in val.replace(" ", "").split("by")]
        except ValueError:
            ...

    try:
        return int(val)
    except ValueError:
        ...
    try:
        return float(val)
    except ValueError:
        ...
    return val


def parse_dump(header_string: str) -> dict[str, Any]:
    """Parse raw output string from cv_dump/ev_dump/wa_dump

    Args:
        header_string (str): dgi file header as a string

    Returns:
        Dictionary of parsed data

    """
    lines = (
        line
        for line in header_string.splitlines(keepends=False)
        if line != "" and ":" in line and "=====" not in line
    )
    lines = (line for line in lines if not line.startswith("attribute:"))
    split_lines = (line.split(":") for line in lines)
    key_val_lines = ((line[0], " ".join(line[1:]).strip(" ")) for line in split_lines)
    header_info = {
        _clean_dump_k_key(key): _parse_dump_val(val) for key, val in key_val_lines
    }
    return header_info


def _fix_dump_keys(dump_dict: dict[str, Any]) -> dict[str, Any]:
    replacements = {
        "xcolumns": "xcol",
        "yrows": "yrow",
        "zlevels": "zlev",
    }
    return {replacements.get(key, key): val for key, val in dump_dict.items()}


def _parse_dump_k(header_string: str) -> dict[str, Any]:
    """Parse the output from `cv/ev/wa_dump -K`

    Args:
        header_string: Header string from `cv/ev/wa_dump -K`

    Returns:
        Dictionary of parsed data

    """

    def _parse_attr(line: str) -> dict[str, Any]:
        key_vals = (key_val.split("=") for key_val in shplit(line))
        return {_clean_dump_k_key(key): _parse_dump_val(val) for key, val in key_vals}

    def _parse_attributes(
        attribute_strings: list[tuple[str, str]],
    ) -> dict[str, list[Any]]:
        return {"attributes": [_parse_attr(line[1]) for line in attribute_strings]}

    def _parse_non_attributes(
        non_attributes_tuples: Generator[tuple[str, str], None, None],
    ) -> dict[str, Any]:
        return {
            _clean_dump_k_key(key): _parse_dump_val(val)
            for key, val in non_attributes_tuples
        }

    lines = [
        (a, b)
        for a, _, b in (
            line.partition(" ")
            for line in header_string.splitlines(keepends=False)
            if line != ""
        )
    ]
    attr_lines = [line for line in lines if line[0] == "attribute"]
    non_attr_lines = (line for line in lines if line not in attr_lines)
    data = {**_parse_attributes(attr_lines), **_parse_non_attributes(non_attr_lines)}
    return _fix_dump_keys(data)


def _parse_dump_j(json_dump_string: str) -> dict[str, Any]:
    """Load the JSON dump for a file given the fspath

    Args:
        fspath: Filepath to the file to get the header/dump data
        prefix: Prefix to use
        env: Environment dictionary

    Returns:
        Dump data as a dictionary

    """
    r = [
        ('"unknown"', "null"),
        ('"yes"', "true"),
        ('"no"', "false"),
        ("'no'", "false"),
        (" no ", "false"),
        ('"null"', "null"),
        ('"(null)"', "null"),
        (" inf", '"inf"'),
        (" -inf", '"-inf"'),
    ]
    json_dump_string = multi_replace(json_dump_string, r)
    try:
        return _fix_dump_keys({"attributes": [], **JSON.loads(json_dump_string)})

    except JSON.JSONDecodeError as e:
        if "\\" not in json_dump_string:
            raise e

    try:
        return {"attributes": [], **JSON.loads(json_dump_string.replace("\\", "\\\\"))}
    except JSON.JSONDecodeError as e:
        raise e


def _load_dump_j(
    filepath: str, prefix: str = "cv", env: dict[str, str] | None = None
) -> dict[str, Any]:
    """Load the JSON dump for a file given the fspath

    Args:
        filepath: Filepath to the file to get the header/dump data
        prefix: Prefix to use
        env: Environment dictionary

    Returns:
        Dump data as a dictionary

    """
    json_dump_string = dump(filepath, prefix=prefix, J=True, env=env)
    return {
        "fspath": filepath,
        "filename": path.basename(filepath),
        **_parse_dump_j(json_dump_string),
    }


def _load_dump_k(
    filepath: str, prefix: str = "cv", env: dict[str, str] | None = None
) -> dict[str, Any]:
    """Load and parse the output from `cv/ev/wa_dump -K` into a dictionary

    Args:
        filepath (str): fspath to load the dump for
        prefix (str): 'cv' / 'ev' / 'wa' prefix
        env (dict[str, str]): Environment dictionary to run dump under

    Returns:
        Dictionary of parsed data

    """
    return {
        "fspath": filepath,
        "filename": path.basename(filepath),
        **_parse_dump_k(dump(filepath, prefix=prefix, K=True, env=env)),
    }


def read_header(
    filepath: str, prefix: str = "cv", env: dict[str, str] | None = None
) -> dict[str, Any]:
    """cv/ev/wa_dump a file given the path and then parse the resulting string

    Args:
        filepath (str): fspath to load the dump for
        prefix (str): 'cv' / 'ev' / 'wa' prefix
        env (dict[str, str]): Environment dictionary to run dump under

    Returns:
        Dictionary with the dump data

    """
    try:
        return _load_dump_j(filepath=filepath, prefix=prefix, env=env)
    except Exception as e:
        log.debug(
            "Failed to load JSON dump for %s with prefix %s: %s",
            filepath,
            prefix,
            e,
        )
        log.debug("Falling back to K dump for %s with prefix %s", filepath, prefix)
        return _load_dump_k(filepath=filepath, prefix=prefix, env=env)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
