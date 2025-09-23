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
from __future__ import annotations

from os import PathLike
from pathlib import Path
from typing import TYPE_CHECKING, Any, ParamSpec, TypeVar

if TYPE_CHECKING:
    from typing import TypeAlias

    PathLikeAny: TypeAlias = PathLike[Any]
    PathLikeStr: TypeAlias = PathLike[str]
    PathLikeBytes: TypeAlias = PathLike[bytes]
    PathLikeStrBytes: TypeAlias = PathLikeStr | PathLikeBytes
else:
    PathLikeAny = PathLike
    PathLikeStr = PathLike
    PathLikeBytes = PathLike
    PathLikeStrBytes = PathLike

__all__ = (
    "_R",
    "FsPath",
    "Json",
    "JsonArrT",
    "JsonDictT",
    "JsonListT",
    "JsonObjT",
    "JsonPrimitive",
    "JsonT",
    "PathLikeAny",
    "PathLikeBytes",
    "PathLikeStr",
    "PathLikeStrBytes",
    "T",
)

T = TypeVar("T")
_R = TypeVar("_R")
P = ParamSpec("P")

FsPath: TypeAlias = str | Path | PathLikeAny
JsonPrimitive: TypeAlias = bool | int | float | str | None
Json: TypeAlias = dict[str, "Json"] | list["Json"] | str | int | float | bool | None
JsonT: TypeAlias = dict[str, "JsonT"] | list["JsonT"] | str | int | float | bool | None
JsonDictT: TypeAlias = dict[str, Any]
JsonListT: TypeAlias = list[Any]
JsonObjT: TypeAlias = dict[str, Any]
JsonArrT: TypeAlias = list[Any]
