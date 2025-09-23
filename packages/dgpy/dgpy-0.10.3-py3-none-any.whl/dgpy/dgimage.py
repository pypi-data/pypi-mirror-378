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
"""DGI image container and utility functions"""

from __future__ import annotations

from base64 import b64encode
from io import BytesIO
from typing import Any, TypeVar

import numpy as np

from imageio import v3 as iio
from requires.shed import requires_imageio, requires_ipython
from shellfish import fs, sh

from dgpy._types import FsPath
from dgpy.dgpydantic import DgpyBaseModel
from dgpy.xtypes import Arr

__all__ = (
    "DGImage",
    "ImgDims",
    "TDGImage",
)

TDGImage = TypeVar("TDGImage", bound="DGImage")


class ImgDims(DgpyBaseModel):
    """Image dimensions object"""

    height: int
    width: int
    channels: int


class DGImage(DgpyBaseModel):
    """DGI-image class"""

    arr: Arr
    filepath: FsPath | None = None
    fmt: str = "jpg"

    @classmethod
    @requires_imageio
    def from_filepath(cls: type[TDGImage], filepath: FsPath) -> TDGImage:
        """Read, create and return a DGImage object (or subclass) from an image fspath"""
        _fmt = "jpg"
        if str(filepath).lower().endswith("png"):
            _fmt = "png"
        img_arr = iio.imread(str(filepath))
        return cls(arr=img_arr, filepath=filepath, fmt=_fmt)

    @classmethod
    @requires_imageio
    def load(cls, filepath: FsPath) -> DGImage:
        """Load from fspath"""
        return cls.from_filepath(filepath=filepath)

    def filename(self) -> str:
        """Return image filepath"""
        if self.filepath is None:
            raise ValueError("Img fspath attr is None")
        return sh.basename(str(self.filepath))

    @requires_imageio
    def to_bytesio(self, fmt: str | None = None) -> BytesIO:
        """Write image array to BytesIO buffer and return the buffer"""
        bio = BytesIO()
        iio.imwrite(
            bio,
            self.arr,
            plugin="pillow",
            extension=".png" if self.fmt == "png" else ".jpg",
        )
        return bio

    def to_bytes(self, fmt: str | None = None) -> bytes:
        """Return the image array as bytes"""
        return self.to_bytesio(fmt).getvalue()

    @requires_imageio
    def write(self, uri: FsPath, *, fmt: str | None = None) -> None:
        """Save an image to a URI"""
        _fmt = fmt or self.fmt
        uri_str = str(uri)
        if uri_str.lower().endswith("png"):
            _fmt = "png"
        elif uri_str.lower().endswith("jpg") or uri_str.lower().endswith("jpeg"):
            _fmt = "jpg"
        if not uri_str.endswith(_fmt):
            uri = f"{uri}.{_fmt}"
        bites = self.to_bytes(fmt=_fmt)
        fs.write_bytes(uri, bites)

    @requires_imageio
    def save(self, uri: FsPath, *, fmt: str | None = None) -> None:
        """Alias of `write` method to save an image to a URI"""
        self.write(uri, fmt=fmt)

    @property
    def b64_bytes(self) -> bytes:
        """Return the base64 bytes for the image"""
        return b64encode(self.to_bytes())

    @property
    def b64_str(self) -> str:
        """Return the base64 string for the image"""
        return self.b64_bytes.decode()

    def html_img_bytes(self) -> bytes:
        """Return the html image tag as bytes"""
        return b"".join([
            b'<img src="data:image/',
            self.fmt.encode(),
            b";base64,",
            self.b64_bytes,
            b'">',
        ])

    def info(self) -> dict[str, str | tuple[int, ...]]:
        """Return image info in a dictionary"""
        return {
            "fmt": self.fmt,
            "shape": self.shape,
        }

    @property
    def shape(self) -> tuple[int, ...]:
        """Return the image array shape"""
        return self.arr.shape

    def dims(self) -> ImgDims:
        """Return an image dimensions object"""
        h, w, c = self.arr.shape
        return ImgDims(height=h, width=w, channels=c)

    @property
    def height(self) -> int:
        """Return the height of the image"""
        return int(self.arr.shape[0])

    @property
    def width(self) -> int:
        """Return the width of the image"""
        return int(self.arr.shape[1])

    @property
    def dtype(self) -> Any:
        """Return the image array data type"""
        return self.arr.dtype

    def is8bit(self) -> bool:
        """Return True if the image is an 8-bit image; False otherwise"""
        return self.arr.dtype == np.uint8

    def is16bit(self) -> bool:
        """Return True if the image is a 16-bit image; False otherwise"""
        return self.arr.dtype == np.uint16

    def html_img_str(self) -> str:
        """Return the image as an HTML <img/> tag"""
        return self.html_img_bytes().decode()

    def _repr_html_(self) -> str:
        """Return HTML string representation of the object"""
        return self.html_img_str()

    @requires_ipython
    def show(self, *, info: bool = False) -> None:
        """Show the latest image from the PyViewserver"""
        from IPython.core.display import HTML, display  # type: ignore[attr-defined]

        if info:
            display(HTML(f"<div><pre>{self.info()}</pre>{self.html_img_str()}</div>"))
        else:
            display(HTML(self.html_img_str()))

    def imdiff(self, other: DGImage) -> DGImage:
        """Return difference image between this image and another"""
        return DGImage(arr=Arr(np.abs(self.arr - other.arr)), fmt=self.fmt)

    def jupyter_show(self) -> None:
        """Show the image in jupyter"""
        return self.show()
