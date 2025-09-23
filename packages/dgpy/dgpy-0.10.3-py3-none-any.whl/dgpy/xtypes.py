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
"""Type definitions for dgpy"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar

import numpy as np

from pydantic_core import CoreSchema, core_schema

if TYPE_CHECKING:
    from pydantic import GetCoreSchemaHandler, ValidationInfo

    from dgpy import npt

_DT = TypeVar("_DT")

VecInt = tuple[int, ...]
Vec2Int = tuple[int, int]
Vec3Int = tuple[int, int, int]
Vec4Int = tuple[int, int, int, int]
Mat2x2Int = tuple[Vec2Int, Vec2Int]
Mat3x3Int = tuple[Vec3Int, Vec3Int, Vec3Int]
Mat3x4Int = tuple[Vec3Int, Vec3Int, Vec3Int, Vec3Int]
Mat4x4Int = tuple[Vec4Int, Vec4Int, Vec4Int, Vec4Int]

VecFloat = tuple[float, ...]
Vec2Float = tuple[float, float]
Vec3Float = tuple[float, float, float]
Vec4Float = tuple[float, float, float, float]
Mat2x2Float = tuple[Vec2Float, Vec2Float]
Mat3x3Float = tuple[Vec3Float, Vec3Float, Vec3Float]
Mat3x4Float = tuple[Vec3Float, Vec3Float, Vec3Float, Vec3Float]
Mat4x4Float = tuple[Vec4Float, Vec4Float, Vec4Float, Vec4Float]


class ArrMeta(type):
    """Metaclass for Arr - add your metaclass implementation here if needed"""

    ...


class Arr(np.ndarray, Generic[_DT]):
    """Numpy ndarray wrapper class to provide type annotations

    Used to be declared like:
        ```
        class Arr(np.ndarray, Generic[_DT], metaclass=ArrMeta):
            ...
        ```

    but python3.6 did not like that

    Using the type annotation:
        ```
        int_values: Arr[float]
        any_values: Arr
        shape_1d: Arr[float, (-1, )]
        shape_2d: Arr[float, (2, 1)]
        ```

    """

    __metaclass__ = ArrMeta

    @classmethod
    def validate_type(cls, v: Any) -> Arr:
        """Validate and convert input to Arr type"""
        if isinstance(v, cls):
            return v
        if isinstance(v, np.ndarray):
            return v.view(cls)
        # Convert array-like to numpy array, then to Arr
        return np.asarray(v).view(cls)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        # Alternative: Use with_info_plain_validator_function if the above doesn't work

        def _validate_arr(value: Any, info: ValidationInfo) -> Arr:
            return cls.validate_type(value)

        return core_schema.with_info_plain_validator_function(_validate_arr)

    def __new__(cls, input_array: npt.ArrayLike) -> Arr:
        return np.asarray(input_array).view(cls)

    def to_nparray(self) -> np.ndarray:
        """Eject the array and return a pure numpy array"""
        return np.ndarray(self)
