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
"""lib-multigrid dgpy"""

from __future__ import annotations

import datetime
import json
import logging
import math
import os
import re

from typing import TYPE_CHECKING, Any, Self, TypedDict, TypeVar

import h5
import h5py
import numpy as np
import xarray as xr

from dateutil.parser import parse
from pydantic import Field

from dgpy import maths, npt
from dgpy._types import FsPath
from dgpy.core.config import dgi_module
from dgpy.dgi_coordinate_systems import coordinate_system_dict
from dgpy.dgpydantic import DgpyBaseModel
from dgpy.libmultigrid._utils import (
    match_datetimes,
    strip_downward_suffix,
    units_string,
)
from dgpy.libmultigrid.attributes import Attribute, AttributeDump
from dgpy.libmultigrid.axis_label import AxisLabel
from dgpy.libmultigrid.enums import TimestepPrecision as TimestepPrecision
from dgpy.libmultigrid.h5_models import CsXy, CsZ, MetaGeneral
from dgpy.xtypes import Arr

if TYPE_CHECKING:
    from types import TracebackType

__all__ = (
    "PyMultigridSpace",
    "Pym2grdHeaderDump",
    "Pym3grdHeaderDump",
    "Pym6grdSpaceDump",
    "TimestepPrecision",
)

log = logging.getLogger(__name__)
TPym6grd = TypeVar("TPym6grd", bound="Pym6grd")


class Pym6grdSpaceDump(DgpyBaseModel):
    angle: float = Field(
        ..., description="Angle of rotation in degrees (positive is clockwise)"
    )
    downward: bool = Field(..., description="Is downward")
    xcol: int = Field(..., description="Number of columns")
    xmax: float = Field(..., description="Maximum X value")
    xmaxboundingbox: float = Field(..., description="Maximum X value")
    xmin: float = Field(..., description="Minimum X value")
    xminboundingbox: float = Field(..., description="Minimum X value")
    xpivot: float = Field(..., description="X pivot value")
    xrange: float = Field(..., description="X range value")
    ymax: float = Field(..., description="Maximum Y value")
    ymaxboundingbox: float = Field(..., description="Maximum Y value")
    ymin: float = Field(..., description="Minimum Y value")

    zmax: float = Field(..., description="Maximum Z value")
    zmin: float = Field(..., description="Minimum Z value")
    zminboundingbox: float = Field(..., description="Minimum Z value")
    zmaxboundingbox: float = Field(..., description="Maximum Z value")

    yminboundingbox: float = Field(..., description="Minimum Y value")
    ypivot: float = Field(..., description="Y pivot value")
    yrange: float = Field(..., description="Y range value")
    yrow: int = Field(..., description="Number of rows")
    zlev: int = Field(..., description="Number of levels")
    zpivot: float = Field(..., description="Z pivot")
    zrange: float = Field(..., description="Z range")


def available_dataset_paths(fspath: FsPath) -> list[str]:
    datasets = h5.datasets(fspath)
    pattern = re.compile(r"^\/attr\/property.*")
    return ["/".join(i[0].split("/")) for i in [*datasets] if pattern.match(i[0])]


def hdf5_dataset_to_numpy(
    h5file: h5py.File, dataset: Attribute, timestep: str = "static"
) -> npt.NDArray:
    if not dataset.uses_lut:
        dataset_path = f"/attr/property/{dataset.name.lower()}/{timestep}/values"
        ds = h5file.get(dataset_path)
        if ds is not None and isinstance(ds, h5py.Dataset):
            data = ds[:]
            data = np.where(data == 255.0, np.nan, data)
            return data
        else:
            raise KeyError(f"Dataset not found or invalid at path: {dataset_path}")
    else:
        dataset_path = (
            f"/attr/property/{dataset.name.lower()}/{timestep}/raw_values/values"
        )
        ds = h5file.get(dataset_path)
        if not isinstance(ds, h5py.Dataset):
            raise KeyError(f"Dataset not found or invalid at path: {dataset_path}")
        lut = h5file[f"/attr/property/{dataset.name.lower()}/{timestep}/lut"]
        if not isinstance(lut, h5py.Dataset):
            raise KeyError(f"LUT not found or invalid at path: {lut.name}")
        lut_array = lut[()]
        if lut.attrs["lut_type"] == "factor_shift":
            factor, offset = lut_array
            return ds * factor + offset
        else:
            lut_len = len(lut)
            lut_extended = np.append(lut, b"")
            raw_values_masked = np.where(ds != 255, ds, lut_len)
            data_masked = lut_extended[raw_values_masked]
            data = np.where(data_masked == 255.0, np.nan, data_masked)
            return data


def check_for_single_timestamp(h5file: TPym6grd, attr_name: str) -> str | None | None:
    data = h5file.dataset_paths
    for i in data:
        path_parts = i.split("/")
        if path_parts[3] == attr_name and path_parts[4] != "static":
            return path_parts[4]
    return None


class Pym2grdHeaderDump(DgpyBaseModel):
    alias: str
    angle: float
    attributes: list[AttributeDump]
    coordinate_system_id: str
    coordinate_system_name: str
    desc: str
    downward: bool
    history: list[str] = Field([], description="File history")
    number_of_attributes: int = Field(-1, description="Number of attributes")
    number_of_time_steps: int = Field(0, description="Number of attributes")
    type: str = Field("pym2grd", description="File type")
    version: int
    xcol: int
    xmax: float = Field(..., description="Maximum X value")
    xmaxboundingbox: float
    xmin: float = Field(..., description="Minimum X value")
    xminboundingbox: float
    xpivot: float
    xrange: float
    xyunits: str
    ymax: float = Field(..., description="Maximum Y value")
    ymaxboundingbox: float
    ymin: float = Field(..., description="Minimum Y value")
    yminboundingbox: float
    ypivot: float
    yrange: float
    yrow: int
    zlev: int
    zunits: str

    # Optional fields
    time_steps: list[str] = Field([], description="List of time steps")
    z_datum_above_msl: float | None = Field(
        None, description="Z datum above mean sea level"
    )
    zpivot: float | None = Field(None, description="Z pivot")
    zrange: float | None = Field(None, description="Z range")


class Pym3grdHeaderDump(DgpyBaseModel):
    alias: str
    angle: float
    attributes: list[AttributeDump]
    coordinate_system_id: str
    coordinate_system_name: str
    desc: str
    downward: bool
    history: list[str]
    number_of_attributes: int
    type: str = Field("multi-attribute 3D grid", description="Type of model")
    version: int = Field(..., description="Version number")
    xcol: int = Field(..., description="Number of columns")
    xmax: float = Field(..., description="Maximum X value")
    xmaxboundingbox: float
    xmin: float = Field(..., description="Minimum X value")
    xminboundingbox: float
    xpivot: float
    xrange: float
    xyunits: str
    ymax: float = Field(..., description="Maximum Y value")
    ymaxboundingbox: float
    ymin: float = Field(..., description="Minimum Y value")

    zmax: float = Field(..., description="Maximum Z value")
    zmin: float = Field(..., description="Minimum Z value")
    zmaxboundingbox: float | None = Field(None, description="Z max bounding box")
    zminboundingbox: float | None = Field(None, description="Z min bounding box")

    axis_labeling: list[AxisLabel] | None = Field(None, description="Axis labeling")

    yminboundingbox: float
    ypivot: float
    yrange: float
    yrow: int
    zlev: int
    zunits: str

    # Optional fields
    time_steps: list[str] = Field([], description="List of time steps")
    number_of_time_steps: int = Field(0, description="Number of time steps")
    z_datum_above_msl: float | None = Field(
        None, description="Z datum above mean sea level"
    )
    zpivot: float = Field(..., description="Z pivot")
    zrange: float = Field(..., description="Z range")
    date: datetime.datetime | datetime.date | str | None = Field(
        None, description="Date attribute"
    )


class SpaceDumpDict(TypedDict):
    angle: float
    downward: bool
    xcol: int
    yrow: int
    zlev: int
    xmin: float
    xmax: float
    ymin: float
    ymax: float
    zmin: float
    zmax: float
    xminboundingbox: float
    xmaxboundingbox: float
    yminboundingbox: float
    ymaxboundingbox: float
    zminboundingbox: float
    zmaxboundingbox: float
    xpivot: float
    ypivot: float
    zpivot: float
    xrange: float
    yrange: float
    zrange: float


class PyMultigridSpace(DgpyBaseModel):
    """Multigrid space object"""

    brick_size: Arr  # float
    resolution: Arr  # int
    ijk_to_xyz: Arr  # float

    @property
    def transform_matrix(self) -> npt.NDArray:
        """Returns the IJK2XYZ 3x3 transformation matrix"""
        return self.ijk_to_xyz.reshape(3, 4)[:, :-1]

    def transform_det(self) -> float:
        """Returns the determinant of the IJK2XYZ 3x3 transformation matrix"""
        return np.linalg.det(self.transform_matrix)

    def is_downward(self) -> bool:
        """Returns True if the Z axis is downward

        transform matrix determinant is positive if the Z axis is downward
        """
        return self.transform_det() > 0

    @property
    def shift(self) -> npt.NDArray:
        """Returns the 3x1 shift vector for the ijk 2 xyz transformation"""
        return self.ijk_to_xyz.reshape(3, 4)[:, -1]

    def corner_point_indices(self) -> npt.NDArray:
        i, j, k = (el - 1 for el in self.resolution)
        inds: npt.NDArray = np.array([
            (0, 0, 0),
            (i, 0, 0),
            (0, j, 0),
            (0, 0, k),
            (i, j, 0),
            (0, j, k),
            (i, 0, k),
            (i, j, k),
        ])
        return inds

    def ijk2xyz(self, ijk: npt.NDArray) -> npt.NDArray:
        assert ijk.shape == (3,) or ijk.shape[1] == 3
        if ijk.shape == (3,):
            return ijk.dot(self.transform_matrix) + self.shift
        return ijk.dot(self.transform_matrix.transpose()) + self.shift

    def corners_xyz(self) -> npt.NDArray:
        return self.ijk2xyz(self.corner_point_indices())

    @property
    def angle_rad(self) -> float:
        return -1 * maths.angle(
            np.array([1, 0, 0]),
            np.array(self.ijk_to_xyz[::4]),
        )

    @property
    def xcol(self) -> int:
        return int(self.resolution[0])

    @property
    def yrow(self) -> int:
        return int(self.resolution[1])

    @property
    def zlev(self) -> int:
        return int(self.resolution[2])

    @property
    def angle_deg(self) -> float:
        return np.rad2deg(self.angle_rad)

    @property
    def angle(self) -> float:
        return self.angle_deg

    def zrange_2d(self) -> float:
        return math.fabs(self.ijk_to_xyz[10])

    def is_2d(self) -> bool:
        return self.resolution[2] == 1

    def space_dump_dict(self) -> SpaceDumpDict:
        res = self.corners_xyz()
        downward: bool = self.is_downward()
        pivot = res[0]

        xpivot, ypivot, zpivot = pivot

        i_axis_corner = res[1]
        j_axis_corner = res[2]

        _loc_xaxis = i_axis_corner - pivot
        xrange = float(np.sqrt(np.dot(_loc_xaxis, _loc_xaxis)))
        _loc_yaxis = j_axis_corner - pivot
        yrange = float(np.sqrt(np.dot(_loc_yaxis, _loc_yaxis)))

        if self.is_2d():
            zrange = self.zrange_2d()
        else:
            k_axis_corner = res[3]
            _loc_zaxis = k_axis_corner - pivot
            zrange = float(np.sqrt(np.dot(_loc_zaxis, _loc_zaxis)))
            if not self.is_downward():
                zpivot = zpivot - zrange
        xmax: int = np.max(res[:, 0])
        xmin: int = np.min(res[:, 0])
        ymax: int = np.max(res[:, 1])
        ymin: int = np.min(res[:, 1])
        zmax: int = np.max(res[:, 2])
        zmin: int = np.min(res[:, 2])
        return {
            "angle": self.angle,
            "downward": downward,
            "xcol": self.xcol,
            "yrow": self.yrow,
            "zlev": self.zlev,
            "xmin": xmin,
            "xmax": xmax,
            "ymin": ymin,
            "ymax": ymax,
            "zmin": zmin,
            "zmax": zmax,
            "xminboundingbox": xmin,
            "xmaxboundingbox": xmax,
            "yminboundingbox": ymin,
            "ymaxboundingbox": ymax,
            "zminboundingbox": zmin,
            "zmaxboundingbox": zmax,
            "xpivot": xpivot,
            "ypivot": ypivot,
            "zpivot": zpivot,
            "xrange": xrange,
            "yrange": yrange,
            "zrange": zrange,
        }

    def space_dump(self) -> Pym6grdSpaceDump:
        return Pym6grdSpaceDump.model_construct(**self.space_dump_dict())


class Pym6grdHeader(DgpyBaseModel):
    """Pym6grdHeader base class"""

    attributes: list[Attribute] = Field([], description="List of attributes")
    time_steps: list[str] = Field([], description="List of time steps")
    coordinate_system_id: str = Field("unknown", description="Coordinate system ID")

    def _attributes_dump(self) -> list[AttributeDump]:
        return [attr.to_attribute_dump() for attr in self.attributes]

    @property
    def number_of_timesteps(self) -> int:
        return -1 if self.time_steps is None else len(list(self.time_steps))

    @property
    def number_of_attributes(self) -> int:
        return len(self.attributes)

    @property
    def coordinate_system_name(self) -> str:
        data = coordinate_system_dict()
        return data[self.coordinate_system_id]


class Pym2grdHeader(Pym6grdHeader):
    space: PyMultigridSpace = Field(..., description="Space object")
    alias: str = Field("", description="Alias")
    attributes: list[Attribute] = Field([], description="List of attributes")

    desc: str = Field("", description="Description")
    history: list[str] = Field([], description="History")
    type: str = Field("multi-attribute 2D grid", description="Type of multi-grid")
    version: int = Field(-1, description="Version number")
    xyunits: str = Field("unknown", description="XY units")
    zunits: str = Field("unknown", description="Z units")

    timestep_properties: set[str] | None = Field(
        None, description="Properties with timesteps"
    )
    z_datum_above_msl: float | None = Field(
        None, description="Z datum above mean sea level"
    )

    def dump(self) -> Pym2grdHeaderDump:
        """Pym2grd header dump; re-implementation of `cv_dump -J`"""
        is_downward = self.space.is_downward()
        space_dump = self.space.space_dump()

        return Pym2grdHeaderDump.model_construct(
            # use pydantic construct bc we know the types
            alias=self.alias,
            attributes=self._attributes_dump(),
            coordinate_system_id=self.coordinate_system_id,
            coordinate_system_name=self.coordinate_system_name,
            desc=self.desc,
            history=self.history,
            number_of_attributes=self.number_of_attributes,
            number_of_time_steps=self.number_of_timesteps,
            time_steps=self.time_steps if self.time_steps else [],
            type=self.type,
            version=self.version,
            z_datum_above_msl=self.z_datum_above_msl,
            xyunits=units_string(self.xyunits, downward=is_downward),
            zunits=units_string(self.zunits, downward=is_downward),
            # from space dump
            angle=space_dump.angle,
            downward=space_dump.downward,
            xcol=space_dump.xcol,
            xmax=space_dump.xmax,
            xmaxboundingbox=space_dump.xmaxboundingbox,
            xmin=space_dump.xmin,
            xminboundingbox=space_dump.xminboundingbox,
            xpivot=space_dump.xpivot,
            xrange=space_dump.xrange,
            ymax=space_dump.ymax,
            ymaxboundingbox=space_dump.ymaxboundingbox,
            ymin=space_dump.ymin,
            yminboundingbox=space_dump.yminboundingbox,
            ypivot=space_dump.ypivot,
            yrange=space_dump.yrange,
            yrow=space_dump.yrow,
            zlev=space_dump.zlev,
            zpivot=space_dump.zpivot,
            zrange=space_dump.zrange,
        )


class Pym3grdHeader(Pym6grdHeader):
    space: PyMultigridSpace = Field(..., description="Space object")
    alias: str = Field("", description="Alias")
    attributes: list[Attribute] = Field([], description="List of attributes")
    desc: str = Field("", description="Description")
    date: datetime.datetime | datetime.date | str | None = Field(
        None, description="Date attribute"
    )
    history: list[str] = Field([], description="History")
    type: str = Field("multi-attribute 3D grid", description="Type of multi-grid")
    version: int = Field(-1, description="Version number")
    xyunits: str = Field("unknown", description="XY units")
    zunits: str = Field("unknown", description="Z units")
    time_steps: list[str] = Field([], description="List of time steps")
    axis_labeling: list[AxisLabel] | None = Field(None, description="Axis labeling")
    z_datum_above_msl: float | None = Field(
        None, description="Z datum above mean sea level"
    )
    timestep_properties: set[str] | None = Field(
        None, description="Properties with timesteps"
    )

    def dump(self) -> Pym3grdHeaderDump:
        """Pym3grd header dump; re-implementation of `cv_dump -J`"""
        is_downward = self.space.is_downward()
        space_dump = self.space.space_dump()
        return Pym3grdHeaderDump.model_construct(
            alias=self.alias,
            attributes=self._attributes_dump(),
            axis_labeling=self.axis_labeling,
            coordinate_system_id=self.coordinate_system_id,
            coordinate_system_name=self.coordinate_system_name,
            date=self.date,
            desc=self.desc,
            history=self.history,
            number_of_attributes=self.number_of_attributes,
            number_of_time_steps=self.number_of_timesteps,
            time_steps=self.time_steps if self.time_steps else [],
            type=self.type,
            version=self.version,
            z_datum_above_msl=self.z_datum_above_msl,
            xyunits=self.xyunits,
            zunits=units_string(self.zunits, downward=is_downward),
            # from space dump
            angle=space_dump.angle,
            downward=space_dump.downward,
            xcol=space_dump.xcol,
            xmax=space_dump.xmax,
            xmaxboundingbox=space_dump.xmaxboundingbox,
            xmin=space_dump.xmin,
            xminboundingbox=space_dump.xminboundingbox,
            xpivot=space_dump.xpivot,
            xrange=space_dump.xrange,
            ymax=space_dump.ymax,
            ymaxboundingbox=space_dump.ymaxboundingbox,
            ymin=space_dump.ymin,
            zmax=space_dump.zmax,
            zmin=space_dump.zmin,
            zminboundingbox=space_dump.zminboundingbox,
            zmaxboundingbox=space_dump.zmaxboundingbox,
            yminboundingbox=space_dump.yminboundingbox,
            ypivot=space_dump.ypivot,
            yrange=space_dump.yrange,
            yrow=space_dump.yrow,
            zlev=space_dump.zlev,
            zpivot=space_dump.zpivot,
            zrange=space_dump.zrange,
            # **{k: v for k, v in self.space.space_dump_dict().items() if k},
        )


def copy_group(
    source_group: h5py.File | h5py.Group,
    target_group: h5py.File | h5py.Group,
) -> None:
    # Copy all datasets in the group
    for name, obj in source_group.items():
        if isinstance(obj, h5py.Dataset):
            if obj.dtype.kind == "S":
                # If the dataset contains strings, convert them to bytes
                data = obj.value
            else:
                # Otherwise, copy the data directly
                data = obj[:]

            target_group.create_dataset(
                name, data=data, shape=obj.shape, dtype=obj.dtype
            )

            # Copy attributes
            for key, value in obj.attrs.items():
                target_group[name].attrs[key] = value

        elif isinstance(obj, h5py.Group):
            # Recursively copy subgroups

            subgroup_target = target_group.create_group(name)
            for key, value in obj.attrs.items():
                target_group[name].attrs[key] = value
            copy_group(obj, subgroup_target)

        # Recursively copy all groups in the input file


class Pym6grd(DgpyBaseModel):
    """dgpy base class for m2grd and m3grd"""

    fspath: FsPath
    mode: str

    @classmethod
    def open(cls, fspath: FsPath, mode: str = "r") -> Self:
        assert mode in ["r", "rw"], "file mode must be either r or rw"
        return cls(fspath=fspath, mode=mode)

    def __enter__(self: TPym6grd) -> TPym6grd:
        return self

    def __exit__(
        self,
        exc_type: BaseException | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...

    @property
    def header(self) -> Pym2grdHeader | Pym3grdHeader:
        raise NotImplementedError("Subclasses must implement the header property")

    def attribute_dict(self) -> dict[str, Attribute]:
        attr_dict = {i.name.lower(): i for i in self.header.attributes}
        for attr_name, attr_obj in attr_dict.items():
            attr_obj.uses_lut = any(
                True
                for i in self.dataset_paths
                if i.endswith("/lut") and f"/{attr_name}/" in i
            )
            single_timestep = check_for_single_timestamp(self, attr_name)
            if not getattr(attr_obj, "time_steps", None) and single_timestep:
                attr_obj.temporal = True
                attr_obj.time_steps = [single_timestep]
        return attr_dict

    def attributes_as_json(self) -> str:
        attr_dict = {i.name.lower(): i.model_dump() for i in self.header.attributes}

        for attr in attr_dict:
            attr_dict[attr]["uses_lut"] = any(
                True
                for i in self.dataset_paths
                if i.endswith("/lut") and f"/{attr}/" in i
            )
            single_timestep = check_for_single_timestamp(self, attr)
            if not attr_dict[attr]["time_steps"] and single_timestep:
                attr_dict[attr]["temporal"] = True
                attr_dict[attr]["time_steps"] = [single_timestep]
            attr_dict[attr] = {
                k: v
                for k, v in attr_dict[attr].items()
                if k in ["time_steps", "temporal"]
            }
        dict_string = json.dumps(attr_dict, indent=4)
        return dict_string

    @property
    def dataset_paths(self) -> list[str]:
        return available_dataset_paths(self.fspath)

    def space(self) -> PyMultigridSpace:
        return self.header.space

    def to_dataset(self) -> xr.Dataset:
        raise NotImplementedError("Subclasses must implement the to_dataset method")

    def to_dataarray(
        self, attr_name: str, timeslice: str | None = None
    ) -> xr.DataArray:
        dataset = self.to_dataset()
        if timeslice:
            try:
                return dataset.sel(time=timeslice)[attr_name]
            except KeyError:
                raise KeyError(f"Invalid timeslice. {timeslice}") from None
        else:
            return dataset[attr_name]

    def _to_mgrid(self, output_filepath: FsPath) -> None:
        with (
            h5py.File(self.fspath, "r") as infile,
            h5py.File(output_filepath, "w") as outfile,
        ):
            copy_group(infile, outfile)


class Pym2grd(Pym6grd):
    """dgpy m2grd"""

    @property
    def header(self) -> Pym2grdHeader:
        m2grd_reader = Pym2grdReader(self.fspath)
        m2grd_header = m2grd_reader.read_header()
        return m2grd_header

    def dump(self) -> Pym2grdHeaderDump:
        return self.header.dump()

    def get_xyz(self) -> tuple[npt.NDArray, npt.NDArray]:
        """Get x,y,z arrays from header"""
        m2grd_dump = self.dump()

        xarr = np.linspace(
            start=m2grd_dump.xmin, stop=m2grd_dump.xmax, num=m2grd_dump.xcol
        )
        yarr = np.linspace(
            start=m2grd_dump.ymin, stop=m2grd_dump.ymax, num=m2grd_dump.yrow
        )
        return (xarr, yarr)

    def to_dataset(self) -> xr.Dataset:
        with h5py.File(self.fspath, "r") as file:
            dataarray_dict = {}
            yarr, xarr = self.get_xyz()
            attrs = self.attribute_dict()
            for attr_name in attrs:
                attr = attrs[attr_name]
                if attr.temporal:
                    coords = [
                        ("time", np.array(sorted([parse(i) for i in attr.time_steps]))),
                        ("y", yarr),
                        ("x", xarr),
                    ]
                    timestep_collection = [
                        np.squeeze(hdf5_dataset_to_numpy(file, attr, j))
                        for j in attr.time_steps
                    ]
                    timestep_collection = [
                        np.where(np.isinf(i), np.nan, i) for i in timestep_collection
                    ]
                    dataarray_dict[attr_name] = xr.DataArray(
                        timestep_collection, coords=coords
                    )
                else:
                    coords = [("y", yarr), ("x", xarr)]
                    dataset = np.squeeze(hdf5_dataset_to_numpy(file, attr, "static"))
                    if dataset.dtype != "object":
                        dataset = np.where(np.isinf(dataset), np.nan, dataset)
                    dataarray_dict[attr_name] = xr.DataArray(dataset, coords=coords)

        return xr.Dataset(dataarray_dict)

    def to_m2grd(self, output_filepath: FsPath) -> None:
        """Opens up file at fspath and copies hdf5 file to new file at output_filepath"""
        assert str(output_filepath).endswith(".m2grd"), (
            "output_filepath must have .m2grd extension"
        )
        self._to_mgrid(output_filepath)

    def add_attribute(self, attr_name: str, data: xr.DataArray) -> None:
        """Add a hdf5 dataset using a xarray dataarray as input.

        Currently only supports static datasets.
        TODO: write to new file
        TODO: add support for temporal datasets
        """
        assert self.mode == "rw", (
            "File must be opened in read-write mode (rw) to add attribute"
        )

        data = data[np.newaxis, :]
        new_attr_shape = np.array(data.shape)[np.array([2, 1, 0])]

        if not np.array_equal(new_attr_shape, self.header.space.brick_size):
            raise ValueError("dataarray shape does not match m3grd shape")

        data_remapped = np.array(data)
        data_remapped[np.isnan(data_remapped)] = np.inf

        with h5py.File(self.fspath, "a") as file:
            new_group = file.create_group(f"/attr/property/{attr_name}")
            new_group.attrs["name"] = attr_name
            new_group.attrs["type"] = "numeric"
            new_group.attrs["unit"] = "none"

            static_group = new_group.create_group("static")
            static_group.attrs["DIMENSION_LABELS"] = ["J", "I", "K"]
            static_group.attrs["extents"] = data_remapped.shape
            static_group.attrs["max"] = np.nanmax(data)
            static_group.attrs["min"] = np.nanmin(data)
            static_group.attrs["null_count"] = np.sum(np.isinf(data_remapped))
            static_group.attrs["null_value"] = 255

            static_group.create_dataset("values", data=data_remapped)


class Pym3grd(Pym6grd):
    """dgpy m3grd"""

    @property
    def header(self) -> Pym3grdHeader:
        m3grd_reader = Pym3grdReader(self.fspath)
        return m3grd_reader.read_header()

    def dump(self) -> Pym3grdHeaderDump:
        return self.header.dump()

    def get_xyz(self) -> tuple[npt.NDArray, npt.NDArray, npt.NDArray]:
        """Get x,y,z arrays from header."""
        m3grd_dump = self.dump()

        xarr = np.linspace(
            start=m3grd_dump.xmin, stop=m3grd_dump.xmax, num=m3grd_dump.xcol
        )
        yarr = np.linspace(
            start=m3grd_dump.ymin, stop=m3grd_dump.ymax, num=m3grd_dump.yrow
        )
        zarr = np.linspace(
            start=m3grd_dump.zmin, stop=m3grd_dump.zmax, num=m3grd_dump.zlev
        )

        return (xarr, yarr, zarr)

    def to_dataset(self) -> xr.Dataset:
        """Convert m3grd to xarray dataset."""
        with h5py.File(self.fspath, "r") as file:
            dataarray_dict = {}
            xarr, yarr, zarr = self.get_xyz()
            attrs = self.attribute_dict()

            for attr_name in attrs:
                attr = attrs[attr_name]
                if attr.temporal:
                    coords = [
                        ("time", np.array(sorted([parse(i) for i in attr.time_steps]))),
                        ("y", yarr),
                        ("x", xarr),
                        ("z", zarr),
                    ]
                    timestep_collection = [
                        hdf5_dataset_to_numpy(file, attr, j) for j in attr.time_steps
                    ]
                    timestep_collection = [
                        np.where(np.isinf(i), np.nan, i) for i in timestep_collection
                    ]
                    dataarray_dict[attr_name] = xr.DataArray(
                        timestep_collection, coords=coords
                    )
                else:
                    coords = [("y", yarr), ("x", xarr), ("z", zarr)]
                    dataset = hdf5_dataset_to_numpy(file, attr, "static")
                    if dataset.dtype != "object":
                        dataset = np.where(np.isinf(dataset), np.nan, dataset)
                    dataarray_dict[attr_name] = xr.DataArray(dataset, coords=coords)

        return xr.Dataset(dataarray_dict)

    def to_netcdf(self, output_filepath: FsPath) -> None:
        """Export m3grd to netcdf file.

        For this file to be viewable in ESRI ArcGIS Pro, we must transpose the
        data to the order expected by that software.
        """
        # ensure netcdf4 library is installed
        try:
            import netCDF4
        except ImportError as ie:
            raise ImportError(
                "netCDF4 library is required for this method: pip install netcdf4"
            ) from ie

        pref = dgi_module()

        def datetime_to_epoch(datetime_str: str) -> int:
            """Convert datetime string to time since epoch in milliseconds."""
            datetime_str = datetime_str.replace("T", " ")
            datetime_str = datetime_str[:23]
            dateformat_options = [
                "%Y-%m-%d %H:%M:%S.%f",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M",
                "%Y-%m-%d",
            ]

            for fmt in dateformat_options:
                try:
                    dt_val = datetime.datetime.strptime(datetime_str, fmt)
                    if dt_val.year >= 1970:
                        return int(dt_val.timestamp())
                    else:
                        raise ValueError(
                            f"Invalid datetime string: {datetime_str}. Must be after 1970."
                        )
                except (TypeError, LookupError):
                    pass

            raise ValueError(
                f"Invalid datetime string: {datetime_str}. Must be in ISO 8601 format."
            )

        data_type_mapping = {
            "int32": "i4",
            "int64": "i8",
            "float32": "f4",
            "float64": "f8",
            "str": "S1",
        }

        # get CRS and WKT for output attributes
        file_crs = pref.dump("-c", self.fspath).stdout.strip()
        file_wkt_lines = [
            i.strip() for i in pref.dem("-W", file_crs).stdout.split("\n")
        ]
        file_wkt = "".join(file_wkt_lines)
        if file_crs.startswith("L"):
            raise ValueError(
                "File is in local rectangular coordinates. Input file must have geographic or projected coordinates."
            )

        file_grid_mapping_name = (
            "latitude_longitude" if file_crs.startswith("G") else "projected"
        )
        ds = self.to_dataset()

        lowerleft_x = ds.x.min().values
        lowerleft_y = ds.y.min().values
        max_depth = ds.z.max().values
        cellsize = ds.x[1].values - ds.x[0].values
        rowsize = ds.y[1].values - ds.y[0].values
        layersize = ds.z[1].values - ds.z[0].values

        no_rows = ds.sizes["y"]
        no_cols = ds.sizes["x"]
        no_depths = ds.sizes["z"]

        y_vals = np.arange(lowerleft_y, lowerleft_y + rowsize * no_rows, rowsize)
        x_vals = np.arange(lowerleft_x, lowerleft_x + cellsize * no_cols, cellsize)
        depth_vals = np.arange(
            max_depth, max_depth - layersize * no_depths, layersize * -1
        )

        time_vals = []
        if "time" in ds.dims:
            time_strings = [str(time) for time in ds.time.values]
            time_vals = [datetime_to_epoch(dt_str) for dt_str in time_strings]

        try:
            with netCDF4.Dataset(
                output_filepath, "w", format="NETCDF4", set_auto_mask=False
            ) as nc_file:
                nc_file.source = "DGPY"
                nc_file.Conventions = "CF-1.6"
                nc_file.history = "Created using Dynamic Graphics Python API"

                is_temporal = "time" in ds.dims

                # Create Dimensions
                nc_file.createDimension("y", no_rows)
                nc_file.createDimension("x", no_cols)
                nc_file.createDimension("z", no_depths)
                if is_temporal and time_vals:
                    nc_file.createDimension("time", len(time_vals))

                # Create Variables
                crs_var = nc_file.createVariable(
                    "crs", "l", (), fill_value=-9999, zlib=True
                )
                crs_var.standard_name = "crs"
                crs_var.grid_mapping_name = file_grid_mapping_name
                crs_var.crs_wkt = file_wkt

                y_var = nc_file.createVariable("y", "f4", ("y"), fill_value=-9999)
                y_var.units = "degrees_north" if file_crs.startswith("G") else "meters"
                y_var.standard_name = (
                    "latitude"
                    if file_crs.startswith("G")
                    else "projection_y_coordinate"
                )
                y_var.axis = "Y"
                y_var[:] = y_vals

                x_var = nc_file.createVariable("x", "f4", ("x"), fill_value=-9999)
                x_var.units = "degrees_east" if file_crs.startswith("G") else "meters"
                x_var.standard_name = (
                    "longitude"
                    if file_crs.startswith("G")
                    else "projection_x_coordinate"
                )
                x_var.axis = "X"
                x_var[:] = x_vals

                depth_var = nc_file.createVariable("z", "f4", ("z"), fill_value=-9999)
                depth_var.short_name = "z"
                depth_var.standard_name = "z"
                depth_var.positive = "up"
                depth_var.units = "meters"
                depth_var.axis = "Z"
                depth_var[:] = depth_vals

                if is_temporal:
                    time_var = nc_file.createVariable(
                        "time", "i4", ("time"), fill_value=-9999
                    )
                    time_var.units = "seconds since 1970-01-01 00:00:00"
                    time_var.standard_name = "time"
                    time_var.long_name = "time"
                    time_var[:] = time_vals

                # Loop through data variables and create netCDF variables
                for var in ds.data_vars:
                    # get dimensions and their indices
                    dimensions = ds[var].dims
                    dim_indices = {dim: idx for idx, dim in enumerate(dimensions)}
                    z_index = dim_indices.get("z")
                    x_index = dim_indices.get("x")
                    y_index = dim_indices.get("y")
                    t_index = dim_indices.get("time") if is_temporal else None

                    # get data type and assign order of output dimensions
                    data_type = str(ds[var].dtype)
                    output_dtype = data_type_mapping.get(data_type, "f4")
                    output_dims = (
                        ("time", "z", "y", "x") if is_temporal else ("z", "y", "x")
                    )

                    # create netCDF variable, assign data in correct order
                    temp_var = nc_file.createVariable(
                        var, output_dtype, output_dims, fill_value=-9999
                    )
                    temp_var.short_name = var
                    temp_var.standard_name = var
                    temp_var.units = "undefined"
                    temp_var.grid_mapping = "crs"

                    vals = ds[var].values
                    if is_temporal and t_index is not None:
                        transposed_vals = np.transpose(
                            vals,
                            [
                                i
                                for i in (t_index, z_index, y_index, x_index)
                                if i is not None
                            ],
                        )
                        for t, _ in enumerate(time_vals):
                            temp_var[t, :, :, :] = transposed_vals[t, :, :, :]
                    else:
                        transposed_vals = np.transpose(
                            vals,
                            [i for i in (z_index, y_index, x_index) if i is not None],
                        )
                        temp_var[:, :, :] = transposed_vals

        except Exception as e:
            log.exception("Error converting m3grd to netCDF", exc_info=e)
            if os.path.exists(output_filepath):
                os.remove(output_filepath)
            exit(1)
        log.debug("NetCDF file created successfully at %s", output_filepath)

    def update_attribute(self, attr: str, data: xr.DataArray) -> None:
        """Update a hdf5 dataset using a xarray dataarray as input.

        Currently only supports static datasets.
        """
        ...

    def add_attribute(
        self, attr_name: str, data: xr.DataArray, dtype: str = "numeric"
    ) -> None:
        """Add a hdf5 dataset using a xarray dataarray as input.

        Currently only supports static datasets.
        TODO: add support for temporal datasets
        """
        assert self.mode == "rw", (
            "File must be opened in read-write mode (rw) to add attribute"
        )

        new_attr_shape = np.array(data.shape)[np.array([1, 0, 2])]
        if not np.array_equal(new_attr_shape, self.header.space.brick_size):
            raise ValueError("dataarray shape does not match m3grd shape")

        if len(data.shape) > 3:
            raise ValueError("dataarray shape must be 3 dimensional")

        if dtype == "string":
            with h5py.File(self.fspath, "a") as file:
                new_group = file.create_group(f"/attr/property/{attr_name}")
                new_group.attrs["name"] = attr_name
                new_group.attrs["type"] = attr_name.lower()
                new_group.attrs["unit"] = "non-numeric"

                static_group = new_group.create_group("static")
                raw_values_group = static_group.create_group("raw_values")

                arr = np.array(data)
                dataset_without_nulls = arr[~np.equal(arr, None)]  # type: ignore
                unique_values, indices = np.unique(
                    dataset_without_nulls, return_inverse=True
                )
                lut = np.array(unique_values, dtype="|O")
                raw_values = np.full(arr.shape, 255)
                raw_values[arr is not None] = indices

                lut = static_group.create_dataset("lut", data=lut)
                lut_usage_values = np.arange(lut.size)
                lut.attrs["lut_type"] = "string_lut_sorted"
                raw_values_group.attrs["DIMENSION_LABELS"] = ["J", "I", "K"]
                raw_values_group.attrs["extents"] = arr.shape
                raw_values_group.attrs["max"] = lut.size
                raw_values_group.attrs["min"] = 0
                raw_values_group.attrs["null_count"] = 0
                raw_values_group.attrs["null_value"] = 255
                raw_values_group.create_dataset(
                    "values", data=raw_values, dtype="uint8"
                )
                raw_values_group.create_dataset(
                    "usage_set", data=lut_usage_values, dtype="uint8"
                )

        elif dtype == "numeric":
            with h5py.File(self.fspath, "a") as file:
                data_remapped = np.array(data)
                data_remapped[np.isnan(data_remapped)] = np.inf
                new_group = file.create_group(f"/attr/property/{attr_name}")
                new_group.attrs["name"] = attr_name
                new_group.attrs["type"] = "numeric"
                new_group.attrs["unit"] = "none"

                static_group = new_group.create_group("static")
                static_group.attrs["DIMENSION_LABELS"] = ["J", "I", "K"]
                static_group.attrs["extents"] = data_remapped.shape
                static_group.attrs["max"] = np.nanmax(data.values)
                static_group.attrs["min"] = np.nanmin(data.values)
                static_group.attrs["null_count"] = np.sum(np.isinf(data_remapped))
                static_group.attrs["null_value"] = 255

                static_group.create_dataset("values", data=data_remapped)


class MultigridReader:
    fspath: str
    _h5_attrs: dict[str, Any] | None = None

    def __init__(self, fspath: FsPath) -> None:
        self.fspath = str(fspath)

    @staticmethod
    def h5path_tuple(h5path: str) -> tuple[str, ...]:
        return tuple(h5path.split("/")[1:])

    def h5_attrs(self) -> dict[str, Any]:
        if self._h5_attrs is None:
            self._h5_attrs = {
                k: {**attributes_manager}
                for k, attributes_manager in h5.attrs_dict(self.fspath).items()
            }
        return self._h5_attrs

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.fspath})"

    def _groups_at(self, h5path: str) -> list[str]:
        with h5py.File(self.fspath, "r") as h5file:
            attr_group = h5file.get(h5path)
            groups = list(attr_group.keys())
        return list(groups)

    def read_space(self) -> PyMultigridSpace:
        attrs_dict = self.h5_attrs()
        spatial = attrs_dict["/spatial"]
        ijk2xyz = spatial["ijk_to_xyz"]
        assert ijk2xyz.shape == (12,), f"Invalid ijk_to_xyz shape {ijk2xyz.shape}"
        space = PyMultigridSpace(**spatial)
        return space

    def read_axis_labeling(self) -> list[AxisLabel]:
        attrs = self.h5_attrs()
        axis_labeling = []
        with h5py.File(self.fspath, "r") as h5file:
            for ax in ["i", "j"]:
                if f"/attr/geometry/{ax}" in attrs:
                    axis = ax
                    name = attrs[f"/attr/geometry/{ax}"]["name"]
                    if not isinstance(h5file, h5py.Dataset):
                        raise ValueError("h5file is not a dataset")
                    lut_ds = h5file.get(f"/attr/geometry/{ax}/lut")
                    if lut_ds is not None and isinstance(lut_ds, h5py.Dataset):
                        lut_data = lut_ds[()]
                        step = lut_data[0] if len(lut_data) > 0 else 1.0
                        start = lut_data[1] if len(lut_data) > 1 else 0.0
                    else:
                        step = 1.0
                        start = 0.0
                    axis_labeling.append(
                        AxisLabel.model_validate({
                            "axis": ord(axis.upper()),
                            "name": name,
                            "step": step,
                            "start": start,
                        })
                    )
        return axis_labeling

    def read_attributes(self) -> list[Attribute]:
        attrs = self.h5_attrs()
        property_attributes = {
            k: v for k, v in attrs.items() if k.startswith("/attr/property/")
        }
        property_roots: set[str] = {
            k for k in property_attributes.keys() if len(k[1:].split("/")) == 3
        }
        property_attributes_roots = {
            k: v for k, v in property_attributes.items() if k in property_roots
        }
        # non-temporal property roots are those that have a static attribute
        # and temporal property roots are those that do not and will have timestamp
        # hdf5 groups
        non_temporal_property_roots: set[str] = {
            k for k in property_roots if f"{k}/static" in attrs
        }
        temporal_property_roots = property_roots - non_temporal_property_roots

        temporal_attrs_with_one_time_step: set[str] = set()

        property_time_steps: dict[str, list[str]] = {}

        for temporal_property_root in temporal_property_roots:
            ts_groups = self._groups_at(temporal_property_root)
            if len(ts_groups) == 1:
                temporal_attrs_with_one_time_step.add(temporal_property_root)
            else:
                property_time_steps[temporal_property_root] = list(ts_groups)

        for _k, v in property_attributes.items():
            # TODO: remove once we know precision is always: 'ms' | 'second' | 'day'
            if "precision" in v:
                assert v["precision"] in ["ms", "second", "day", "minute"], v[
                    "precision"
                ]

        return [
            Attribute.from_hdf5_dictionary({
                **v,
                "key": k,
                "temporal": k in temporal_property_roots
                and k not in temporal_attrs_with_one_time_step,
                "time_steps": property_time_steps.get(k, set()),
            })
            for k, v in property_attributes_roots.items()
        ]

    def _try_meta_general_last_revision(self) -> str | None:
        attrs_dict = self.h5_attrs()
        try:
            return attrs_dict["/meta/general/last_revision"]["date"]
        except KeyError:
            pass
        return None


class Pym2grdReader(MultigridReader):
    def read_header(self) -> Pym2grdHeader:
        """Read Pym2grdHeader"""
        attrs_dict = self.h5_attrs()
        attributes = self.read_attributes()
        space = self.read_space()
        cs_xy_data = attrs_dict["/cs/xy"]
        cs_xy = CsXy(**cs_xy_data)
        cs_z_data = attrs_dict["/cs/z"]
        cs_z = CsZ(**cs_z_data)
        meta_general_data = attrs_dict["/meta/general"]
        meta_general = MetaGeneral(**meta_general_data)
        timestep_properties, time_steps = match_datetimes(attrs_dict)
        version = attrs_dict["/meta/m2grd"]["version"]
        return Pym2grdHeader(
            alias="",  # TODO: check where alias is read
            type="multi-attribute 2D grid",
            space=space,
            coordinate_system_id=cs_xy.id,
            z_datum_above_msl=cs_z.datum,
            version=version,
            attributes=attributes,
            history=meta_general.history.splitlines(keepends=False),
            desc=meta_general.description,
            time_steps=time_steps,
            timestep_properties=timestep_properties,
            xyunits=cs_xy.unit,
            zunits=cs_z.unit,
        )


class Pym3grdReader(MultigridReader):
    def read_header(self) -> Pym3grdHeader:
        """Read Pym2grdHeader"""
        attrs_dict = self.h5_attrs()
        axis_labeling = self.read_axis_labeling()
        space = self.read_space()
        attributes = self.read_attributes()
        cs_xy_data = attrs_dict["/cs/xy"]
        cs_xy = CsXy(**cs_xy_data)
        cs_z_data = attrs_dict["/cs/z"]
        cs_z = CsZ(**cs_z_data)
        meta_general_data = attrs_dict["/meta/general"]
        meta_general = MetaGeneral(**meta_general_data)
        _date = self._try_meta_general_last_revision()

        version = attrs_dict["/meta/m3grd"]["version"]
        _time_steps: set[str] = set()
        for attr in attributes:
            if attr.temporal and attr.time_steps:
                _time_steps.update(attr.time_steps)
        return Pym3grdHeader(
            alias="",  # TODO: check where alias is read
            type="multi-attribute 3D grid",
            axis_labeling=axis_labeling,
            space=space,
            coordinate_system_id=cs_xy.id,
            z_datum_above_msl=cs_z.datum,
            version=version,
            date=_date,
            attributes=attributes,
            history=meta_general.history.splitlines(keepends=False),
            desc=meta_general.description,
            time_steps=list(_time_steps),
            timestep_properties={el.name for el in attributes if el.temporal},
            xyunits=strip_downward_suffix(cs_xy.unit),
            zunits=units_string(cs_z.unit, downward=space.is_downward()),
        )
