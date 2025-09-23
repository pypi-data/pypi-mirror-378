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
"""Py2grd and Py3grd IO"""

from __future__ import annotations

import base64
import logging

from abc import ABC, abstractmethod
from functools import reduce
from io import BytesIO
from operator import mul
from os import path
from pprint import pformat
from struct import calcsize, error as _struct_err, pack, unpack
from typing import TYPE_CHECKING, Any, BinaryIO

import numpy as np

from jsonbourne import JSON
from shellfish import fs

from dgpy.core.config import __config__
from dgpy.core.enums import Evu
from dgpy.core.enums.evu import evu_validate
from dgpy.core.py6grd.evg import (
    Evg,
    EvgToken,
    InvalidEvgTokenError,
    UnknownEvgTokenError,
    evg_str2int,
)
from dgpy.core.py6grd.magic import MAGIC_NUM_DATA, MagicNumber
from dgpy.core.py6grd.py6grd_dto import PygrdHeaderDTO
from dgpy.core.pyspace import PySpace
from dgpy.dgpydantic import DgpyBaseModel
from dgpy.maths import (
    pack_8_bit_arr,
    pack_16_bit_arr,
    unpack_8_bit_arr,
    unpack_16_bit_arr,
)
from dgpy.xtypes import Arr

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    from dgpy import npt
    from dgpy._types import FsPath
    from dgpy.core.py6grd.py6grd_base import Py6grdBase

log = logging.getLogger(__name__)


def _grd_type(filepath: str) -> str:
    if filepath.endswith(".2grd"):
        return "2D grid"
    if filepath.endswith(".3grd"):
        return "3D grid"
    if filepath.endswith(".m3grd"):
        return "Multi-Grid"
    if filepath.endswith(".c3grd"):
        return "Cellgrid"
    raise ValueError("unknown grid type")


def unpack_fmt_tuple(token: int, length: int, byte_order: str) -> tuple[str, int, str]:
    """Get the format string used to unpack bytes with struct.unpack

    Args:
        byte_order: byte order string
        length (int): length of the bytes
        token: Token number to unpack

    Returns:
        string to be used by struct.unpack

    """
    evg = EvgToken.from_int(token)
    fmtstring = evg.fmtstr
    if len(fmtstring) > 1:
        return byte_order, 1, evg.fmtstr
    num = length // calcsize(fmtstring)
    return byte_order, num, evg.fmtstr


def unpack_fmt_string(token: int, length: int, byte_order: str) -> str:
    """Get the format string used to unpack bytes with struct.unpack

    Args:
        byte_order: byte order string
        length (int): length of the bytes
        token: Token number to unpack

    Returns:
        string to be used by struct.unpack

    """
    evg = EvgToken.from_int(token)

    fmtstring = evg.fmtstr
    if len(fmtstring) > 1:
        return f"{byte_order}{evg.fmtstr}"
    num = length // calcsize(fmtstring)
    return f"{byte_order}{num}{evg.fmtstr}"


def bigval2nan(arr: npt.ArrayLike) -> npt.NDArray:
    """Convert all huge-values in a numpy array to np.nan

    Args:
        arr: Array to operate on

    Returns:
        input array with big values converted

    """
    _big_val = 1.0000000200408773e20
    _arr: npt.NDArray = np.array(arr)
    _arr[_arr == _big_val] = np.nan
    return _arr


def get_grd_values(
    grd_data: PygrdHeaderDTO, array_shape: tuple[int, int] | tuple[int, int, int]
) -> npt.NDArray:
    """Get the grid values as a numpy array in the correct shape

    Args:
        grd_data: grid data dictionary
        array_shape: shape of the values array

    Returns:
        numpy array of grid values

    """
    try:
        if grd_data.values_32 is not None:
            arr = bigval2nan(grd_data.values_32)
            arr = arr.reshape(array_shape)
            return arr
        raise KeyError("no values found")
    except KeyError:
        pass
    except TypeError:
        pass
    try:
        node_range_min, node_range_max = grd_data.node_range
        if node_range_min == node_range_max:
            return np.full(array_shape, node_range_min)
    except KeyError:
        pass
    n_nodes = reduce(mul, array_shape, 1)
    if n_nodes == grd_data.nulls_in_grid:
        return np.full(array_shape, np.nan)

    raise ValueError("Could not load grid values for data: " + JSON.dumps(grd_data))


class PygrdTokenBin(DgpyBaseModel):
    """Pygrid token bin-container"""

    token: int
    token_name: str
    bin_data: bytes
    length: int
    byte_order: str
    evg: EvgToken

    def to_dict(self) -> dict[str, Any]:
        """Return object as dictionary"""
        return {
            "token": self.token,
            "token_name": self.token_name,
            "bin_data": base64.b64encode(self.bin_data).decode(),
            "length": self.length,
            "byte_order": self.byte_order,
            "evg": self.evg.to_dict(),
        }

    @classmethod
    def from_json(cls, json_string: bytes | str) -> PygrdTokenBin:
        """Create object from JSON string"""
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
        """Convert object to JSON string"""
        return JSON.dumps(
            self.to_dict(),
            fmt=fmt,
            pretty=pretty,
            sort_keys=sort_keys,
            append_newline=append_newline,
            default=default,
            **kwargs,
        )

    def decode_pyspace_raw(self) -> PySpace:
        """Decode Pyspace object if token is pyspace"""
        if self.token != Evg.space:
            raise ValueError(
                f"Cannot decode Pyspace; token is not space ({self.token_name})"
            )
        return PySpace.from_bytes(self.bin_data)

    def decode_geo_space(self) -> tuple[str, PySpace]:
        return "space", self.decode_pyspace_raw()

    def attr_name(self) -> str:
        return self.evg.dgpy_attr

    def decode_values(self) -> tuple[str, npt.NDArray | None]:
        """Return values and values attr type"""
        # end of header
        # decode geospace
        attrname = self.attr_name()
        if len(self.bin_data) == 0:  # if all nodes are one value no values are written
            return attrname, None
        assert self.bin_data != b"\n"
        binorder, count, token_str = unpack_fmt_tuple(
            self.token, self.length, self.byte_order
        )
        try:
            unpacked: npt.NDArray = np.frombuffer(
                self.bin_data, count=count, dtype=f"{binorder}{token_str}"
            ).astype(dtype=np.float64)
            return attrname, unpacked
        except ValueError as ve:
            raise ve

    def decode_token(self, byte_order: str | None = None) -> tuple[str, Any]:
        """Decode a 2/3grd token

        Args:
            byte_order: order of the packed bytes

        Returns:
            Dictionary containing one key value pair, grid-attribute-name -> data

        Old version usage:

        ``` python
        if buffer:  # If buffer is 0 or '', then grab next token
            if token_name == "Evg_space":
                _token_l[token_name] = PygrdTokenBin(
                    token=token, token_name=token_name, bin_data=buffer, length=length
                    )
                grid_space = PySpace.from_bytes(buffer)
                grd_data["space"] = grid_space
                grd_data.update(grid_space.dump_dict())
            else:
                decoded_data = decode_token(
                    token, token_name, length, buffer, byte_order
                    )
                grd_data.update(decoded_data)
        ```

        """
        _byte_order = byte_order or self.byte_order
        # end of header
        # decode geospace
        if self.token_name == "Evg_space":
            return self.decode_geo_space()
        attrname = self.attr_name()
        if self.token_name == "Evg_endOfHeader":
            return self.attr_name(), None
            ##################################
        # handle values
        if attrname in {
            "values",
            "16bit_values",
            "8bit_values",
            "values_32",
            "values_16",
            "values_8",
        }:
            return self.decode_values()
        if attrname == "padding":
            return attrname, len(self.bin_data)
        if len(self.bin_data) == 0:
            return attrname, None
        unpacked = unpack(
            unpack_fmt_string(self.token, self.length, _byte_order), self.bin_data
        )
        if len(unpacked) == 1:
            unpacked = unpacked[0]
        if attrname == "values":
            _unpacked: npt.NDArray = np.array(unpacked)
            return attrname, _unpacked
        elif self.evg.fmtstr == "s" and isinstance(unpacked, bytes):
            try:
                unpacked = unpacked.decode()
            except UnicodeDecodeError:
                pass
        return attrname, unpacked

    def decoded_dict(self) -> dict[str, Any]:
        if self.token == Evg.endOfHeader:
            return {}
        attrname, unpacked = self.decode_token()
        return {attrname: unpacked}


class PygrdReader:
    """Py2grd/Py3grd reader"""

    binio: BinaryIO
    fspath: str = "buffer"
    magic: MagicNumber | None = None
    _evg_err: bool = False

    def __init__(self, binio: BinaryIO, fspath: str = ""):
        """Initialize PygrdReader with binary-io object"""
        self.binio = binio
        self.fspath = str(fspath)
        self._evg_err = __config__.TESHTING

    @staticmethod
    def read_magic_number(binio: BinaryIO) -> MagicNumber:
        """Return MagicNumber data object for binary-io object"""
        bites = binio.read(4)
        magic_num = unpack("I", bites)[0]
        return MAGIC_NUM_DATA[magic_num]

    @property
    def binio_tell(self) -> int:
        """Return current binio position"""
        return self.binio.tell()

    def data_gen(self, *, skip_nodes: bool = False) -> Iterable[PygrdTokenBin]:
        self.magic = self.read_magic_number(self.binio)

        byte_order: str = self.magic.byte_order
        len_length_flag: str = self.magic.bin_length_flag

        # Format string for struct.unpack to unpack a evg_token and data length
        token_and_length_unpack_str: str = f"{byte_order}i{len_length_flag}"
        # Size of bytes to read to do the unpacking of the token and data length
        token_and_length_bin_size = 4 + self.magic.bin_length

        # Read Magic Number
        bin_chunk = self.binio.read(token_and_length_bin_size)
        while bin_chunk:
            # Get the evg token
            try:
                token_num, length = unpack(token_and_length_unpack_str, bin_chunk)
                evg_token = EvgToken.from_int(token_num)
                if skip_nodes and not evg_token.is_header_token():
                    self.binio.seek(length, 1)
                else:
                    bin_chunk = self.binio.read(length)
                    grid_data_chunk = PygrdTokenBin(
                        token=token_num,
                        token_name=evg_token.token_name,
                        bin_data=bin_chunk,
                        length=length,
                        byte_order=byte_order,
                        evg=evg_token,
                    )
                    yield grid_data_chunk
            except InvalidEvgTokenError as e:
                log.exception("invalid-evg-token")
                raise e
            except UnknownEvgTokenError as e:
                log.warning("unknown-evg-token", exc_info=e)
                if self._evg_err:
                    raise e
            except Exception as e:
                if bin_chunk != b"\n":
                    log.warning(
                        "Error decoding token; binary-chunk: %r - exception: %s",
                        bin_chunk,
                        e,
                    )
                    if self._evg_err:
                        raise e
            #################################################################
            # End of While Loop: Get next token and length of bytes to read #
            #################################################################
            bin_chunk = self.binio.read(token_and_length_bin_size)


def load_grd_data(
    bites: BinaryIO | BytesIO,
    filepath: str = "buffer",
    *,
    skip_nodes: bool = False,
) -> PygrdHeaderDTO:
    """Load the data for a 2/3 grid into a dictionary

    Args:
        skip_nodes (bool): Read grid nodes if True; False otherwise (default = True)
        bites (Union[BinaryIO, BytesIO]): BytesIO-like object of grid data
        filepath (str): path to a 2 or 3 grid

    Returns:
        dictionary with the data for a 2/3 grid

    """
    if isinstance(bites, bytes):
        bites = BytesIO(bites)

    pygrd_reader = PygrdReader(binio=bites, fspath=filepath)

    dto = PygrdHeaderDTO()

    for pg_token_bin in pygrd_reader.data_gen(skip_nodes=skip_nodes):
        try:
            attrname, value = pg_token_bin.decode_token()
            if pg_token_bin.token == Evg.history:
                dto.history.append(value)
            elif pg_token_bin.token in (Evg.xyunits, Evg.zunits, Evg.punits):
                dto.__setattr__(attrname, evu_validate(value))
            elif pg_token_bin.token != 93 and value is not None:
                dto.__setattr__(attrname, value)
        except Exception as e:
            log.warning("grd-decoding warning: %s", e)
            raise e
    return dto


def load_2grd_buffer(
    bites: bytes | BinaryIO | BytesIO,
    *,
    skip_nodes: bool = False,
    filepath: str = "buffer",
) -> PygrdHeaderDTO:
    if isinstance(bites, bytes | bytearray | memoryview):
        bites = BytesIO(bites)
    grd_data = load_grd_data(bites, skip_nodes=skip_nodes)
    grd_data.fspath = "unknown/buffer" if filepath else path.abspath(filepath)
    grd_data.dims = ["yrows", "xcolumns"]

    if not skip_nodes:
        if grd_data.values_8 is not None:
            _values_array: npt.NDArray = np.array(grd_data.values_8, dtype=np.float64)
            values_32 = unpack_8_bit_arr(
                arr=_values_array,
                factor=float(grd_data.bit_factor),
                shift=float(grd_data.bit_shift),
            )
            grd_data.values_32 = Arr(values_32)
        elif grd_data.values_16 is not None:
            _values_array = np.array(grd_data.values_16, dtype=np.float64)
            values_32 = unpack_16_bit_arr(
                arr=_values_array,
                factor=float(grd_data.bit_factor),
                shift=float(grd_data.bit_shift),
            )
            grd_data.values_32 = Arr(values_32)

        array_shape: tuple[int, int] = (
            grd_data.yrow,
            grd_data.xcol,
        )
        if grd_data.is_bordered:
            array_shape = (grd_data.yrow - 2, grd_data.xcol - 2)
        _py2grd_values_32 = get_grd_values(grd_data, array_shape)
        grd_data.values_32 = Arr(_py2grd_values_32)
        grd_data.bit_shift = 0.0
        grd_data.bit_factor = 1.0
        if grd_data.is_bordered or grd_data.geometry == 8:
            grd_data.xcol -= 2
            grd_data.yrow -= 2
            grd_data.values_32 = grd_data.values()[1:-1, 1:-1]  # type: ignore
            grd_data.geometry = 0
    return grd_data


def load_3grd_buffer(
    bites: bytes | BinaryIO | BytesIO,
    *,
    skip_nodes: bool = False,
    filepath: str = "buffer",
) -> PygrdHeaderDTO:
    if isinstance(bites, bytes):
        bites = BytesIO(bites)
    grd_data = load_grd_data(bites, skip_nodes=skip_nodes)
    if filepath:
        grd_data.fspath = path.abspath(filepath)
    else:
        grd_data.fspath = "unknown/buffer"

    grd_data.is_bordered = False

    grd_data.dims = ["zlevels", "yrows", "xcolumns"]
    array_shape: tuple[int, int, int] = (grd_data.zlev, grd_data.yrow, grd_data.xcol)

    if not skip_nodes:
        if grd_data.values_8 is not None:
            _values_array: npt.NDArray = np.array(grd_data.values_8, dtype=np.float64)
            _values_32 = unpack_8_bit_arr(
                arr=_values_array,
                factor=float(grd_data.bit_factor),
                shift=float(grd_data.bit_shift),
            )
            grd_data.values_32 = Arr(_values_32)

        if grd_data.values_16 is not None:
            _values_array = np.array(grd_data.values_16, dtype=np.float64)
            _values_32 = unpack_16_bit_arr(
                arr=_values_array,
                factor=float(grd_data.bit_factor),
                shift=float(grd_data.bit_shift),
            )
            grd_data.values_32 = Arr(_values_32)
        _py3grd_values_32 = get_grd_values(grd_data, array_shape)
        grd_data.values_32 = Arr(_py3grd_values_32)
        grd_data.bit_shift = 0.0
        grd_data.bit_factor = 1.0
    return grd_data


def load_2grd(filepath: str, *, skip_nodes: bool = False) -> PygrdHeaderDTO:
    if str(filepath).startswith("s3://"):
        bio = BytesIO()
        grid_bytes = fs.lbytes(filepath)
        bio.write(grid_bytes)
        bio.seek(0)
        return load_2grd_buffer(bio, filepath=filepath, skip_nodes=skip_nodes)
    with open(filepath, "rb") as gf:
        _read_data = load_2grd_buffer(gf, skip_nodes=skip_nodes, filepath=filepath)
    return _read_data


def load_3grd(filepath: str, *, skip_nodes: bool = False) -> PygrdHeaderDTO:
    if str(filepath).startswith("s3://"):
        bio = BytesIO()
        grid_bytes = fs.lbytes(filepath)
        bio.write(grid_bytes)
        bio.seek(0)
        return load_3grd_buffer(bio, filepath=filepath, skip_nodes=skip_nodes)
    with open(filepath, "rb") as gf:
        _read_data = load_3grd_buffer(gf, skip_nodes=skip_nodes, filepath=filepath)
    return _read_data


def load_grd(filepath: FsPath, *, skip_nodes: bool = False) -> PygrdHeaderDTO:
    """Load the data for a 2/3 grid into a dictionary

    Args:
        filepath (str): path to a 2 or 3 grid
        skip_nodes (bool): Read the grid node values if True, otherwise do not

    Returns:
        dictionary with the data for a 2/3 grid

    Previously implemented with:

    ```python
    load_grd_buffer: Callable[[Union[bytes, BinaryIO], bool, str], PygrdHeaderDTO] = (
        load_2grd_buffer
        if str(filepath).lower().endswith('.2grd')
        else load_3grd_buffer
    )

    if str(filepath).startswith("s3://"):
        bio = BytesIO()
        grid_bytes = fs.lbytes(filepath)
        bio.write(grid_bytes)
        bio.seek(0)
        return load_grd_buffer(bio, skip_nodes, filepath)
    with open(filepath, "rb") as gf:
        _read_data = load_grd_buffer(gf, skip_nodes, filepath)
    return _read_data
    ```
    """
    if str(filepath).lower().endswith(".2grd"):
        return load_2grd(filepath=str(filepath), skip_nodes=skip_nodes)
    return load_3grd(filepath=str(filepath), skip_nodes=skip_nodes)


class PygrdWriterBase(ABC):
    """PyGrd reading/writing class

    Notes:
    ```
    - check nulls in grid
    ~ magic num
    ~ version
    ~ alias
    ~ desc
    ~ space and len space
    ~ csid (coordinate system id)
    ~ cs name (coordinate system name)
    ~ xcol
    ~ yrow
    ~ zlev
    ~ dat
    ~ field
    ~ if 2grd
        ~ vflt
        ~ nvflt
    ~ trend if exists
    - if 3grd
        ~ punits
        - if clip
            ~ clippoly
            ~ cliptop
            ~ clipTopExpansion
            - clipbotexpansion
            - pclip
        - clamp
        - if xform
            - xformtype
            - xform spacing
            - xformtop
            - if xformtop
                - topshift if not empty
                - xform bot if not empty
            - if not xformbotempty:
                - xform bot
                - botshift
                - topperent botpercent
            - if xform size, xform size
            - xfomrzspacing
            - xform bottom
        - zinfluence
    - bpoly
    - nulls in grid
    - geometry
    - noderange
    - date
    - lineorientation/seismicline and trace
    - each line of history
    - reserved
    - end of header (EOH)
    ```
    """

    pygrd: Py6grdBase

    def __str__(self) -> str:
        return pformat(self.__dict__, compact=True)

    @abstractmethod
    def magic_token_bytes(self) -> bytes: ...

    def pack_array(self, evg_token_name: str) -> bytes:
        token = evg_str2int(evg_token_name)
        tmp_token = pack("=I", token)
        _attr_data = self.pygrd.nparr
        _token_info = Evg.evg_token(token)
        if evg_token_name == "Evg_8bitValues":
            _values = self.__dict__["values"]
            _factor = self.__dict__["bit_factor"]
            _shift = self.__dict__["bit_shift"]
            _attr_data = pack_8_bit_arr(_values, _factor, _shift)
            evg_token_name = "Evg_values"
        elif evg_token_name == "Evg_16bitValues":
            _values = self.__dict__["values"]
            _factor = self.__dict__["bit_factor"]
            _shift = self.__dict__["bit_shift"]
            _attr_data = pack_16_bit_arr(_values, _factor, _shift)
            evg_token_name = "Evg_values"
        else:
            _attr_data = self.__dict__["values"]

        if evg_token_name in {"Evg_values", "Evg_8bitValues", "Evg_16bitValues"}:
            _attr_data = _attr_data.flatten()

        try:
            _attr_data_length = len(_attr_data)
        except TypeError:
            if isinstance(_attr_data, int) or isinstance(_attr_data, float):
                _attr_data_length = 1
            else:
                _attr_data_length = 1

        tmp_length = pack("=q", _attr_data_length * calcsize(_token_info.fmtstr))
        _data_fmt_str = f"={_token_info.fmtstr}"
        tmp_bin = _attr_data.astype(_data_fmt_str).tobytes()
        log.debug(
            "Packing token: %s -- Attr data: %r",
            evg_token_name,
            _attr_data,
        )
        return b"".join([tmp_token, tmp_length, tmp_bin])

    def pack_history(self) -> bytes:
        tmp_token = pack("=I", Evg.history)
        history_lines = self.pygrd.head.history
        history_byte_chunks: list[bytes] = []
        for line in history_lines:
            _attr_data_length = len(line)

            tmp_length = pack("=q", _attr_data_length * calcsize("s"))

            line_bytes = str.encode(line)

            tmp_bin = pack(f"={_attr_data_length!s}s", line_bytes)
            log.debug("Packing token: Evg_history")
            history_byte_chunks.extend([tmp_token, tmp_length, tmp_bin])
        return b"".join(history_byte_chunks)

    def pack_units_token(self, evg_token: Evg) -> bytes:
        evg_token_name = Evg.token_to_token_name(evg_token)
        token = evg_token
        tmp_token = pack("=I", token)
        _token_info = Evg.evg_token(token)
        _attr_data_name = _token_info.dgpy_attr
        _attr_data = self.__dict__[_attr_data_name]
        _attr_data_length = 1
        tmp_length = pack("=q", _attr_data_length * calcsize(_token_info.fmtstr))
        # std lib loger
        log.info(
            "Packing token: %s -- Attr data: %r",
            evg_token_name,
            _attr_data,
        )
        if isinstance(_attr_data, str):
            _attr_data = Evu.string2enum(_attr_data)
        try:
            tmp_bin = pack(f"={_attr_data_length!s}{_token_info.fmtstr}", _attr_data)
        except _struct_err:
            if (
                _attr_data is None
                or _attr_data == b"unknown"
                or "units" in evg_token_name
            ):
                _attr_data = (-1,)
                _attr_data_length = 1
                tmp_length = pack(
                    "=q", _attr_data_length * calcsize(_token_info.fmtstr)
                )
            tmp_bin = pack(
                "=" + str(_attr_data_length) + _token_info.fmtstr, *_attr_data
            )
        return b"".join([tmp_token, tmp_length, tmp_bin])

    def _get_field_attr_data(self) -> str:
        _attr_data = self.__dict__.get("p_field", None)
        if _attr_data is None:
            _attr_data = self.__dict__.get("z_field", None)
        if not _attr_data:
            raise ValueError(
                "No field data found in PygrdWriterBase for token: 'field'"
            )
        if not isinstance(_attr_data, str):
            _attr_data = str(_attr_data)
        return _attr_data

    def pack_token(self, evg: Evg) -> bytes:
        evg_token = Evg.evg_token(evg)
        evg_token_name = evg_token.token_name
        token = evg
        if evg_token_name in {
            "Evg_values",
            "Evg_8bitValues",
            "Evg_16bitValues",
        }:
            return self.pack_array(evg_token_name)
        elif evg == Evg.history:
            return self.pack_history()
        elif evg in {Evg.punits, Evg.xyunits, Evg.zunits}:
            return self.pack_units_token(evg)
        tmp_token = pack("=I", token)
        _token_info = Evg.evg_token(token)
        _attr_data_name = _token_info.dgpy_attr
        _attr_data = ""

        if evg_token == Evg.field:
            _attr_data = self._get_field_attr_data()
        else:
            # direct access token
            try:
                _attr_data = self.__dict__[_attr_data_name]
            except KeyError:
                if _attr_data_name == "end_of_header":
                    _attr_data = ""
        try:
            _attr_data_length = len(_attr_data)
        except TypeError:
            if isinstance(_attr_data, int) or isinstance(_attr_data, float):
                _attr_data_length = 1
            else:
                _attr_data_length = 1

        tmp_length = pack("=q", _attr_data_length * calcsize(_token_info.fmtstr))
        if __config__.debug:
            log.debug("Packing token: %s -- Attr data: %s", evg_token_name, _attr_data)

        if isinstance(_attr_data, str):
            _attr_data = str.encode(_attr_data)  # type: ignore
        try:
            if _token_info.fmtstr == "s" and isinstance(_attr_data, str):
                _attr_data = str.encode(_attr_data)  # type: ignore

            tmp_bin = pack(
                "=" + str(_attr_data_length) + _token_info.fmtstr, _attr_data
            )
        except _struct_err:
            if (
                _attr_data is None
                or _attr_data == b"unknown"
                or "units" in evg_token_name
            ):
                _attr_data = (-1,)  # type: ignore
                _attr_data_length = 1
                tmp_length = pack(
                    "=q", _attr_data_length * calcsize(_token_info.fmtstr)
                )
            tmp_bin = pack(
                "=" + str(_attr_data_length) + _token_info.fmtstr, *_attr_data
            )
        return b"".join([tmp_token, tmp_length, tmp_bin])

    @abstractmethod
    def _bin_gen(self) -> Iterable[bytes]: ...

    @abstractmethod
    def write2buffer(self, buf: BinaryIO | BytesIO) -> None: ...

    @abstractmethod
    def save_grd(self, filepath: str) -> None:
        """Write out to a grid file

        Args:
            filepath (str): fspath (relative or absolute) of where to write

        Returns:
            None

        """
