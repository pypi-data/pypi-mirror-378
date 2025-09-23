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
"""Hashing utilities/functions

Default hashing alg is blake2b
"""

from __future__ import annotations

from hashlib import blake2b, md5, sha1, sha256
from typing import TYPE_CHECKING

from shellfish import fs

if TYPE_CHECKING:
    from dgpy._types import FsPath

HASHERS = {
    "b2": blake2b,
    "blake2b": blake2b,
    "md5": md5,
    "sha1": sha1,
    "sha256": sha256,
}


def hash_bytes(
    bites: bytes, algorithm: str = "sha256", *, hexstr: bool = True
) -> str | bytes:
    """Get the hash of a file given a fspath using a given algorithm

    Args:
        bites: Bytes object to hash
        algorithm: Algorithm to hash the file with; Valid options are
                can pick ('b2', 'blake2b', 'md5', 'sha1', or 'sha256')
        hexstr: Whether to hexdigest the final result

    Returns:
        Hash of the as either a hexstring or a number

    """
    try:
        _hasher = HASHERS[algorithm]()  # type: ignore[operator]
        _hasher.update(bites)
        return _hasher.hexdigest() if hexstr else _hasher.digest()
    except KeyError:
        raise ValueError(
            f"Invalid hashing alg given: {algorithm}\n"
            f"|  => Valid choices: {sorted(HASHERS.keys())!s}"
        ) from None


def hash_filepath(
    filepath: FsPath, algorithm: str = "sha256", *, hexstr: bool = True
) -> str | bytes:
    """Get the hash of a file given a fspath using a given algorithm

    Args:
        filepath: path to file to hash
        algorithm: Algorithm to hash the file with; Valid options are
                can pick ('b2', 'blake2b', 'md5', 'sha1', or 'sha256')
        hexstr: Whether to hexdigest the final result

    Returns:
        Hash of the as either a hexstring or a number

    """
    try:
        _hasher = HASHERS[algorithm]()  # type: ignore[operator]
        for block in fs.read_bytes_gen(filepath):
            _hasher.update(block)
        return _hasher.hexdigest() if hexstr else _hasher.digest()
    except KeyError:
        raise ValueError(
            f"Invalid hashing alg given: {algorithm}\n"
            f"|  => Valid choices: {sorted(HASHERS.keys())!s}"
        ) from None


async def hash_filepath_async(
    filepath: FsPath, algorithm: str = "sha256", *, hexstr: bool = True
) -> str | bytes:
    """Get the hash of a file given a fspath

    Args:
        filepath: path to file to hash
        algorithm: Algorithm to hash the file with; Valid options are
                can pick ('b2', 'blake2b', 'md5', 'sha1', or 'sha256')
        hexstr: Weather to hexdigest the final result

    Returns:
        Hash of the as either a hexstring or a number

    """
    try:
        _hasher = HASHERS[algorithm]()  # type: ignore[operator]
        async for block in fs.read_bytes_gen_async(filepath):
            _hasher.update(block)
        return _hasher.hexdigest() if hexstr else _hasher.digest()
    except KeyError:
        raise ValueError(
            f"Invalid hashing alg given: {algorithm}\n"
            f"|  => Valid choices: {sorted(HASHERS.keys())!s}"
        ) from None


def sha1_filepath(filepath: FsPath, *, hexstr: bool = True) -> str | bytes:
    """Return the sha1 hash as a string for a given fspath

    Args:
        filepath (FsPath): fspath-string/Pathlib.Path object
        hexstr (bool): Return hexdigest or digest; defaults to True

    Returns:
        str: sha1 hash of the fspath

    """
    return hash_filepath(filepath, algorithm="sha1", hexstr=hexstr)


async def sha1_filepath_async(filepath: FsPath, *, hexstr: bool = True) -> str | bytes:
    """Return (ASYNC) the sha1 hash as a string for a given fspath

    Args:
        filepath (FsPath): fspath-string/Pathlib.Path object
        hexstr (bool): Return hexdigest or digest; defaults to True

    Returns:
        str: sha1 hash of the fspath

    """
    return await hash_filepath_async(filepath, algorithm="sha1", hexstr=hexstr)


def sha256_filepath(filepath: FsPath, *, hexstr: bool = True) -> str | bytes:
    """Return the sha256 hash as a string for a given fspath

    Args:
        filepath (FsPath): fspath-string/Pathlib.Path object
        hexstr (bool): Return hexdigest or digest; defaults to True

    Returns:
        str: sha256 hash of the fspath

    """
    return hash_filepath(filepath, algorithm="sha256", hexstr=hexstr)


async def sha256_filepath_async(
    filepath: FsPath, *, hexstr: bool = True
) -> str | bytes:
    """Return (ASYNC) the sha256 hash as a string for a given fspath

    Args:
        filepath (FsPath): fspath-string/Pathlib.Path object
        hexstr (bool): Return hexdigest or digest; defaults to True

    Returns:
        str: sha256 hash of the fspath

    """
    return await hash_filepath_async(filepath, algorithm="sha256", hexstr=hexstr)


def md5_filepath(filepath: FsPath, *, hexstr: bool = True) -> str | bytes:
    """Return the md5 hash as a string for a given fspath

    Args:
        filepath (FsPath): fspath-string/Pathlib.Path object
        hexstr (bool): Return hexdigest or digest; defaults to True

    Returns:
        str: md5 hash of the fspath

    """
    return hash_filepath(filepath, algorithm="md5", hexstr=hexstr)


async def md5_filepath_async(filepath: FsPath, *, hexstr: bool = True) -> str | bytes:
    """Return (ASYNC) the md5 hash as a string for a given fspath

    Args:
        filepath (FsPath): fspath-string/Pathlib.Path object
        hexstr (bool): Return hexdigest or digest; defaults to True

    Returns:
        str: md5 hash of the fspath

    """
    return await hash_filepath_async(filepath, algorithm="md5", hexstr=hexstr)


def blake2b_filepath(filepath: FsPath, *, hexstr: bool = True) -> str | bytes:
    """Return the blake2b hash as a string for a given fspath

    Args:
        filepath (FsPath): fspath-string/Pathlib.Path object
        hexstr (bool): Return hexdigest or digest; defaults to True

    Returns:
        str: blake2b hash of the fspath

    """
    return hash_filepath(filepath, algorithm="blake2b", hexstr=hexstr)


async def blake2b_filepath_async(
    filepath: FsPath, *, hexstr: bool = True
) -> str | bytes:
    """Return (ASYNC) the blake2b hash as a string for a given fspath

    Args:
        filepath (FsPath): fspath-string/Pathlib.Path object
        hexstr (bool): Return hexdigest or digest; defaults to True

    Returns:
        str: blake2b hash of the fspath

    """
    return await hash_filepath_async(filepath, algorithm="blake2b", hexstr=hexstr)
