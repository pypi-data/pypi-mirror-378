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
"""dgpy interactive shell and inspection module"""

from __future__ import annotations

import code
import sys

from typing import Any

import numpy as np
import pandas as pd
import xarray as xr

from shellfish import sh

from dgpy import dgio
from dgpy.__about__ import __version__

funcs = locals()

LOADERS = {
    "json": {".json", ".geojson"},
    "csv": {".csv"},
    "pydat": {".pdat"},
}


def load_src(fspath: str) -> Any:
    return dgio.read_file(
        fspath,
    )


def main(
    banner: str,
    src: Any,
    *,
    ipython: bool = False,
) -> int:
    """Main entry point for use with python interpreter."""
    local = dict(funcs, src=src, np=np, sh=sh, pd=pd, xr=xr)
    sh.echo(local)
    if not ipython:
        code.interact(banner, local=local)
    else:
        import IPython

        IPython.InteractiveShell.banner1 = banner  # type: ignore[attr-defined,assignment]
        IPython.start_ipython(argv=[], user_ns=local)

    return 0


if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        sh.echo("Usage: python -m dgpy.insp [--ipython] [--help] filepath")
        sys.exit(0)
    _verbose = any(
        arg in sys.argv
        for arg in (
            "--verbose",
            "-v",
        )
    )
    _argv_set = set(sys.argv)
    _ipython = any(arg in _argv_set for arg in ("--ipython", "-i", "ipython"))
    arguments = [
        arg
        for arg in sys.argv
        if arg
        not in (
            "--ipython",
            "-i",
            "ipython",
            "--verbose",
            "-v",
        )
    ]
    last_arg = arguments[-1]
    src_file = (
        last_arg
        if not last_arg.startswith("--") and not last_arg.endswith(".py")
        else None
    )
    src = load_src(src_file) if src_file else None
    main(
        banner=f"dgpy {__version__} repl",
        src=src,
        ipython=_ipython,
    )
