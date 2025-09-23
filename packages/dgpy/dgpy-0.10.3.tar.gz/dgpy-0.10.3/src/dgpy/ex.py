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
"""Error objects for dgpy"""

from __future__ import annotations

from pprint import pformat
from shutil import get_terminal_size
from traceback import format_exc
from typing import Any

import fmts


class DgpyError(Exception):
    """Error class for dgpy"""

    info: dict[str, Any] | None = None

    def __init__(
        self,
        msg: str = "DgpyError",
        info: dict[str, Any] | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Create a DgpyError; which is an Exception"""
        super().__init__(msg, *args)
        self.info = info

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        """Return a formatted and readable string for DgpyError"""
        base_str = super().__str__()
        if self.info:
            _terminal_size = get_terminal_size((80, 20))
            _columns = _terminal_size.columns - 4
            return "\n".join([
                base_str,
                "__INFO__",
                fmts.indent(pformat(self.info, indent=2, width=_columns)),
            ])
        return base_str


def error_log_string(error: Any) -> str:
    """Format an error string for logging with traceback information

    Args:
        error: error/exception

    Returns:
        str: Formatted error string

    """
    return (
        f"_________\n"
        f"Exception: {error!s}\n"
        f"----Exception type: {type(error)!s}\n"
        f"----Traceback: {format_exc()!s}\n"
        f"~ ~ ~"
    )


if __name__ == "__main__":
    ...
