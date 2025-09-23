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
"""Python builtin data structure utils"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from collections.abc import Hashable, Mapping


def dict2tuple(dictionary: dict[Hashable, Any]) -> tuple[Any, ...]:
    """Convert a dictionary to a sorted tuple of key-value tuples

    Args:
        dictionary: dictionary to convert

    Returns:
        Sorted tuple of key-value tuples

    Examples:
        >>> dict2tuple({"a": 1, "b": 2, "c": 3})
        (('a', 1), ('b', 2), ('c', 3))
        >>> dict2tuple({"b": 2, "a": 1, "c": 3})
        (('a', 1), ('b', 2), ('c', 3))

    """
    return tuple(sorted(dictionary.items()))


def dictlist2set(dictlist: list[dict[Hashable, Any]]) -> set[tuple[Any, ...]]:
    """Convert a list of dictionaries to a set of dictionary-tuples

    Args:
        dictlist: a list of dictionaries

    Returns:
        Set of tuples

    Examples:
        >>> dictlist2set([{"a": 1, "b": 2, "c": 3}])
        {(('a', 1), ('b', 2), ('c', 3))}
        >>> dictlist2set([{"a": 1, "b": 2, "c": 3},{"b": 2, "a": 1, "c": 3}])
        {(('a', 1), ('b', 2), ('c', 3))}
        >>> sorted(dictlist2set([{"a": 1, "b": 2, "c": 3},{"b": 2, "a": 1, "d": 4}]))
        [(('a', 1), ('b', 2), ('c', 3)), (('a', 1), ('b', 2), ('d', 4))]

    """
    return {dict2tuple(dictionary) for dictionary in dictlist}


_Tkey = TypeVar("_Tkey")
_Tval = TypeVar("_Tval")


def replace_keys(
    dictionary: dict[_Tkey, _Tval], replacements: Mapping[_Tkey, _Tkey]
) -> dict[_Tkey, _Tval]:
    """Replace the keys of a dictionary

    Args:
        dictionary: dictionary to replace keys with
        replacements: dictionary of old-key => new-key replacements

    Returns:
        dictionary with keys replaced

    """
    return {replacements.get(k, k): v for k, v in dictionary.items()}
