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
"""dgpy configuration"""

from __future__ import annotations

from functools import lru_cache
from itertools import chain
from os import environ, getcwd, path
from pathlib import Path
from pprint import pformat as pfmt
from typing import TYPE_CHECKING, Any

from jsonbourne import JSON
from listless import unique_gen
from shellfish import fs
from shellfish.process import env_dict, is_win

from dgpy.dgpydantic import DgpyBaseModel

if TYPE_CHECKING:
    import types

    from collections.abc import Callable, Iterator

    from dgpy._types import FsPath

__all__ = (
    "DgiConfig",
    "__config__",
    "config",
)

_ENV = dict(environ.items())
try:
    _HOMEDIRPATH = _ENV["USERPROFILE"] if is_win() else _ENV["HOME"]
except KeyError:
    _HOMEDIRPATH = getcwd()

_DGI_ENV_VARS = [
    "COVIZHOME",
    "EVHOME",
    "WAHOME",
    "DGI_NLCD_LICENSE_FILE",
    "MSYSPATH",
    "LM_LICENSE_FILE",
    "TESHTING",
]
_ENV_VARIABLES = {
    "DGPY_LOG_LEVEL",
    "PREF",
}
_CONFIG_FILENAMES = ("dgi.config.json", ".dgi.json")


class DgiConfig(DgpyBaseModel):
    """Dgi configuration container object"""

    COVIZHOME: str = ""
    EVHOME: str = ""
    WAHOME: str = ""
    DGI_NLCD_LICENSE_FILE: str = ""
    LM_LICENSE_FILE: str = ""
    MSYSPATH: str = ""
    PREF: str = ""
    DGPY_LOG_LEVEL: str = "WARNING"
    verbose: bool = False
    debug: bool = False
    TESHTING: bool = False

    def coviz_home_exists(self) -> bool:
        if self.COVIZHOME == "":
            return False
        return path.exists(self.COVIZHOME)

    def evhome_exists(self) -> bool:
        if self.EVHOME == "":
            return False
        return path.exists(self.EVHOME)

    def wahome_exists(self) -> bool:
        if self.WAHOME == "":
            return False
        return path.exists(self.WAHOME)

    def refresh_env_vars(self) -> None:
        if self.COVIZHOME != environ.get("COVIZHOME", ""):
            self.COVIZHOME = environ.get("COVIZHOME", "")
        if self.EVHOME != environ.get("EVHOME", ""):
            self.EVHOME = environ.get("EVHOME", "")
        if self.WAHOME != environ.get("WAHOME", ""):
            self.WAHOME = environ.get("WAHOME", "")

    def _lin_env(self) -> dict[str, str]:
        """Get current linux environment path"""
        _path_parts = []
        _ld_lib_path_parts = []
        if self.COVIZHOME != "":
            _path_parts.extend(_dgi_path_parts(self.COVIZHOME))
            _ld_lib_path_parts.extend(_dgi_ld_lib_path(self.COVIZHOME))

        if self.EVHOME != "":
            _path_parts.extend(_dgi_path_parts(self.EVHOME))
            _ld_lib_path_parts.extend(_dgi_ld_lib_path(self.EVHOME))
        _path_parts.append(env_dict()["PATH"])
        try:
            _ld_lib_path_parts.append(env_dict()["LD_LIBRARY_PATH"])
        except KeyError:
            pass

        return {
            "PATH": _lin_path(":".join(_path_parts)),
            "LD_LIBRARY_PATH": _lin_path(":".join(_ld_lib_path_parts)),
        }

    def _win_env(self) -> dict[str, str]:
        """Get current windows environment path"""
        _path_parts = []
        if self.COVIZHOME != "":
            _path_parts.extend(_dgi_path_parts(self.COVIZHOME))

        if self.EVHOME != "":
            _path_parts.extend(_dgi_path_parts(self.EVHOME))

        if self.WAHOME != "":
            _path_parts.extend(_dgi_path_parts(self.WAHOME))

        if self.MSYSPATH != "":
            _path_parts.append(self.MSYSPATH)
        _path_parts.append(env_dict()["PATH"])
        return {"PATH": _win_path(";".join(_path_parts))}

    @property
    def environment(self) -> dict[str, str]:
        """Return the current environment as a dictionary

        Returns:
            Dictionary of env variables

        """
        self.refresh_env_vars()
        _os_env = self._win_env() if is_win() else self._lin_env()
        return {
            **dict(environ.items()),
            **_os_env,
            **_load_config_env_vars(),
        }

    def set_verbose(self, *, value: bool) -> None:
        """Set the verbose field of the global DgiConfig object

        Args:
            value: Boolean value to set the config class verbosity

        Returns:
            None

        """
        self.verbose = value

    def pformat(self) -> str:
        """Return a pretty-formatted string of the DgiConfig object"""
        return pfmt(self)

    def _check_covizhome(self) -> None:
        """Check if COVIZHOME system environment variable exists and is valid"""
        if self.COVIZHOME != "" and not Path(self.COVIZHOME).exists():
            raise OSError(
                f"COVIZHOME invalid: {self.COVIZHOME}\nDgiConfig({self.pformat()})"
            )

    def _check_evhome(self) -> None:
        """Check if EVHOME system environment variable exists and is set to a valid path"""
        if not (self.EVHOME != "" and Path(self.EVHOME).exists()):
            raise OSError(f"EVHOME invalid: {self.EVHOME}\nDgiConfig({self.pformat()})")

    def _check_wahome(self) -> None:
        """Check if WAHOME system environment variable exists and is set to a valid path"""
        if not (self.WAHOME != "" and Path(self.WAHOME).exists()):
            raise OSError(f"WAHOME invalid: {self.WAHOME}\nDgiConfig({self.pformat()})")

    @classmethod
    def from_json(cls, json_string: bytes | str) -> DgiConfig:
        """Return a `DgiConfig` object from a JSON string"""
        return cls(**JSON.loads(json_string))

    def to_json(
        self,
        *,
        fmt: bool = False,
        pretty: bool = False,
        sort_keys: bool = False,
        append_newline: bool = False,
        default: Callable[[Any], Any] | None = None,
        **kwargs: Any,
    ) -> str:
        return JSON.dumps(
            self.model_dump(),
            fmt=fmt,
            pretty=pretty,
            sort_keys=sort_keys,
            append_newline=append_newline,
            default=default,
            **kwargs,
        )


@lru_cache(maxsize=32)
def _dgi_path_parts(root_dirpath: FsPath) -> list[str]:
    """Get list of paths needed for DGI bins"""
    if not isinstance(root_dirpath, str):
        return _dgi_path_parts(str(root_dirpath))
    return [
        path.join(root_dirpath, "bin64"),
        path.join(root_dirpath, "scripts"),
        path.join(root_dirpath, "python_bin"),
    ]


@lru_cache(maxsize=32)
def _dgi_ld_lib_path(root_dirpath: FsPath) -> list[str]:
    """Get list of paths needed for DGI bins"""
    if not isinstance(root_dirpath, str):
        return _dgi_ld_lib_path(str(root_dirpath))
    return [
        path.join(root_dirpath, "lib64"),
        path.join(root_dirpath, "lib"),
    ]


@lru_cache(maxsize=32)
def _lin_path(pth: str) -> str:
    """Re-makes linux path string to remove duplicate directories

    Args:
        pth (str): Original linux path string

    Returns:
        Linux path string with duplicate directory paths removed
    """
    return ":".join(unique_gen(el for el in pth.split(":") if el != ""))


@lru_cache(maxsize=32)
def _win_path(pth: str) -> str:
    """Remakes windows path string to remove duplicate directories

    Args:
        pth (str): Original windows path string

    Returns:
        Windows path string with duplicate directory paths removed
    """
    return ";".join(unique_gen(el for el in pth.split(";") if el != ""))


def _load_config_file(filepath: str) -> Any | None:
    """Load config file from fspath and gives a config dictionary of file contents

    Args:
        filepath (str): Path to DGPY config file (can be any valid config format)

    Returns:
        Dictionary of loaded config file contents

    """
    if not path.exists(filepath):
        return None
    if filepath.endswith(".json"):
        return fs.read_json(filepath)
    raise ValueError("Something went wrong here in the _config")


def _find_config_file_in_dir(dirpath: FsPath) -> str | None:
    """Give fspath of valid config file given a potential file-containing directory atph

    Args:
        dirpath (str): Directory path in which to find config file

    Returns:
        Filepath of config file if it exists in the particular directory

    """
    for filename in _CONFIG_FILENAMES:
        _config_filepath = path.join(str(dirpath), filename)
        if path.exists(_config_filepath):
            return _config_filepath
    return None


def _config_filepaths() -> Iterator[str]:
    """Give a tuple of valid config filepaths based on the current directory"""
    return (
        path.join(_dirpath, _filename)
        for _filename in _CONFIG_FILENAMES
        for _dirpath in (getcwd(), _HOMEDIRPATH)
    )


def _load_config_env_vars() -> dict[str, str]:
    """Get current environment's env variables"""
    # get it again here so it allows for changes
    _env = dict(env_dict())
    return {
        **{k: _env[k] for k in _DGI_ENV_VARS if k in _env and path.exists(_env[k])},
        **{k: _env[k] for k in _ENV_VARIABLES if k in _env},
    }


def dgi_module() -> types.ModuleType:
    """Return the appropriate module based on which env variable is set."""
    # set module name appropriately based on env variable
    env_coviz = environ.get("COVIZHOME")
    env_ev = environ.get("EVHOME")
    env_wa = environ.get("WAHOME")

    if env_coviz:
        from dgpy import cv

        return cv
    elif env_ev:
        from dgpy import ev

        return ev
    elif env_wa:
        from dgpy import wa

        return wa
    else:
        raise ImportError(
            "One of COVIZHOME, EVHOME, or WAHOME env variables must be set."
        )


def load_config() -> DgiConfig:
    """Load the dgi configuration object and return the loaded object

    Returns:
        Return the a DgiConfig object containing all config settings according
        environment variables and/or configuration files

    """
    _env = env_dict()
    _configs = list(
        reversed(
            list(filter(None, (_load_config_file(fp) for fp in _config_filepaths())))
        )
    )

    # Add to the end of the configs list the config variables according to env
    # variables; pref is also added in addition to 'DGI-HOME' paths
    _pref = ""
    if "PREF" in _env and _env["PREF"].lower().strip("_") in {"cv", "ev", "wa"}:
        _pref = _env["PREF"].lower().strip("_")
    _configs.append({
        **_load_config_env_vars(),
        "PREF": _pref,
        "TESHTING": _env.get("TESHTING", "").lower()
        not in (
            "0",
            "false",
        ),
    })
    # Priority is home-config < local-config < env-variables
    # By doing chain from iterable and making it into a dict, the last items
    # overwrite the first items
    return DgiConfig(**dict(chain.from_iterable(d.items() for d in _configs)))


__config__ = load_config()


def config() -> DgiConfig:
    """Return the global DgpyConfig object (which is a dictionary)

    Returns:
        DgiConfig: Configuration object

    """
    global __config__
    if __config__ is None:
        __config__ = load_config()
    return __config__


def set_verbose(value: bool | None = None) -> None:  # noqa: FBT001
    """Set verbosity of logging level in DGPY config"""
    _config: DgiConfig = config()
    if value is None:
        value = not _config.verbose
    _config.verbose = value


def get_dgpy_pkg_location() -> str:
    """Return the installed DGPY package location dirpath as a string

    Returns:
        Path to installed DGPY package

    """
    return path.split(path.realpath(__file__))[0]
