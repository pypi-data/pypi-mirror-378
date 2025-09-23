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
"""DGI Exe Wrapping"""

from __future__ import annotations

from functools import cache
from itertools import chain
from os import environ, path
from pathlib import Path
from shlex import split as shplit
from typing import TYPE_CHECKING, Any, TypeAlias

from fmts import pstr
from jsonbourne import JSON
from listless import flatten_strings
from pydantic import field_validator
from shellfish import fs, sh
from shellfish.process import is_win, sys_path_sep
from shellfish.sh import Done, do, do_async
from typing_extensions import override

from dgpy.const import DGI_ENV_VARS
from dgpy.core.config import config
from dgpy.core.enums.prefix import DgiPref, dgi_module_functions
from dgpy.dgpydantic import DgpyBaseModel
from dgpy.ex import DgpyError
from dgpy.utils import hash

if TYPE_CHECKING:
    from collections.abc import Coroutine, Iterable
    from types import ModuleType

    from dgpy._types import FsPath

__all__ = (
    "ExeFunction",
    "ExeFunctionAsync",
    "ExeInfo",
    "ExeResponse",
    "ExeRunRequest",
    "exe2pyfn",
    "exe_function_name",
    "funkify_mod",
)

STDIN: TypeAlias = bytes | str | None


class ExeRunRequest(DgpyBaseModel):
    """Params for running an exe-function"""

    args: list[str]
    env: dict[str, str] | None = None
    cwd: str | None = None
    verbose: bool | None = False
    stdin: STDIN | None = None
    timeout: int | None = None
    exe: str | None = None

    def __post_init__(self) -> None:
        """Post init"""
        self.args = list(flatten_strings(self.args))

    @field_validator("args", mode="before")
    @classmethod
    def _validate_args(cls, v: list[str] | str | tuple[str, ...]) -> list[str]:
        val = shplit(v) if isinstance(v, str) else v
        return list(flatten_strings(val))


class ExeResponse(DgpyBaseModel):
    """Pydantic model for ExeResponse for use with FastAPI"""

    run: ExeRunRequest
    done: Done


class ExeInfo(DgpyBaseModel):
    """Exe info container"""

    help: str
    version: str
    which: str
    sha256: str | None
    md5: str | None
    size: int | None


_exe_info_cache: dict[str, ExeInfo] = {}


def _env(env: dict[str, str] | None = None) -> dict[str, str]:
    if env is None:
        env = {}
    return {**config().environment, **env}


class ExeFunction:
    """Exe function wrapper callable method"""

    __slots__ = ("_args", "_cache", "_help", "_verbose", "exe", "name")
    name: str
    exe: str
    _args: tuple[Any, ...] | None
    _help: str | None
    _verbose: bool | None

    def __init__(
        self,
        name: str,
        exe: str,
    ) -> None:
        """Construct ExeFunction

        Args:
            name (str): Name of the function; `cv_dump` would be `dump`
            exe (str): Exe string `cv_dump` would be `cv_dump`

        """
        self.name = name
        self.exe = exe
        self._args = None
        self._verbose = None
        self._help = None

    def __str__(self) -> str:
        """Return string representation of ExeFunction object"""
        return f"<dgpy.{self.pref}.{self.name} Function>"

    def __repr__(self) -> str:
        """Return string representation of ExeFunction object"""
        return self.__str__()

    def _get_help_str(self) -> str:
        """Get the help message for the function and cache if for later

        Equivalent to calling the function with the argument '-V'

        Returns:
            str: exe help message

        """
        if self._help:
            return self._help
        help_proc = self.run("-h")
        help_str = help_proc.stdout or help_proc.stderr
        self._help = help_str
        return help_str

    @property
    def __doc__(self) -> str:  # type: ignore[override]
        """Get the help message for the function and cache if for later

        Equivalent to calling the function with the argument '-V'

        Returns:
            str: exe help message

        """
        return self._get_help_str()

    @property
    def help(self) -> pstr:
        """Return exe help message/docstring/__doc__"""
        return pstr(self._get_help_str())

    H = help
    h = help

    def _get_version_str(self) -> str:
        """Get the version message for the function and cache if for later

        Equivalent to calling the function with the argument '-V'

        Returns:
            str: exe version message

        """
        version_proc = self.run("-V")
        version_str = version_proc.stdout or version_proc.stderr
        return version_str

    @property
    def version(self) -> str:
        """Get the version message for the function and cache if for later

        Equivalent to calling the function with the argument '-V'

        Returns:
            str: exe version message

        """
        return pstr(self._get_version_str())

    V = version  # alias for calling exe.version

    @property
    def pref(self) -> str:
        """Return exe prefix"""
        pref = self.exe.split("_")[0]
        if pref not in {"cv", "ev", "wa"}:
            raise ValueError(f"Invalid exe prefix: {pref}")
        return pref

    def prefix_suffix(self) -> tuple[str, str]:
        """Return prefix (cv/ev/wa) and suffix (dump/stat/exe-name)"""
        pref, _, suf = self.exe.partition("_")
        return pref, suf

    def suffix(self) -> str:
        """Return the suffix/exe name without `cv_`/`ev_`/`wa_`"""
        _, _, suf = self.exe.partition("_")
        return suf

    @property
    def env_variable(self) -> str:
        """Return the affiliated env var for the exe; 'COVIZHOME'/'EVHOME'/'WAHOME'"""
        return DGI_ENV_VARS[self.pref]

    def _check_env(self) -> None:
        if self.env_variable not in environ:
            raise OSError(f"Environment Variable not set: {self.env_variable}")
        if not path.exists(environ[self.env_variable]):
            raise OSError(
                f"Environment Variable set but path does not exist: {self.env_variable}"
            )

    def __which__(self) -> str | None:
        return sh.which_lru(self.exe, path=_env()["PATH"])

    @property
    def which(self) -> str | None:
        """Return the location of the wrapped exe"""
        return self.__which__()

    @property
    def where(self) -> str | None:
        """Return the location of the wrapped exe"""
        return self.__which__()

    def _validate_args(self, args: tuple[Any, ...]) -> list[str]:
        if len(args) == 1 and isinstance(args[0], str):
            _args_list = shplit(args[0])
        else:
            _args_list = list(flatten_strings(*args))
        if _args_list and _args_list[0] == self.exe:
            _args_list = _args_list[1:]
        return _args_list

    def run_exe_params(self, params: ExeRunRequest) -> Done:
        """Call (sync) the function given an exe-params object"""
        return self.run(
            *params.args,
            env=params.env,
            cwd=params.cwd,
            verbose=params.verbose,
            input=params.stdin,
            timeout=params.timeout or 3600,
        )

    def run_request(self, params: ExeRunRequest) -> ExeResponse:
        """Run exe using params from ExeRunRequest object"""
        _done = self.run_exe_params(params)
        params.exe = self.exe
        return ExeResponse(
            done=_done,
            run=params,
        )

    def run(
        self,
        *args: str | list[str] | tuple[str],
        input: STDIN = None,
        stdin: STDIN = None,
        pipe: bool = False,
        env: dict[str, str] | None = None,
        shell: bool = False,
        prepend_path: str | None = None,
        verbose: bool | None = None,
        cwd: FsPath | None = None,
        timeout: int = 3600,
        check: bool = True,
    ) -> Done:
        """Call (SYNC) the function for the exe taking the string args as params

        Args:
            input (str): Stdin input
            stdin (str): Stdin input (alias for input)
            pipe (bool): Allow operator piping
            env (dict[str, str]): Environment dictionary to overlay onto env
            shell (bool): Run subprocess in running shell if True
            prepend_path (str, optional): Prepend to PATH environment variable
            check (bool): Check output
            timeout (int): Timeout in seconds; default is 3600
            cwd (Optional[FsPath]): Directory to run process in
            verbose (bool): Write exe process stdout/stderr to sys.stdout/sys.stderr
            *args: arguments as strings

        Returns:
            The finished result as a dictionary

        """
        if input and stdin:
            raise ValueError("Cannot give `input` and `stdin` kwargs")
        if len(args) == 1 and isinstance(args[0], ExeRunRequest):
            return self.run_exe_params(args[0])

        if env is None:
            env = {}
        _env = {**config().environment, **env}
        if prepend_path:
            _env["PATH"] = f"{prepend_path}{sys_path_sep()}{_env['PATH']}"
        self._verbose = config().verbose
        if verbose is not None:
            self._verbose = verbose

        _stdin = None
        if input or stdin:
            _stdin = input or stdin

        self._args = args
        if pipe:
            return self  # type: ignore

        if args or _stdin:
            exe_name = self.exe
            _args_list = self._validate_args(args)

            cmd_args = [exe_name, *_args_list]
            try:
                _run_info = do(
                    args=cmd_args,
                    env=_env,
                    verbose=self._verbose,
                    input=_stdin,
                    shell=shell,
                    cwd=cwd,
                    timeout=timeout,
                    check=check,
                )
            except FileNotFoundError as fnfe:
                self._check_env()
                if is_win():
                    cmd_args = [exe_name + ".bat", *_args_list]
                    _run_info = do(
                        args=cmd_args,
                        env=_env,
                        verbose=self._verbose,
                        input=_stdin,
                        shell=shell,
                        cwd=cwd,
                        timeout=timeout,
                        check=check,
                    )
                else:
                    raise fnfe
            self._verbose = False
            return _run_info
        return self  # type: ignore

    async def run_exe_params_async(self, params: ExeRunRequest) -> Done:
        """Call (sync) the function given an exe-params object"""
        return await self.run_async(
            *params.args,
            env=params.env,
            cwd=params.cwd,
            verbose=params.verbose,
            input=params.stdin,
            timeout=params.timeout or 3600,
        )

    async def run_request_async(self, params: ExeRunRequest) -> ExeResponse:
        """Run exe async using params from ExeRunRequest object"""
        _done = await self.run_exe_params_async(params)
        params.exe = self.exe
        return ExeResponse(
            done=_done,
            run=params,
        )

    async def run_async(
        self,
        *args: Any,
        input: STDIN = None,
        stdin: STDIN = None,
        pipe: bool = False,
        env: dict[str, str] | None = None,
        shell: bool = False,
        verbose: bool | None = None,
        cwd: FsPath | None = None,
        timeout: int = 3600,
    ) -> Done:
        """Call the function for the exe taking the string args as params

        Args:
            *args: arguments as strings
            input: Optional stdin
            stdin: Optional stdin (alias for input)
            pipe (bool): Flag to expect more stdin and return a pipe-able function
            env: Environment mapping to run using
            shell (bool): Run command in shell
            prepend_path (Optional[str]): Prepend to PATH environment variable
            verbose (Optional[bool]): Flag to run command and output stdout/stderr
            cwd: Path to directory to run command in
            timeout (int): Timeout for the command
            check (bool): Check output based on return code; default is True
            **kwargs: keyword arguments that can be accepted

        Returns:
            The finished result as a dictionary

        """
        if input and stdin:
            raise ValueError("Cannot give `input` and `stdin` kwargs")
        if args and len(args) > 0 and isinstance(args[0], ExeRunRequest):
            if len(args) > 1:
                raise ValueError("Cannot give multiple ExeRunRequest")
            return await self.run_exe_params_async(args[0])

        if env is None:
            env = {}
        _env = {**config().environment, **env}
        self._verbose = config().verbose
        if verbose is not None:
            self._verbose = verbose

        _stdin = None
        if input or stdin:
            _stdin = input or stdin

        self._args = args
        if pipe:
            return self  # type: ignore

        if args or _stdin:
            exe_name = self.exe
            _args_list = self._validate_args(args)
            cmd_args = [exe_name, *_args_list]
            try:
                _run_info = await do_async(
                    args=cmd_args,
                    env=_env,
                    verbose=self._verbose,
                    input=_stdin,
                    shell=shell,
                    cwd=None if cwd is None else str(cwd),
                    timeout=timeout,
                )
            except FileNotFoundError as fnfe:
                self._check_env()
                if is_win():
                    cmd_args = [exe_name + ".bat", *_args_list]
                    _run_info = await do_async(
                        args=cmd_args,
                        env=_env,
                        verbose=self._verbose,
                        input=_stdin,
                        shell=shell,
                        cwd=None if cwd is None else str(cwd),
                        timeout=timeout,
                    )
                else:
                    raise fnfe
            self._verbose = False
            return _run_info
        return self  # type: ignore

    def __call__(
        self,
        *args: Any,
        input: STDIN = None,
        stdin: STDIN = None,
        pipe: bool = False,
        env: dict[str, str] | None = None,
        shell: bool = False,
        prepend_path: str | None = None,
        verbose: bool | None = None,
        cwd: FsPath | None = None,
        timeout: int = 3600,
        check: bool = True,
        **kwargs: Any,
    ) -> Done:
        """Call the function for the exe taking the string args as params

        Args:
            *args: arguments as strings
            input: Optional stdin
            stdin: Optional stdin (alias for input)
            pipe (bool): Flag to expect more stdin and return a pipe-able function
            env: Environment mapping to run using
            shell (bool): Run command in shell
            prepend_path (Optional[str]): Prepend to PATH environment variable
            verbose (Optional[bool]): Flag to run command and output stdout/stderr
            cwd: Path to directory to run command in
            timeout (int): Timeout for the command
            check (bool): Check output based on return code; default is True
            **kwargs: keyword arguments that can be accepted

        Returns:
            The finished result as a dictionary

        """
        return self.run(
            *args,
            input=input,
            stdin=stdin,
            pipe=pipe,
            env=env,
            shell=shell,
            prepend_path=prepend_path,
            verbose=verbose,
            cwd=cwd,
            timeout=timeout,
            check=check,
        )

    def pipe_bytes(self, bites: str | bytes) -> Done:
        """Pipe bytes handler function"""
        if isinstance(bites, str) or isinstance(bites, bytes):
            _args: list[str] = []
            if self._args:
                _args = list(self._args)
            return self.run(*_args, input=bites, verbose=self._verbose)

        raise ValueError(
            "Must give string or bytes as stdin/stdin;\n"
            f"Given: {bites} (type={type(bites)})"
        )

    def __lshift__(self, pipe_stdin: str | bytes) -> Done:
        """Pipe string/bytes faux 'input' into function using `<<` operator"""
        return self.pipe_bytes(pipe_stdin)

    def __ror__(self, pipe_stdin: str | bytes) -> Done:
        """Pipe string/bytes faux 'input' into function using `|` operator"""
        return self.pipe_bytes(pipe_stdin)

    def pipe_filepath(self, filepath: FsPath) -> Done:
        """Allow fspath contents to be piped into exe function"""
        _path = Path(filepath)
        if not _path.exists():
            raise ValueError(f"Unable to find fspath: {_path}")
        return self.run(input=_path.read_bytes(), verbose=self._verbose)

    def __lt__(self, filepath: FsPath) -> Done:
        """Pipe fspath into function call using `<`"""
        return self.pipe_filepath(filepath)

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "pref": self.pref,
            "exe": self.exe,
            "env_var": self.env_variable,
            "help_str": self.help,
            "version_str": self.version,
        }

    def to_json(self) -> str:
        return JSON.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, dictionary: dict[str, Any]) -> ExeFunction:
        if "name" not in dictionary:
            raise ValueError(f"'name' key not in given dictionary: {dictionary}")
        if "exe" not in dictionary:
            raise ValueError(f"'exe' key not in given dictionary: {dictionary}")
        return cls(**{
            k: v
            for k, v in dictionary.items()
            if k in ("name", "exe", "help_str", "version_str")
        })

    @classmethod
    def from_json(cls, json_str: str) -> ExeFunction:
        return cls.from_dict(JSON.loads(json_str))

    def exe_info(self) -> ExeInfo:
        """Return ExeInfo object for ExeFunction (SYNC)"""
        _location = self.which
        if _location is None:
            raise DgpyError(f"EXE not found: {self.exe}")
        _md5 = str(hash.md5_filepath(_location))
        _sha256 = str(hash.sha256_filepath(_location))
        _size = fs.filesize(_location)
        return ExeInfo(
            help=str(self.help),
            version=str(self.version),
            which=_location,
            md5=_md5,
            sha256=_sha256,
            size=_size,
        )

    async def exe_info_async(self) -> ExeInfo:
        """Return ExeInfo object for ExeFunction (ASYNC)"""
        _location = self.which
        if _location is None:
            raise DgpyError(f"EXE not found: {self.exe}")
        _size = await fs.filesize_async(_location)
        _md5 = await hash.md5_filepath_async(_location)
        _sha256 = await hash.sha256_filepath_async(_location)
        return ExeInfo(
            help=self.help,
            version=self.version,
            which=_location,
            md5=str(_md5),
            sha256=str(_sha256),
            size=_size,
        )

    async def exe_info_cached_async(self) -> ExeInfo:
        """Return ExeInfo object for ExeFunction (ASYNC)"""
        _location = self.which
        if _location is None:
            raise DgpyError(f"EXE not found: {self.exe}")
        try:
            return _exe_info_cache[_location]
        except KeyError:
            pass
        einfo = await self.exe_info_async()
        _exe_info_cache[_location] = einfo
        return einfo


class ExeFunctionAsync(ExeFunction):
    """Exe function wrapper callable method"""

    async def __call__(  # type: ignore
        self,
        *args: Any,
        input: STDIN = None,
        stdin: STDIN = None,
        pipe: bool = False,
        env: dict[str, str] | None = None,
        shell: bool = False,
        verbose: bool | None = None,
        cwd: FsPath | None = None,
        timeout: int = 3600,
        **kwargs: Any,
    ) -> Done:
        """Call the function for the exe taking the string args as params

        Args:
            *args: arguments as strings
            input: Optional stdin
            stdin: Optional stdin (alias for input)
            pipe (bool): Flag to expect more stdin and return a pipe-able function
            env: Environment mapping to run using
            shell (bool): Run command in shell
            prepend_path (Optional[str]): Prepend to PATH environment variable
            verbose (Optional[bool]): Flag to run command and output stdout/stderr
            cwd: Path to directory to run command in
            timeout (int): Timeout for the command
            check (bool): Check output based on return code; default is True
            **kwargs: keyword arguments that can be accepted:

        Returns:
            The finished result as a dictionary

        """
        return await self.run_async(
            *args,
            input=input,
            stdin=stdin,
            pipe=pipe,
            env=env,
            shell=shell,
            verbose=verbose,
            cwd=cwd,
            timeout=timeout,
        )

    @override
    async def pipe_bytes(self, bites: str | bytes) -> Done:  # type: ignore[override]
        """Pipe bytes handler function"""
        if isinstance(bites, str) or isinstance(bites, bytes):
            _args: list[str] = []
            if self._args:
                _args = list(self._args)
            r = await self.run_async(*_args, input=bites, verbose=self._verbose)
            return r

        raise ValueError(
            "Must give string or bytes as stdin/stdin;\n"
            f"Given: {bites} (type={type(bites)})"
        )

    def __lshift__(self, pipe_stdin: str | bytes) -> Coroutine[Any, Any, Done]:  # type: ignore[override]
        return self.pipe_bytes(pipe_stdin)

    def __ror__(self, pipe_stdin: str | bytes) -> Coroutine[Any, Any, Done]:  # type: ignore[override]
        return self.pipe_bytes(pipe_stdin)

    async def pipe_filepath(self, filepath: FsPath) -> Done:  # type: ignore[override]
        """Allow fspath contents to be piped into exe function"""
        _path = Path(filepath)
        if not _path.exists():
            raise ValueError(f"Unable to find fspath: {_path}")
        return await self.run_async(input=_path.read_bytes(), verbose=self._verbose)

    @override
    def __lt__(self, filepath: FsPath) -> Coroutine[Any, Any, Done]:  # type: ignore[override]
        """Pipe fspath into function call using `<`"""
        return self.pipe_filepath(filepath)


def kwargs_2_cmd(**kwargs: str) -> Iterable[str]:
    """Convert key-word arguments to command line arguments for the shell

    Args:
        **kwargs: Dictionary of keyword arguments

    Returns:
        Iterable of strings

    """
    return chain.from_iterable((f"-{k}", v) for k, v in kwargs.items())


def exe_function_name(exe_name: str) -> tuple[str, str]:
    """Get the exe python-function name(s) for a given dgi function

    Args:
        exe_name: exe name without the prefix

    Returns:
        Tuple(s) containing the function name and the affiliated exe name

    """
    if exe_name.startswith(("2", "3", "4")) or exe_name == "import":
        return (f"_{exe_name}", exe_name)
    return (exe_name, exe_name)


@cache
def exe2pyfn(exe_name: str, *, _async: bool = False) -> str:
    """Translate an exe name to a python function name"""
    if _async:
        return f"{exe2pyfn(exe_name, _async=False)}_async"
    if exe_name == "import":
        return "_import"
    if exe_name.startswith(("2", "3", "4")):
        return f"_{exe_name}"
    return exe_name


def _exe_string(prefix: str, exe_name: str) -> str:
    return f"{prefix}_{exe_name}"


def funkify_mod(mod: ModuleType, prefix: str | DgiPref | None = None) -> None:
    """Add functions to a module

    Args:
        mod: Module to add functions to
        prefix: dgi exe prefix for the wrapper function

    Returns:
        None

    ------------------------------------------------
    slightly more readable version (commented out)
    ------------------------------------------------

    _function_names_n_exes = chain.from_iterable(
        exe_function_name(exe_name) for exe_name in _module_exes
    )
    _functions = (
        (func_name, ExeFunction(func_name, exe_name, mod))
        for func_name, exe_name in _function_names_n_exes
    )

    ---------------------------------------
    unreadable version (BUT FASTER) version
    ---------------------------------------

    _fname_exe_name = list(
        chain.from_iterable(
            exe_function_name(exe_name) for exe_name in _module_exes
        )
    )

    """
    if prefix is None:
        prefix = mod.__name__.split(".")[-1]
    # ------------------------------------------------
    # unreadable; see docstring for a readable version
    # ------------------------------------------------
    _module_exes = dgi_module_functions(prefix)
    _fname_exe_name = list(map(exe_function_name, _module_exes))
    _async_fname_exe_name = [
        (f"{func_name}_async", exe_name) for func_name, exe_name in _fname_exe_name
    ]
    _module_functions = [
        *(
            (fname, ExeFunction(name=fname, exe=_exe_string(prefix, exe_name)))
            for fname, exe_name in _fname_exe_name
        ),
        *(
            (fname, ExeFunctionAsync(name=fname, exe=_exe_string(prefix, exe_name)))
            for fname, exe_name in _async_fname_exe_name
        ),
    ]
    setattr(  # noqa
        mod, "__all__", (*(func_name for func_name, _ in _module_functions),)
    )
    for fname, funk in _module_functions:
        setattr(mod, fname, funk)
    setattr(mod, "__FUNCTIONS__", dict(_module_functions))  # noqa
