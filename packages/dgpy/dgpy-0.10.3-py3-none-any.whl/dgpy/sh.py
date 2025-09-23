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
"""Shell utilities and functions for dgpy/python

`from dgpy import sh`
"""

from __future__ import annotations

from functools import update_wrapper
from pathlib import Path
from platform import system
from typing import TYPE_CHECKING, Any, TypeAlias, TypeVar

import shellfish as sh

from shellfish.process import is_win

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable

    from dgpy._types import FsPath

T = TypeVar("T")
# =============================================================================
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
# =============================================================================
#  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\
# /  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \
# =============================================================================
# \/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
# =============================================================================
IS_WIN: bool = is_win()

Pipeable: TypeAlias = sh.Done | str | bytes


class PipeStdin:
    """Allows for 'piping' stdin to a function that has 'stdin' as a kwarg"""

    function: Callable[..., Any]

    def __init__(self, function: Callable[..., T]) -> None:
        """Construct a PipeStdin object

        Args:
            function: Decorated function whose name is to be preserved as base
                function name with update_wrapper

        """
        self.function = function
        update_wrapper(self, function)

    def __ror__(self, other: str) -> str:
        """Overloaded | (pipe) operator to allow for literal piping in python code

        [sh.cat(thing) | sh.grep("pattern")]

        Args:
            other: Target function into which stdout should be piped as
                stdin (function after | operator)

        Returns:
            Function handle of target function

        """
        return str(self.function(stdin=other))

    def __call__(self, *args: Any, **kwargs: Any) -> PipeStdin | str:
        """Wrap the function and give input as stdin

        Args:
            *args: The function's original args
            **kwargs: The function's original kwargs

        Returns:
            Function handle with stdin piped as a key word argument to the function

        """
        if "stdin" in kwargs and kwargs["stdin"] is not None:
            return str(self.function(*args, **kwargs))

        def _wrapper(*_args: Any, **_kwargs: Any) -> str:
            """Call and return the result of the wrapped function"""
            return self.function(*(*args, *_args), **{**kwargs, **_kwargs})

        return PipeStdin(_wrapper)


# =============================================================================
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
# =============================================================================
#  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\  /\
# /  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \/  \
# =============================================================================
# \/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
# =============================================================================


async def cp_file_async(src_filepath: str, dest_filepath: str) -> None:
    """Copy a file (ASYNC)

    Args:
        src_filepath: Source fspath
        dest_filepath: Destination fspath

    """

    async def _bytes_only_gen() -> AsyncGenerator[bytes, None]:
        async for chunk in sh.read_bytes_gen_async(src_filepath):
            if isinstance(chunk, str):
                yield chunk.encode()
            else:
                yield chunk

    await sh.write_bytes_gen_async(dest_filepath, _bytes_only_gen())


async def sync_async(src: str, dest: str) -> None:
    """Sync the contents of two directories given their paths

    Args:
        src: Source directory
        dest: Destination directory

    """
    dirs = (
        (dirpath, dirpath.replace(src, dest))
        for dirpath in sh.dirs_gen(src, abspath=True)
    )
    for _srcdirpath, destdirpath in dirs:
        try:
            sh.mkdir(destdirpath)
        except FileExistsError:
            ...

    filepaths = (
        (filepath, filepath.replace(src, dest))
        for filepath in sh.files_gen(src, abspath=True)
    )

    for src_filepath, dest_filepath in filepaths:
        await cp_file_async(src_filepath, dest_filepath)


def chmod777(filepath: str, *, raise_permission_error: bool = True) -> bool:
    """Change permissions of a specified file to 777 [rwxrwxrwx]

    777 => no restrictions on file usage (be careful!)

    Args:
        filepath (str): File path to file for which to change permissions
        raise_permission_error (bool): Raise `PermissionError` if encountered

    Returns:
        bool: True if the mod was ch-ed

    Raises:
        PermissionError: if except_permission_error is True

    """
    if "windows" not in system().lower():
        try:
            sh.chmod(filepath, 0o777)
            return True
        except PermissionError as e:
            if raise_permission_error:
                raise e
    return False


@PipeStdin
def head(
    stdin: Pipeable | None = None,
    *,
    n: int = 10,
    _checkpath: bool = True,
    verbose: bool = False,
) -> str | PipeStdin:
    """Give the first [n] lines of given stdin object

    Args:
        stdin: Piped stdin object (bytes or PRun or string) from which to
            return lines
        n (int): Number of lines to return from beginning of stdin
        _checkpath (bool): If TRUE, confirms if path to stdin exists before
            executing
        verbose (bool): If TRUE, runs the function in verbose mode (prints out
            return string as well as returning)

    Returns:
        String of first [n] lines of given stdin

    Raises:
        ValueError: if stdin is not of type bytes, PRun, or string


    """
    if isinstance(stdin, sh.Done):
        stdin = stdin.stdout
    if isinstance(stdin, bytes):
        stdin = stdin.decode()
    if isinstance(stdin, str):
        if _checkpath:
            _path = Path(stdin)
            try:
                if _path.exists():
                    string = sh.read_str(str(_path))
                    return head(stdin=string, n=n, _checkpath=False)
            except OSError:
                ...

        lines = stdin.splitlines(keepends=False)

        _s = "\n".join(lines[:n])
        if verbose:
            sh.echo(_s)
        return str(_s)
    raise ValueError(f"Unexpected argument (type={type(stdin)}): {stdin}")


@PipeStdin
def tail(
    stdin: Pipeable | None = None,
    *,
    n: int = 10,
    _checkpath: bool = True,
    verbose: bool = False,
) -> str | PipeStdin:
    """Give the last [n] lines of given stdin object

    Args:
        stdin: Piped stdin object (bytes or PRun or string) from which to
            return lines
        n (int): Number of lines to return from end of stdin
        _checkpath (bool): If TRUE, confirms if path to stdin exists before
            executing
        verbose (bool): If TRUE, runs the function in verbose mode (prints
            out return string as well as returning)

    Returns:
        String of last [n] lines of given stdin

    Raises:
        ValueError: if stdin is not of type bytes, PRun, or string

    """
    if isinstance(stdin, sh.Done):
        stdin = stdin.stdout
    if isinstance(stdin, bytes):
        stdin = stdin.decode()
    if isinstance(stdin, str):
        if _checkpath:
            _path = Path(stdin)
            try:
                if _path.exists():
                    string = sh.read_str(str(_path))
                    return tail(stdin=string, n=n, _checkpath=False)
            except OSError:
                ...
        lines = stdin.splitlines(keepends=False)
        _s = "\n".join(lines[-n:])
        if verbose:
            sh.echo(_s)
        return _s
    raise ValueError(f"Unexpected argument (type={type(stdin)}): {stdin}")


@PipeStdin
def grep(
    pattern: str, stdin: Pipeable | None = None, *, verbose: bool = False
) -> str | PipeStdin:
    """Find given pattern in stdin and outputs lines containing the given pattern

    Args:
        pattern (str): String pattern to match in the given stdin
        stdin: Piped stdin object (bytes/string/Done) to search for pattern
        verbose (bool): runs function in verbose mode printing results

    Returns:
        String of lines containing the given pattern

    Raises:
        ValueError: if stdin is not of type bytes, PRun, or string

    """
    if isinstance(stdin, sh.Done):
        stdin = stdin.stdout
    if isinstance(stdin, bytes):
        stdin = stdin.decode()
    if isinstance(stdin, str):
        _s = "\n".join(
            str_line
            for str_line in stdin.splitlines(keepends=False)
            if pattern in str_line
        )
        if verbose:
            sh.echo(_s)
        return _s
    raise ValueError(f"Stdin type (type: {type(stdin)!s}) not supported")


def cat(stdin: str, *, _checkpath: bool = True) -> str:
    """Return content string or strings cot-ed together from stdin or filepaths

    Args:
        stdin: Piped stdin object (bytes or PRun or string) from which to
            generate content string
        _checkpath (bool): If TRUE, confirms if path to stdin exists before
            executing

    Returns:
        String of stdin content

    Raises:
        ValueError: if stdin is not of type bytes, PRun, or string

    """
    if isinstance(stdin, bytes):
        stdin = stdin.decode()
    if _checkpath:
        _path = Path(stdin)
        if _path.exists():
            return sh.read_str(str(_path))
    raise ValueError("im tired; finish this later")


def _parse_ldd_stdout(string: str) -> dict[str, str | None]:
    """Parse the output from running ldd"""
    lines = [el.strip("\t") for el in string.splitlines(keepends=False)]
    pairs = [
        (el[0], el[2]) if "=>" in el else (el[0], None)
        for el in [line.split(" ") for line in lines]
    ]
    return dict(pairs)


def ldd(filepath: FsPath) -> dict[str, str | None]:
    """Parse and return results ldd as a dictionary of so-name => so-path

    Args:
        filepath: Path to executable to LDD

    Returns:
        Dictionary of libs where keys are lib-name and value is lib-fspath

    Raises:
        OSError: if not on linux
        FileNotFoundError: if filepath does not exist

    """
    if is_win():
        raise OSError("`dgpy.sh.ldd(_async)` is linux only")
    if not sh.path.exists(str(filepath)):
        raise FileNotFoundError(f"Cannot `ldd`; Filepath does not exist: {filepath!s}")
    proc = sh.do(args=["ldd", filepath])
    return _parse_ldd_stdout(proc.stdout)


async def ldd_async(filepath: FsPath) -> dict[str, str | None]:
    """Parse and return results ldd as a dictionary of so-name => so-path

    Args:
        filepath: Path to executable to LDD

    Returns:
        Dictionary of libs where keys are lib-name and value is lib-fspath

    Raises:
        OSError: If running on windows
        FileNotFoundError: If filepath does not exist

    """
    if is_win():
        raise OSError("`dgpy.sh.ldd(_async)` is linux only")
    if not sh.path.exists(str(filepath)):
        raise FileNotFoundError(f"Cannot `ldd`; Filepath does not exist: {filepath!s}")
    proc = await sh.do_async(args=["ldd", filepath])
    return _parse_ldd_stdout(proc.stdout)


async def source_async(filepath: FsPath, *, _globals: bool = True) -> None:
    """Execute/run a python file given a fspath (ASYNC)

    Args:
        filepath (FsPath): Path to python file
        _globals (bool): Exec using globals

    """
    string = await sh.read_str_async(str(filepath))
    if _globals:
        exec(string, globals())
    else:
        exec(string)
