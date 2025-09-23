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
"""PyViewserver and related objects and functions"""

from __future__ import annotations

import asyncio
import base64
import logging

from collections import deque
from dataclasses import dataclass
from functools import lru_cache
from io import BytesIO
from os import environ
from subprocess import Popen
from time import sleep
from typing import (
    TYPE_CHECKING,
    Any,
    BinaryIO,
    Final,
    Literal,
    TypeAlias,
)
from urllib import parse

import zmq  # "conda install pyzmq" to get this
import zmq.asyncio
import zmq.constants

from aiopen import aiopen
from fmts import b64_html_jpg, b64_html_png
from jsonbourne import JSON
from requires.shed import requires_ipython
from shellfish import write_bytes
from shellfish.process import is_win
from zmq.error import ZMQError
from zmq.sugar.context import Context
from zmq.sugar.socket import Socket

from dgpy.core.config import config
from dgpy.dgipython import display_html
from dgpy.dgpydantic import DgpyBaseModel
from dgpy.ex import DgpyError
from dgpy.pyviewserver._const import VIEWSERVER_COMMANDS, VIEWSERVER_DEFAULT_IMGFORMAT
from dgpy.pyviewserver._types import ViewserverCommand, ViewserverImgFormat
from dgpy.utils.web import get_unused_port

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable, Iterable, Iterator
    from types import TracebackType

_LOCALHOST: Final[str] = "127.0.0.1"


log = logging.getLogger(__name__)
ViewserverKwarg: TypeAlias = str | int | float | bool
ViewserverKwargs = dict[str, ViewserverKwarg]

__all__ = (
    "VIEWSERVER_COMMANDS",
    "Command",
    "CommandLike",
    "PyViewserver",
    "PyViewserverAsync",
    "ViewserverCommand",
    "ViewserverImage",
)


@dataclass
class Command:
    """Command object for Viewserver commands"""

    __slots__ = ("command", "kwargs")
    command: str
    kwargs: ViewserverKwargs

    def __init__(self, command: str, **kwargs: ViewserverKwarg) -> None:
        """Initialize Command object with command string and optional kwargs"""
        self.command = command
        self.kwargs = kwargs or {}
        self.__post_init__()

    def __post_init__(self) -> None:
        """Validate command"""
        if "command" in self.kwargs:
            raise ValueError("Command cannot contain a 'command' key in dict form")

    @property
    def cmd(self) -> str:
        """Alias to return the command string"""
        return self.command

    @cmd.setter
    def cmd(self, command: str) -> None:
        """Alias to set the command string"""
        self.command = command

    def asdict(self) -> dict[str, str | int | float | bool]:
        """Return the command as a dictionary"""
        return {"command": self.command, **self.kwargs}

    def stringify(self, *, fmt: bool = False) -> str:
        """Return the command as a JSON string"""
        return JSON.dumps(self.asdict(), fmt=fmt)

    @property
    def is_exit(self) -> bool:
        """Return True if the command is an exit command"""
        return self.command == "exit"

    @classmethod
    def new(
        cls,
        command: str | Command | ViewserverKwargs,
        **kwargs: ViewserverKwarg,
    ) -> Command:
        if isinstance(command, str):
            return cls(command, **kwargs)
        if isinstance(command, Command):
            if kwargs:
                command.kwargs.update(kwargs)
            return command
        if isinstance(command, dict) and "command" not in command:
            raise ValueError("Command must contain a 'command' key in dict form")
        cmd_string = command.pop("command")
        return cls(str(cmd_string), **command, **kwargs)


CommandLike: TypeAlias = str | Command | ViewserverKwargs | tuple[str, ViewserverKwargs]


def cmd2obj(
    command: CommandLike,
    **kwargs: ViewserverKwarg,
) -> Command:
    """Parse, validate and return command object"""
    if isinstance(command, tuple):
        command, _kwargs = command
        kwargs.update(_kwargs)
    return Command.new(command, **kwargs)


def window_request(height: int = 400, width: int = 600) -> dict[str, str | int]:
    """Return a window/request as a dictionary"""
    return {"command": "window/request", "width": width, "height": height}


def viewserver_command(command: str, **kwargs: Any) -> dict[str, str | int]:
    """Return a viewserver command dictionary"""
    return {"command": command, **kwargs}


@lru_cache(maxsize=16)
def format2extension(fmt: str) -> str:
    """Return the extension for the given format"""
    if fmt.strip(".") != fmt:
        return format2extension(fmt.strip("."))
    return f".{fmt.lower()}"


class ViewserverImage(DgpyBaseModel):
    """Image data object for image data created and sent by the viewserver"""

    id: int | str
    width: int
    height: int
    format: str
    frametag: int
    maxframe: int
    image: str
    statedelta: Any | None = None

    def iio_extension(self) -> str:
        """Return the image's extension for imageio; which requires a leading '.'"""
        return format2extension(self.format)

    def html_string(self) -> str:
        """Return the image as an HTML 'img' tag"""
        _funk = b64_html_png if "png" in self.format.lower() else b64_html_jpg
        return _funk(self.image)

    def _repr_html_(self) -> str:
        """HTML representation of the image data"""
        return self.html_string()

    @property
    def base64_str(self) -> str:
        """Return the image as a base64 string"""
        return self.image

    @property
    def base64_bin(self) -> bytes:
        """Return the base64 string as a bytes"""
        return self.base64_str.encode()

    def to_bytes(self) -> bytes:
        """Return the image as bytes"""
        return base64.decodebytes(self.base64_bin)

    def to_bytesio(self) -> BytesIO:
        """Return the image as a BytesIO buffer containing the image bytes"""
        return BytesIO(self.to_bytes())

    def write2buffer(self, buffer: BinaryIO) -> None:
        """Write the image as bytes to a buffer/file-io object"""
        buffer.write(self.to_bytes())

    def _check_extension(self, filepath: str, *, strict: bool = False) -> str:
        if not filepath.lower().endswith((".png", ".jpg")):
            filepath = f"{filepath}.{self.format.lower()}"
        if strict:
            if filepath.endswith(".jpg") and self.format.lower() == "png":
                raise ValueError("Format is PNG, gave fspath with jpg extension")

            if filepath.endswith(".png") and self.format.lower() != "png":
                raise ValueError("Format is jpg, gave fspath with png extension")
        return filepath

    def to_filepath(self, filepath: str) -> None:
        """Write the image to a fspath"""
        _filepath = self._check_extension(filepath)
        write_bytes(_filepath, self.to_bytes())

    async def to_filepath_async(self, filepath: str) -> None:
        """Write (async) the image to a fspath"""
        _filepath = self._check_extension(filepath)
        async with aiopen(_filepath, "wb") as f:
            await f.write(self.to_bytes())

    def save(self, to_filepath: str) -> None:
        """Save the image to a fspath"""
        self.to_filepath(to_filepath)

    async def save_async(self, to_filepath_async: str) -> None:
        """Save (async) the image to a fspath"""
        await self.to_filepath_async(to_filepath_async)

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

    @classmethod
    def from_json(cls, json_string: bytes | str) -> ViewserverImage:
        """Return an ViewserverImage object given a JSON string"""
        return cls(**JSON.loads(json_string))

    @requires_ipython
    def display(self) -> None:
        """Display in jupyter"""
        display_html(self.html_string())

    @requires_ipython
    def show(self) -> None:
        """Display in jupyter"""
        return self.display()


class ViewserverConnection(DgpyBaseModel):
    """Container for context, dealer and router for a viewserver connection"""

    context: Context
    dealer: Socket
    subscriber: Socket

    def send_string(self, string: str) -> None:
        """Send a string to the dealer"""
        self.dealer.send_string("ASYNCH", zmq.constants.SNDMORE)
        self.dealer.send_string(string)

    def send_json(self, data: Any) -> None:
        """Send a dictionary to the dealer as json"""
        self.send_string(JSON.dumps(data))

    def recv_string(self) -> str:
        """Receive a string from the dealer"""
        mode = self.dealer.recv_string()  # recv mode value
        # Reply from server is in JSON format.  Decode.
        response_string = self.dealer.recv_string().strip().strip("\n")
        log.debug("RESPONSE ~ mode: %s, response: %s", mode, response_string)
        return response_string

    def recv_json(self) -> Any:
        """Receive, parse and return JSON from from the dealer"""
        return JSON.loads(self.recv_string())

    def poll_subscriber_gen(self) -> Iterator[Any]:
        """Check for an image. Returns base64-encoded image if found."""
        # If there's an output file, check subscriber socket for an update.
        poll_res = self.subscriber.poll(timeout=0)
        if poll_res:
            # Read all updates and just process last one.
            while self.subscriber.poll(timeout=2):
                _img_data = self.subscriber.recv_json()
                yield _img_data

    def close(self) -> None:
        self.dealer.close()
        self.subscriber.close()
        self.context.term()


class ViewserverConnectionAsync(DgpyBaseModel):
    """Container for context, dealer and router for a viewserver connection"""

    context: zmq.asyncio.Context
    dealer: zmq.asyncio.Socket
    subscriber: zmq.asyncio.Socket

    async def send_string(self, string: str) -> None:
        """Send (async) a string to the dealer"""
        log.debug("Sending to viewserver: %s", string)
        await self.dealer.send_string("ASYNCH", zmq.constants.SNDMORE)
        await self.dealer.send_string(string)

    async def send_json(self, data: Any) -> None:
        """Send (async) a dictionary to the dealer as json"""
        await self.send_string(JSON.dumps(data))

    async def recv_string(self) -> str:
        """Receive (async), parse and return JSON from from the dealer"""
        mode = await self.dealer.recv_string()  # recv mode value
        log.debug("Response mode: %s", mode)
        # Reply from server is in JSON format.  Decode.
        result = await self.dealer.recv_string()
        return result.strip().strip("\n")

    async def recv_json(self) -> Any:
        """Receive (async), parse and return JSON from from the dealer"""
        return JSON.loads(await self.recv_string())

    async def poll_subscriber_images(self) -> list[Any]:
        """Return an image from the viewserver as a base64 string"""
        # If there's an output file, check subscriber socket for an update.
        images: list[Any] = []
        poll_while = await self.subscriber.poll(timeout=100)
        while poll_while:
            data_multipart = await self.subscriber.recv_multipart()
            images.extend(JSON.loads(el) for el in data_multipart)
            poll_while = await self.subscriber.poll(timeout=100)
        return images

    def close(self) -> None:
        self.dealer.close()
        self.subscriber.close()
        self.context.term()


def start_viewserver_proc(
    port: int,
    *,
    npr: bool = False,
    nobase64: bool = False,
    imgformat: ViewserverImgFormat = VIEWSERVER_DEFAULT_IMGFORMAT,
    si: bool = False,
    stdout: BinaryIO | None = None,
    stderr: BinaryIO | None = None,
    env: dict[str, str] | None = None,
    shell: bool = False,
) -> Popen:
    """Start and return a cv_viewserver subprocess a Popen object"""
    if imgformat not in {"jpgpng", "jpgjpg", "pngpng", "pngjpg"}:
        raise ValueError(
            "Invalid image format: {} -- Must be one of: {}".format(
                imgformat, str({"jpgpng", "jpgjpg", "pngpng", "pngjpg"})
            )
        )
    _env = env or {**dict(environ.items()), **config().environment}
    vs_args = list(
        filter(
            None,
            [
                "cv_viewserver",
                "-server",
                str(port),
                "-imgformat",
                imgformat,
                "-npr" if npr else None,
                "-nobase64" if nobase64 else None,
                "-si" if si else None,
            ],
        )
    )
    log.debug("cv_viewserver args: %r", vs_args)
    try:
        return Popen(vs_args)
    except FileNotFoundError:
        raise DgpyError(
            f"cv_viewserver not found; current path: {_env['PATH']}"
        ) from None


def _connect_to_viewserver(hostname: str, port: int | str) -> ViewserverConnection:
    """Connect to viewserver process

    Connect to viewserver which is expected to be running.  ZeroMQ will wait
    until connection is established so this function will not fail if the
    server is not found.
    """
    # Break connect string into host and port number portions
    # Open ZeroMQ context
    context = Context()

    # Open communication socket to talk to viewserver
    log.debug("Connecting to viewserver on %s:%s", hostname, port)
    try:
        dealer: Socket = context.socket(zmq.constants.DEALER)
        dealer.connect(f"tcp://{hostname!s}:{port!s}")
        log.debug("Connected!")
    except ZMQError as e:
        log.exception("Unable to connect to viewserver")
        raise e
    log.debug("Subscribing...")
    # Serialize and send2viewserver command to viewserver
    dealer.send_string("SUBSCRIBE", zmq.constants.SNDMORE)
    dealer.send_string("")
    # Expect port number reply.
    mode = dealer.recv_string()
    if mode != "SUBSCRIBE":
        log.error("Error retrieving publisher port from server.")
        raise DgpyError("Unable to connect to viewserver")

    log.debug("Reading port from socket...")
    publish_port = dealer.recv_string()

    log.debug("Publisher port: %s", publish_port)
    # Subscribe to server's publications
    try:
        subscriber: Socket = context.socket(zmq.constants.SUB)
        subscriber.connect(publish_port)
        subscriber.setsockopt(zmq.constants.SUBSCRIBE, b"")
        log.debug("Subscribed to viewserver updates")
    except ZMQError as e:
        log.exception("Unable to connect to viewserver")
        raise e
    return ViewserverConnection(context=context, dealer=dealer, subscriber=subscriber)


async def _connect_to_viewserver_async(
    hostname: str, port: int | str
) -> ViewserverConnectionAsync:
    """Connect (async) to a viewserver process

    Connect to viewserver which is expected to be running.  ZeroMQ will wait
    until connection is established so this function will not fail if the
    server is not found.
    """
    # Break connect string into host and port number portions
    # Open ZeroMQ context
    context: zmq.asyncio.Context = zmq.asyncio.Context.instance()

    # Open communication socket to talk to viewserver
    log.debug("Connecting to viewserver on %s:%s", hostname, port)
    try:
        dealer: zmq.asyncio.Socket = context.socket(zmq.constants.DEALER)
        dealer.connect(f"tcp://{hostname!s}:{port!s}")
        log.info("Connected to viewserver!")
    except ZMQError as e:
        log.exception("Unable to connect to viewserver")
        raise e
    # Serialize and send2viewserver command to viewserver
    await dealer.send_string("SUBSCRIBE", zmq.constants.SNDMORE)
    await dealer.send_string("")
    # Expect port number reply.
    mode = await dealer.recv_string()
    if mode != "SUBSCRIBE":
        log.error("Error retrieving publisher port from server.")
        raise DgpyError("Not able to to connect to viewserver")

    log.debug("Reading port from socket...")
    publish_port = await dealer.recv_string()

    log.debug("Publisher port is %s", publish_port)
    # Subscribe to server's publications
    try:
        subscriber: zmq.asyncio.Socket = context.socket(zmq.constants.SUB)
        subscriber.connect(publish_port)
        subscriber.setsockopt(zmq.constants.SUBSCRIBE, b"")
        log.info("Subscribed to viewserver updates")
    except ZMQError as e:
        log.exception("Unable to connect to viewserver")
        raise e
    return ViewserverConnectionAsync(
        context=context, dealer=dealer, subscriber=subscriber
    )


class PyViewserverBase:
    """Viewserver wrapper class for dgpy"""

    hostname: str
    port: int
    connection_string: str
    connection: ViewserverConnection | ViewserverConnectionAsync
    server: Popen | None = None
    connected: bool = False
    _async: bool = False
    _image_data: deque[ViewserverImage]

    def __init__(
        self,
        connection_string: str | None = None,
        *,
        npr: bool = False,
        loglevel: Any = None,
        keep: int = 1,
        auto_connect: bool = False,
    ) -> None:
        """Construct a PyViewserver object

        Args:
            connection_string (str): Connection string containing the host and
                port as a string
            npr (bool): Add '-npr' to the viewserver process command
            loglevel: Log level for the viewserver
            keep (int): Number of image to keep from the viewserver; defaults
                to keeping only 1 image.
            auto_connect (bool): Automatically connect to the viewserver
                process on the creation of the PyViewserver object; defaults
                to False for the sake of having both async and sync method in
                the one PyViewserver class

        Returns:
            None

        """
        if connection_string:
            self.hostname = _LOCALHOST
            self.port = int(get_unused_port())
            self.connection_string = f"{self.hostname!s}:{self.port!s}"
        else:
            _parsed_url = parse.urlparse(connection_string)
            self.hostname = _parsed_url.hostname or _LOCALHOST  # type: ignore
            self.port = _parsed_url.port or int(get_unused_port())
            self.connection_string = f"{self.hostname!s}:{self.port!s}"

        self._image_data: deque[ViewserverImage] = deque(maxlen=keep)
        # If not port is specified, randomly generate one as a string.
        if loglevel:
            log.setLevel(loglevel)
        log.info("cv_viewserver port: %s", connection_string)

        self.server = start_viewserver_proc(port=self.port, npr=npr)
        # Connect to viewserver and get the context, dealer and subscriber
        if auto_connect:
            self.auto_connect()
        self.__post_init__()

    def __post_init__(self) -> None:
        """Post init func"""

    def auto_connect(self) -> None:
        """Auto connect to cv_viewserver"""
        raise NotImplementedError

    @property
    def image_data(self) -> list[ViewserverImage]:
        """Return the collected image data"""
        return list(self._image_data)

    @property
    def last_image(self) -> ViewserverImage:
        """Return the last/most-recent ViewserverImage object from the viewserver"""
        return self._image_data[-1]

    def save_last_image(self, filepath: str) -> None:
        """Save the last image (if it exists) to the given fspath

        Args:
            filepath (str): fspath to save image to

        Returns:
            None

        """
        self.last_image.save(filepath)

    @requires_ipython
    def show(self) -> None:
        """Show the latest image from the PyViewserver"""
        display_html(self.last_image.html_string())


class PyViewserver(PyViewserverBase):
    """Viewserver wrapper class for dgpy"""

    hostname: str
    port: int
    connection_string: str
    connection: ViewserverConnection
    server: Popen | None = None
    connected: bool = False
    _async: bool = False
    _image_data: deque[ViewserverImage]

    def connect(self) -> None:
        """Connect to the viewserver process"""
        log.debug("Connecting to viewserver on %s:%s", self.hostname, self.port)
        if not self.connected:
            self.connection = _connect_to_viewserver(self.hostname, self.port)
            self.connected = True

    def auto_connect(self) -> None:
        """Auto connect to the viewserver"""
        if not self.connected:
            self.connect()

    def exit(self) -> None:
        """Send exit command to viewserver"""
        # Check if viewserver is still running
        self._poll_server_proc()
        self.connection.send_json({"command": "exit"})

    def server_ps(self) -> Popen:
        if isinstance(self.server, Popen):
            return self.server
        raise Exception("Viewserver process not running")

    def close(self) -> None:
        self.exit()
        self.connection.close()

        if is_win():
            _server = self.server_ps()
            _server.kill()
            sleep(0.0)
        else:
            _server = self.server_ps()
            _server.terminate()

    def __enter__(self) -> PyViewserver:
        """Enter method for using PyViewserver as a context manager"""
        self.auto_connect()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        exc_traceback: TracebackType | None,
    ) -> Literal[False]:
        """Exit method for using the PyViewserver as a context manager"""
        try:
            if exc_type is not None:
                # exc_info makes logging render the full traceback.
                # You can also attach context via 'extra'.
                log.error(
                    "Closing PyViewserver due to exception",
                    exc_info=(exc_type, exc_value, exc_traceback),  # type: ignore[arg-type]
                    extra={
                        "component": "pyviewserver",
                        "conn_id": getattr(self, "conn_id", None),
                        "last_cmd": getattr(self, "last_cmd", None),
                    },
                )
            else:
                log.debug(
                    "Closing PyViewserver cleanly",
                    extra={
                        "component": "pyviewserver",
                        "conn_id": getattr(self, "conn_id", None),
                    },
                )
        finally:
            try:
                self.close()
            except Exception:
                # close() failures silently
                log.exception(
                    "Error while closing PyViewserver",
                    extra={
                        "component": "pyviewserver",
                        "conn_id": getattr(self, "conn_id", None),
                    },
                )
        return False

    def _poll_server_proc(self) -> None:
        """Check that the viewserver subprocess is still running

        Returns:
            None

        Raises:
            DgpyError: if the viewserver subprocess has exited

        """
        if self.server:
            result = self.server.poll()
        else:
            raise DgpyError("Server is None")
        if result:
            log.error("Viewserver not running; poll response: %s", result)
            raise DgpyError("Viewserver poll failed; viewserver not running")

    def recv_images(self) -> None:
        """Update the viewservers internal deque of image objects"""
        for imgdata in self.connection.poll_subscriber_gen():
            self._image_data.append(ViewserverImage(**imgdata))

    def send_json(self, data: Any) -> None:
        """Send a json object to the viewserver"""
        self.connection.send_json(data)

    def do(self, command: CommandLike, **kwargs: ViewserverKwarg) -> str:
        """Send a command as a dictionary to the viewserver

        Args:
            command (Union[str, Command, ViewserverKwargs]): command to send as string
                or dictionary or Command object
            **kwargs (ViewserverKwarg): keyword arguments to send

        Returns:
            Reply from the cpp viewserver

        """
        log.debug("viewserver.do() - command: %s, kwargs: %s", command, kwargs)

        self._poll_server_proc()  # Check if viewserver process is running
        cmd_obj = cmd2obj(command, **kwargs)
        if cmd_obj.is_exit:
            self.exit()
            return "EXIT"
        self.connection.send_json(cmd_obj.asdict())
        # The exit command does not reply. Exit after sending.
        # Otherwise, make a reply buffer and await reply.
        self.recv_images()
        response_string = self.connection.recv_string()
        log.debug("viewserver.do() - response: %s", response_string)
        return response_string

    def cmd(self, command: CommandLike, **kwargs: ViewserverKwarg) -> str:
        return self.do(command, **kwargs)

    def do_many(self, commands: Iterable[CommandLike]) -> Iterable[str]:
        """Do many commands and yield the results"""
        return (self.do(command) for command in commands)

    def do_many_list(self, commands: Iterable[CommandLike]) -> list[str]:
        """Do many commands and return the results as a list"""
        return list(self.do_many(commands))

    def file_open(self, filepath: str, **kwargs: ViewserverKwarg) -> Any:
        """Send a 'file/open' command to the viewserver"""
        return self.cmd(command="file/open", file=filepath, **kwargs)

    def window_request(
        self, height: int = 400, width: int = 640, **kwargs: ViewserverKwarg
    ) -> Any:
        """Send a window request command to the viewserver"""
        return self.do({
            "command": "window/request",
            "width": width,
            "height": height,
            **kwargs,
        })

    @property
    def image_data(self) -> list[ViewserverImage]:
        """Return the collected image data"""
        if not self._async:
            self.recv_images()
        return list(self._image_data)

    @property
    def last_image(self) -> ViewserverImage:
        """Return the last/most-recent ViewserverImage object from the viewserver"""
        if not self._async:
            self.recv_images()
        return self._image_data[-1]

    def save_last_image(self, filepath: str) -> None:
        """Save the last image (if it exists) to the given fspath

        Args:
            filepath (str): fspath to save image to

        Returns:
            None

        """
        self.last_image.save(filepath)

    def help(self, command: str | None = None) -> Any:
        """Get the help for a command from the viewserver"""
        return self.do(command or "help")

    def _repr_html_(self) -> str:
        if self.last_image:
            return self.last_image.html_string()
        return "<h2>No image to show</h2>"


class PyViewserverAsync(PyViewserverBase):
    """Viewserver wrapper class for dgpy"""

    hostname: str
    port: int
    connection_string: str
    connection: ViewserverConnectionAsync
    server: Popen | None = None
    connected: bool = False
    _image_data: deque[ViewserverImage]

    async def connect(self) -> None:
        """Connect (async) to the viewserver process"""
        if not self.connected:
            self.connection = await _connect_to_viewserver_async(
                self.hostname, self.port
            )
            self._async = self.connected = True

    def auto_connect(self) -> None:
        raise NotImplementedError("Cannot use auto_connect with PyViewserverAsync")

    async def auto_connect_async(self) -> None:
        """Auto connect (async) to the viewserver"""
        if not self.connected:
            await self.connect()

    def server_ps(self) -> Popen:
        if isinstance(self.server, Popen):
            return self.server
        raise Exception("Viewserver process not running")

    async def exit(self) -> None:
        """Send exit command to viewserver"""
        # Check if viewserver is still running
        self._poll_server_proc()
        await self.connection.send_json({"command": "exit"})

    async def close(self) -> None:
        await self.exit()
        self.connection.close()

    async def __aenter__(self) -> PyViewserverAsync:
        """Async enter for using PyViewserver via async context manager"""
        await self.auto_connect_async()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        exc_traceback: TracebackType | None,
    ) -> bool:
        """Async exit method for async context manager.

        Returns False so the original exception (if any) propagates.
        Always attempts to close; shields close() from cancellation so resources
        are cleaned up even on CancelledError.
        """
        try:
            if exc_type is not None:
                # tb + structured context
                log.error(
                    "Closing PyViewserverAsync due to exception",
                    exc_info=(exc_type, exc_value, exc_traceback),  # type: ignore[arg-type]
                    extra={
                        "component": "pyviewserver",
                        "conn_id": getattr(self, "conn_id", None),
                        "last_cmd": getattr(self, "last_cmd", None),
                    },
                )
            else:
                log.debug(
                    "Closing PyViewserverAsync cleanly",
                    extra={
                        "component": "pyviewserver",
                        "conn_id": getattr(self, "conn_id", None),
                    },
                )
        finally:
            # Ensure close() runs even if the task is being cancelled.
            try:
                await asyncio.shield(self.close())
            except Exception:
                # Do not mask the original exception; just log close() failure.
                log.exception(
                    "Error while closing PyViewserverAsync",
                    extra={
                        "component": "pyviewserver",
                        "conn_id": getattr(self, "conn_id", None),
                    },
                )

        # IMPORTANT: return False to propagate any exception that triggered __aexit__
        return False

    def _poll_server_proc(self) -> None:
        """Check that the viewserver subprocess is still running

        Returns:
            None

        Raises:
            DgpyError: if the viewserver subprocess has exited

        """
        if self.server:
            result = self.server.poll()
        else:
            raise DgpyError("Server is None")
        if result:
            log.error("Viewserver not running; poll response: %s", str(result))
            raise DgpyError("Viewserver poll failed; viewserver not running")

    async def recv_images(self) -> None:
        """Update the viewservers internal deque of image objects"""
        image_data_list = await self.connection.poll_subscriber_images()
        self._image_data.extend(
            ViewserverImage(**imgdata) for imgdata in image_data_list
        )

    async def do(self, command: CommandLike, **kwargs: ViewserverKwarg) -> str:
        # async def do(self, data: Any) -> str:
        """Send a command as a dictionary to the viewserver

        Args:
            command (Union[str, Command, ViewserverKwargs]): command to send as string
                or dictionary or Command object
            **kwargs (ViewserverKwarg): keyword arguments to send

        Returns:
            Reply from the cpp viewserver

        """
        log.debug("command: %s, kwargs: %s", command, kwargs)

        self._poll_server_proc()  # Check if viewserver process is running

        cmd_obj = cmd2obj(command, **kwargs)
        if cmd_obj.is_exit:
            await self.exit()
            return "EXIT"
        await self.connection.send_json(cmd_obj.asdict())
        # The exit command does not reply. Exit after sending.
        # Otherwise, make a reply buffer and await reply.
        await self.recv_images()
        response_string = await self.connection.recv_string()
        return response_string

    async def cmd(
        self, command: str | Command | ViewserverKwargs, **kwargs: ViewserverKwarg
    ) -> str:
        """Alias for do()"""
        return await self.do(command, **kwargs)

    async def do_many(
        self, commands: Iterable[CommandLike]
    ) -> AsyncGenerator[str, None]:
        """Do many commands and yield the results"""
        for command in commands:
            yield await self.do(command)

    async def do_many_list(self, commands: Iterable[CommandLike]) -> list[str]:
        """Do many commands and yield the results"""
        return [await self.do(command) for command in commands]

    async def file_open(self, filepath: str, **kwargs: ViewserverKwarg) -> Any:
        """Send (async) a 'file/open' command to the viewserver"""
        return await self.do({"command": "file/open", "file": filepath, **kwargs})

    async def window_request(
        self, height: int = 400, width: int = 640, **kwargs: ViewserverKwarg
    ) -> Any:
        """Send (async) a window request command to the viewserver"""
        return await self.do({
            "command": "window/request",
            "width": width,
            "height": height,
            **kwargs,
        })

    async def help(self, command: str | None = None) -> Any:
        """Get (async) the help for a command from the viewserver"""
        return await self.do(command or "help")

    def _repr_html_(self) -> str:
        if self.last_image:
            return self.last_image.html_string()
        return "<h2>No image to show</h2>"

    @requires_ipython
    def show(self) -> None:
        """Show the latest image from the PyViewserver"""
        display_html(self.last_image.html_string())
