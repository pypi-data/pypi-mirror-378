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
"""bdat; dgi binary-dat file utils"""

from __future__ import annotations

import logging

from typing import TYPE_CHECKING

import h5
import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from dgpy import npt
    from dgpy._types import FsPath

_log = logging.getLogger(__name__)


def _apply_index_array(
    index_array: npt.NDArray, values_array: npt.NDArray
) -> npt.NDArray:
    """Apply an index array (usage_set/lut) to an array"""
    try:
        _ret_array = index_array[values_array]
        return _ret_array
    except IndexError:
        _log.debug("Index array %s is out of range", index_array)

    try:
        return index_array[values_array - min(index_array)]
    except IndexError:
        # In this case the values array is usually an ijk array
        # no application of an index array is needed
        return values_array


def unpack_bdata(filepath: FsPath) -> dict[str, npt.NDArray | pd.Series]:
    """Unpack a bdat given its fspath

    Args:
        filepath (str): bdat-fspath as a string

    Returns:
        Dictionary of property names to the corresponding bdat-datasets.

    Raises:
        ValueError: if bdat array length mismatch detected

    """
    # load the h5 file into the datasets
    _datasets_dict = h5.datasets_dict(str(filepath))
    _bdat_keys: set[str] = {
        k for k in _datasets_dict.keys() if k.startswith("/attr/property/")
    }
    _bdat_values_keys = {
        k
        for k in _bdat_keys
        if k.startswith("/attr/property/") and k.endswith("values")
    }
    _bdat_non_values = _bdat_keys - _bdat_values_keys
    _bdat_values = {k: _datasets_dict[k] for k in _bdat_values_keys}
    _bdat_values_types = {k: (v, type(v)) for k, v in _bdat_values.items()}

    # get the actual unpacked shape of the dataset arrays
    _bdat_values_length = {
        v.shape for k, v in _bdat_values.items() if isinstance(v, np.ndarray)
    }
    # check/assert that there is only 1 shape
    if len(_bdat_values_length) != 1:
        _log.debug("bdat_values_length: %s", _bdat_values_length)
        raise ValueError(f"bdat_values_length: {_bdat_values_length}")
    _arr_shape = _bdat_values_length.pop()

    # Get all the values arrays...
    # => TAKE the array if it is an array
    # => OR make an array of the correct shape using np.full w/ 1 value given
    _bdat_values_arrays = {
        k.replace("/attr/property/", "").split("/")[0]: (
            v if isinstance(v, np.ndarray) else np.full(shape=_arr_shape, fill_value=v)
        )
        for k, v in _bdat_values.items()
    }

    # snag all the lut (look-up-table) and usage_set dataset arrays
    _bdat_lut_and_usage_sets = {
        k.replace("/attr/property/", "").split("/")[0]: v
        for k, v in _datasets_dict.items()
        if k in _bdat_non_values
    }

    # For each key and array in the lut/usage_set dict...
    # Apply the usageset/lut to the index array to get the actual values
    for k, v in _bdat_lut_and_usage_sets.items():
        if not isinstance(v, np.ndarray):
            continue
        values_array = _bdat_values_arrays[k]
        lut_applied = _apply_index_array(
            index_array=v,
            values_array=values_array,
        )
        if lut_applied.dtype == np.dtype("O"):
            series = pd.Series(
                lut_applied,
                dtype="category",
            )
            _bdat_values_arrays[k] = series
        else:
            _bdat_values_arrays[k] = lut_applied
    return _bdat_values_arrays
