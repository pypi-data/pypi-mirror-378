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
"""Base object for py2grd and py3grd objects"""

from __future__ import annotations

from abc import abstractmethod
from typing import (
    TYPE_CHECKING,
    Any,
    BinaryIO,
)

import xarray as xr

from jsonbourne import JSON
from pydantic import Field

from dgpy.core.py6grd.evg import EvgNodeType
from dgpy.core.pyspace import PySpace
from dgpy.dgpydantic import DgpyBaseModel
from dgpy.maths import nanmax, nanmin

if TYPE_CHECKING:
    from collections.abc import Callable, Hashable

    import pandas as pd

    from dgpy import npt
    from dgpy._types import FsPath
    from dgpy.core.py6grd.py6grd_dto import PygrdHeaderDTO
    from dgpy.pydat import Pydat


class Py6grdHeaderBase(DgpyBaseModel):
    """Header base object; Subclassed by Py2grdHeader and Py3grdHeader"""

    xcol: int
    yrow: int
    zlev: int = Field(
        default=1,
        title="zlev",
        description="number of z-levels; will be 1 for Py2grdHeader",
    )

    space: PySpace

    filename: str | None = None

    node_range: tuple[float, float] = (0.0, 0.0)
    byte_order: str = "="
    angle: float = 0.0
    fspath: str | None = None

    property_node: int = EvgNodeType.standard
    desc: str = ""
    downward: bool = False
    dat: str = ""
    history: list[str] = Field(
        default=[], title="history", description="History list of strings"
    )

    # Array o' data related
    bit_factor: float = 1.0  # default factor is 1 b/c default is arr as is
    bit_shift: float = 0.0  # default shift is 0 b/c default has no shift

    # trend related
    trend_coefficients: tuple[int, ...] | None = None
    trend_offsets: tuple[int, ...] | None = None
    trend_order: Any = None
    data_order: int | None = None

    padding: int | None = None

    version: int | None = 80

    @property
    def angle_deg(self) -> float:
        """Return the angle in degrees"""
        return self.space.angle_deg

    @property
    def angle_rad(self) -> float:
        """Return the angle in radians"""
        return self.space.angle_rad

    @abstractmethod
    def dump_dict(self) -> dict[str, Any]: ...

    # ============
    # FROM/TO JSON
    # ============
    @classmethod
    def from_json(cls, json_string: bytes | str) -> Py6grdHeaderBase:
        data_dictionary = JSON.loads(json_string)
        return cls.model_validate(data_dictionary)

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
    @abstractmethod
    def _from_dto(cls, dto: PygrdHeaderDTO) -> Py6grdHeaderBase: ...

    def __repr__(self) -> str:
        return self.__str__()

    def _repr_html_(self) -> str:
        return self.__str__().replace("\n", "<br>")


class Py6grdBase(DgpyBaseModel):
    """DGPY 3grid"""

    head: Py6grdHeaderBase
    dataarray: xr.DataArray
    meta: dict[str, Any] = Field(default_factory=dict)

    # ==========
    # PROPERTIES
    # ==========

    @property
    def nparr(self) -> npt.NDArray:
        """Return the data values as a numpy-array for the Py3grd object"""
        return self.dataarray.values

    @nparr.setter
    def nparr(self, arr: npt.NDArray) -> None:
        """Set data-array values numpy array"""
        self.dataarray.values = arr

    @property
    def array_values(self) -> npt.NDArray:
        """Return the data values as a numpy-array for the Py3grd object"""
        return self.dataarray.values

    @array_values.setter
    def array_values(self, arr: npt.NDArray) -> None:
        """Set data-array values numpy array"""
        self.dataarray.values = arr

    @property
    def body(self) -> xr.DataArray:
        """Return the body/dataarray"""
        return self.dataarray

    @body.setter
    def body(self, dataarray: xr.DataArray) -> None:
        """Set data-array to another array"""
        self.dataarray = dataarray

    @property
    def da(self) -> xr.DataArray:
        """Return the body/dataarray"""
        return self.dataarray

    @da.setter
    def da(self, dataarray: xr.DataArray) -> None:
        """Set data-array to another array"""
        self.dataarray = dataarray

    @property
    def dims(self) -> tuple[Hashable, ...]:
        """Return the data values as a numpy-array for the Py3grd object"""
        return self.dataarray.dims

    @property
    def node_min(self) -> float:
        """Return the minimum node value for the grid"""
        return float(nanmin(self.dataarray.values))

    @property
    def node_max(self) -> float:
        """Return the max node value for the grid"""
        return float(nanmax(self.dataarray.values))

    @property
    def node_range(self) -> tuple[float, float]:
        """Return a tuple containing the grid node_min and node_max values"""
        return self.node_min, self.node_max

    @abstractmethod
    def _update_dimensions(self) -> None: ...

    def _update_node_range(self) -> None:
        """Set the header node_range to the grid node min and max values"""
        self.head.node_range = self.node_range

    def add_spatial_coordinates(self) -> None:
        raise NotImplementedError

    def dump_dict(self) -> dict[str, Any]:
        """Get the header data for a PyGrd object"""
        self._update_node_range()
        return self.head.dump_dict()

    def __str__(self) -> str:
        return "\n".join([
            "__HEADER_(dgpy.Py3grdHeader)__",
            self.head.__str__().replace("\n", "    \n"),
            "__BODY_(xr.DataArray)__",
            self.dataarray.__str__().replace("\n", "    \n"),
        ])

    def _repr_html_(self) -> str:
        return "\n".join((
            "<pre>__HEADER_(dgpy.Py3grdHeader)__",
            self.head._repr_html_(),
            "__BODY_(xr.DataArray)__",
            str(self.dataarray._repr_html_()),
            "</pre>",
        ))

    # ================
    # FROM/TO FILEPATH
    # ================
    @classmethod
    @abstractmethod
    def from_fspath(cls, fspath: FsPath, *, name: str | None = None) -> Py6grdBase:
        """Return a PyGrd object given a path to a 2/3 grid file

        Args:
            fspath (FsPath): fspath to a 2grd/3grd file
            name (str | None): Optional name for the grid; if not provided, will
                use the filename from the fspath

        Returns:
            Py2grd/Py3grd object

        """

    @classmethod
    @abstractmethod
    def from_filepath(cls, filepath: FsPath, *, name: str | None = None) -> Py6grdBase:
        """Return a PyGrd object given a path to a 2/3 grid file

        Args:
            filepath (FsPath): fspath to a 2grd/3grd file

        Returns:
            Py2grd/Py3grd object

        """

    @abstractmethod
    def to_fspath(self, fspath: FsPath) -> FsPath: ...

    @classmethod
    @abstractmethod
    def from_dataarray(cls, dataarray: xr.DataArray) -> Py6grdBase: ...

    @classmethod
    @abstractmethod
    def from_ndarray(cls, arr: npt.NDArray) -> Py6grdBase: ...

    def to_filepath(self, filepath: FsPath) -> FsPath:
        """Write to given filepath"""
        return self.to_fspath(fspath=filepath)

    def save(self, filepath: FsPath) -> FsPath:
        return self.to_fspath(fspath=filepath)

    @classmethod
    def from_buffer(cls, bites: bytes | BinaryIO) -> Py6grdBase:
        """Return a PyGrd object given a path to a 2/3 grid file

        Args:
            fspath (str): path to a 2grd/3grd/m3grd/c3grd file

        Returns:
            PyGrd object

        """
        raise NotImplementedError

    def _metadata(self) -> Any:
        return self.meta

    # ==================
    # FROM/TO DICTIONARY
    # ==================

    @classmethod
    def from_dict(cls, data: dict[Any, Any]) -> Py6grdBase:
        """Create Py2grd/Py3grd from dictionary"""
        raise NotImplementedError

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary from a Py2grd/Py3grd object"""
        return {"head": self.head.model_dump(), "dataarray": self._dataarray_to_dict()}

    def _dataarray_to_dict(self) -> dict:
        return self.dataarray.to_dict()

    def _dataarray_to_json(self) -> str:
        return JSON.dumps(self._dataarray_to_dict())

    # ============
    # FROM/TO JSON
    # ============
    @classmethod
    def from_json(cls, json_string: bytes | str) -> Py6grdBase:
        _dictionary = JSON.loads(json_string)
        return cls.from_dict(_dictionary)

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
            self.to_dict(),
            fmt=fmt,
            pretty=pretty,
            sort_keys=sort_keys,
            append_newline=append_newline,
            default=default,
            **kwargs,
        )

    # =============
    # FROM/TO PYDAT
    # =============

    @classmethod
    def from_pydat(cls, pydat: Pydat) -> Py6grdBase:
        raise NotImplementedError

    @abstractmethod
    def to_pydat(
        self,
        *,
        multiindex: bool = False,
        p_field: str | None = None,
        z_field: str | None = None,
    ) -> Pydat:
        """Convert and return as pydat object"""
        ...

    def to_dataframe(self, *, multiindex: bool = False) -> pd.DataFrame:
        """Return the Py2grd/Py3grd object data as a pandas.dataframe"""
        return self.to_pydat(multiindex=multiindex).to_dataframe()

    def is_bordered(self) -> bool:
        """Return True if Py2grd is bordered; False otherwise. (Py2grd only)

        Py3grds are never bordered
        """
        return False
