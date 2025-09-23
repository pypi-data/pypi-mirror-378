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
"""dgpy.status

Utils for checking the status of dgpy and its dependencies
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import xarray as xr

from pydantic import __version__ as __pydantic_version__
from typing_extensions import TypedDict

from dgpy.__about__ import __pkgroot__, __title__, __version__

__pytest_version__: str | None = None
try:
    from pytest import __version__ as __pytest_version__  # type: ignore[no-redef]
except ImportError:
    ...


def _zmq_version() -> str | None:
    try:
        import zmq

        return zmq.__version__
    except ImportError:
        return None


def _h5py_version() -> str | None:
    try:
        import h5py

        return h5py.__version__
    except ImportError:
        return None


class DgpyDepVersionsStatusDict(TypedDict):
    h5py: str | None
    numpy: str | None
    pandas: str | None
    pydantic: str | None
    xarray: str | None
    zmq: str | None


class DgpyStatusDict(TypedDict):
    pkg: str
    pkgroot: str
    version: str
    deps: dict[str, str | None]
    devdeps: dict[str, str | None]


def status() -> DgpyStatusDict:
    """Return a dict with the status of dgpy and its dependencies"""
    zmq_version = _zmq_version()
    return {
        "pkg": __title__,
        "pkgroot": __pkgroot__,
        "version": __version__,
        "deps": {
            "h5py": _h5py_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "pydantic": __pydantic_version__,
            "xarray": xr.__version__,
            "zmq": zmq_version,
        },
        "devdeps": {
            "pytest": __pytest_version__,
        },
    }


def main() -> None:
    import json
    import sys

    json.dump(status(), sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
