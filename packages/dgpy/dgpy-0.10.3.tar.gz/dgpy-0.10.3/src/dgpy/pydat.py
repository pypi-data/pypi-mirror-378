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
"""Pydat the dgpy Dataframe!"""

from __future__ import annotations

import csv

from collections import Counter
from io import StringIO
from os import path
from pprint import pformat
from shlex import split as shplit
from typing import TYPE_CHECKING, Any, ClassVar

import numpy as np
import pandas as pd

from jsonbourne import JSON
from pandas import DataFrame, Index, Series
from pydantic import ConfigDict, Field
from shellfish import fs, sh

from dgpy.bdat import unpack_bdata
from dgpy.core.header import parse_ditto_fields, parse_header_lines, parse_header_string
from dgpy.core.py2grd import Py2grd
from dgpy.core.py3grd import Py3grd
from dgpy.core.pyspace import PySpace
from dgpy.datfield import DatField
from dgpy.dgpydantic import DgpyBaseModel
from dgpy.maths import is_multiindex
from dgpy.parsing import head_body_strings, header_lines

if TYPE_CHECKING:
    from collections.abc import Callable

    from dgpy import npt
    from dgpy._types import FsPath

_PD_DF_CONSTRUCTOR_KWARGS = {
    "columns",
    "copy",
    "data",
    "dtype",
    "index",
}


class PydatHeader(DgpyBaseModel):
    """Pydat header object"""

    # REQUIRED FIELDS
    type: str = "unknown"
    xyunits: str = "unknown"
    zunits: str = "unknown"
    alias: str = ""
    filepath: str | None = None
    dfields: list[DatField] = Field(default_factory=list)
    coordinate_system_id: str = ""
    coordinate_system_name: str = ""
    date: str | None = None
    desc: str = ""
    downward: bool = False
    format: str | None = "free"
    use_default_ditto: bool = False
    version: float | int | None = None
    z_datum_above_msl: float | str | None = None
    __required_fields__: ClassVar[tuple[str, ...]] = (
        "alias",
        "attributes",
        "coordinate_system_id",
        "coordinate_system_name",
        "date",
        "desc",
        "downward",
        "fields",
        "filename",
        "fspath",
        "format",
        "type",
        "version",
        "xyunits",
        "z_datum_above_msl",
        "zunits",
    )

    # OPTIONAL FIELDS
    space: PySpace | None = None
    dateformat: str | None = None
    ellipsoid: str | None = None
    line_coloring: str | None = None
    projection: str | None = None
    zone: str | int | None = None
    scale_factor_at_central_meridian: float | None = None
    central_meridian: str | None = None
    latitude_of_origin: str | None = None
    false_easting: float | str | None = None
    false_northing: float | str | None = None
    std_parallel_1: str | None = None
    std_parallel_2: str | None = None
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    @staticmethod
    def _sanitize_data_dict(d: dict[str, Any]) -> dict[str, Any]:
        def _try_make_float(val: Any) -> Any:
            try:
                return float(val)
            except TypeError:
                ...
            except ValueError:
                ...
            if isinstance(val, str):
                return val.strip(" ")
            return val

        if "dfields" in d and any(
            "downward" in f.units and "unknown" not in f.units and f.name == "z"
            for f in d["dfields"]
        ):
            d["downward"] = True
        if d["xyunits"] != "" or d["xyunits"] != "unknown":
            for f in d["dfields"]:
                if f.name in ("x", "y"):
                    f.units = d["xyunits"]
        if "format" in d:
            d["format"] = d["format"].lower()
        return {
            k: _try_make_float(v) for k, v in d.items() if k.strip("\n") not in {"end"}
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any], *, sanitize: bool = False) -> PydatHeader:
        """Create and return PydatHeader from dictionary"""
        try:
            data["dfields"] = [
                DatField(**field_data) for field_data in data.pop("fields")
            ]
        except KeyError:
            ...
        try:
            _ = data.pop("ditto")  # pop ditto fields
        except (KeyError, AttributeError):
            ...
        if sanitize:
            data = PydatHeader._sanitize_data_dict(data)
        return cls(**data)

    def units_ignored(self) -> PydatHeader:
        """Return new PydatHeader with units ignored"""
        return PydatHeader(
            dfields=[
                DatField(
                    name=f.name,
                    ditto=f.ditto,
                    units="ignored",
                )
                for f in self.dfields
            ],
            xyunits="ignored",
            zunits="ignored",
            **self.model_dump(exclude={"dfields", "xyunits", "zunits"}),
        )

    @classmethod
    def from_json(cls, json_string: bytes | str) -> PydatHeader:
        """Create object from JSON string"""
        return cls.from_dict(JSON.loads(json_string))

    def to_string(self) -> str:
        header_template = """# Type: {type}
# Version: {version}
# Format: {format}
{fields}
# Coordinate_System_Id: {coordinate_system_id}
# Coordinate_System_Name: {coordinate_system_name}
# Projection: {projection}
# Zone: {zone}
# Ellipsoid: {ellipsoid}
# Units: {zunits}
# Ditto: {ditto_fields}
# End
"""
        """Return the header as a string"""
        fields = "\n".join([
            (
                f'# Field: {i + 1} "{f.name}" {f.units}'
                if " " in f.name
                else f"# Field: {i + 1} {f.name} {f.units}"
            )
            for i, f in enumerate(self.dfields)
        ])
        return header_template.format(
            type=self.type,
            version=self.version,
            format=self.format,
            fields=fields,
            coordinate_system_id=self.coordinate_system_id,
            coordinate_system_name=self.coordinate_system_name,
            projection=self.projection,
            zone=self.zone,
            ellipsoid=self.ellipsoid,
            zunits=self.zunits,
            ditto_fields=",".join([i.name for i in self.dfields if i.ditto]),
        )

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
            self.model_dump(),
            fmt=fmt,
            pretty=pretty,
            sort_keys=sort_keys,
            append_newline=append_newline,
            default=default,
            **kwargs,
        )


class Pydat(DgpyBaseModel):
    """A dataframe for dgpy"""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    head: PydatHeader = Field(
        default=PydatHeader(), description="PydatHeader metadata container object"
    )
    dataframe: pd.DataFrame = Field(
        ...,
        description="pandas.DataFrame or pandas compatible dataframe object",
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Pydat constructor"""
        dataframe_constructor_kwargs = {
            k: v for k, v in kwargs.items() if k in _PD_DF_CONSTRUCTOR_KWARGS
        }
        non_dataframe_constructor_kwargs = {
            k: v for k, v in kwargs.items() if k not in _PD_DF_CONSTRUCTOR_KWARGS
        }
        _kw = {**non_dataframe_constructor_kwargs}
        if dataframe_constructor_kwargs:
            df = pd.DataFrame(**dataframe_constructor_kwargs)
            _kw["dataframe"] = df
        super().__init__(*args, **_kw)

    def __post_init__(self) -> None:
        """Pydat post init"""
        if self.head.use_default_ditto:
            ...

    @property
    def df(self) -> pd.DataFrame:
        """Return the body/dataframe"""
        return self.dataframe

    @df.setter
    def df(self, dataframe: pd.DataFrame) -> None:
        """Set body (pd.DataFrame) to a different pandas dataframe"""
        self.dataframe = dataframe

    @property
    def body(self) -> pd.DataFrame:
        """Return the body/dataframe"""
        return self.dataframe

    @body.setter
    def body(self, dataframe: pd.DataFrame) -> None:
        """Set body/dataframe (pd.DataFrame) to a different pandas dataframe"""
        self.dataframe = dataframe

    def describe(self, *args: Any, **kwargs: Any) -> DataFrame | Series:
        """Dataframe describe easy access"""
        return self.df.describe(*args, **kwargs)

    def __len__(self) -> int:
        """Return dataframe __len__"""
        return self.dataframe.__len__()

    @property
    def columns(self) -> Index:
        """Return the dataframe columns"""
        return self.dataframe.columns

    def info(self, *args: Any, **kwargs: Any) -> None:
        """Print the info for a Pydat object"""
        sh.echo("__DGINFO__")
        sh.echo(pformat(self.head))
        sh.echo(pformat(self.__dict__))
        sh.echo("\n__PANDAS__")
        sh.echo(self.dataframe.info(*args, **kwargs))

    @classmethod
    def from_string(cls, string: str, fspath: FsPath | None = None) -> Pydat:
        return load_scattered_data_from_string(string, fspath=fspath)

    @classmethod
    def from_stdout(cls, done: sh.Done, fspath: FsPath | None = None) -> Pydat:
        # check stdout is not empty
        if done.stdout == "":
            raise ValueError(f"stdout is empty: {done}")
        return cls.from_string(done.stdout, fspath=fspath or "STDOUT")

    @classmethod
    def from_bdat(cls, filepath: FsPath) -> Pydat:
        """Load Pydat from bdat-fspath

        Args:
            filepath (str): bdat fspath

        Returns:
            Pydat object

        """
        bdat_dataframe = pd.DataFrame(unpack_bdata(filepath))
        header = PydatHeader()
        return cls(**{"head": header, "dataframe": bdat_dataframe})

    @classmethod
    def from_2grd(
        cls, filepath: str, *, multindex: bool = False, name: str | None = None
    ) -> Pydat:
        """Return a Pydat object given a fspath to a 2grd/3grd file

        Args:
            name (str): xarray.DataArray name to use in dataframe conversion
            filepath (str): Grid fspath
            multindex (bool): Return the Pydat/Dataframe as a multindex;
                defaults to False.

        Returns:
            Pydat object

        """
        _pygrid = Py2grd.from_filepath(filepath)
        _pygrid.add_spatial_coordinates()
        _dat_header = PydatHeader.model_validate(_pygrid.head.model_dump())
        _df = _pygrid.dataarray.to_dataframe(name=name or path.split(filepath)[-1])
        if not multindex:
            _df = _df.reset_index(["xcolumns", "yrows"])
        return cls(dataframe=_df, head=_dat_header)

    @classmethod
    def from_3grd(
        cls, filepath: str, *, multindex: bool = False, name: str | None = None
    ) -> Pydat:
        """Return a Pydat object given a fspath to a 2grd/3grd file

        Args:
            filepath (str): Grid fspath
            multindex (bool): Return the Pydat/Dataframe as a multindex;
                defaults to False.

        Returns:
            Pydat object

        """
        _pygrid = Py3grd.from_filepath(filepath)
        _pygrid.add_spatial_coordinates()
        _dat_header = PydatHeader.model_validate(_pygrid.head.model_dump())
        _df = _pygrid.dataarray.to_dataframe(name=name or path.split(filepath)[-1])
        if not multindex:
            try:
                _df = _df.reset_index(["xcolumns", "yrows", "zlevels"])
            except KeyError:
                _df = _df.reset_index(["xcolumns", "yrows"])
        return cls(dataframe=_df, head=_dat_header)

    @classmethod
    def from_free_fmt(cls, filepath: FsPath) -> Pydat:
        """Load data from free format file into Pydat object given a fspath

        Args:
            filepath: fspath to the free format data file

        Returns:
            Pydat Object

        """
        return load_pydat_from_free_fmt_filepath(filepath)

    @classmethod
    def from_fixed_fmt(cls, filepath: FsPath) -> Pydat:
        """Load data from fixed format file into Pydat object given a fspath

        Args:
            filepath: fspath to the fixed format data file

        Returns:
            Pydat Object

        """
        return load_scattered_data_from_fspath(filepath)

    @classmethod
    def from_fspath(cls, fspath: FsPath) -> Pydat:
        """Load and return Pydat object from file-system path"""
        if str(fspath).lower().endswith(".bdat"):
            return cls.from_bdat(filepath=fspath)

        return load_scattered_data_from_fspath(filepath=fspath)

    @classmethod
    def from_filepath(cls, filepath: FsPath) -> Pydat:
        """Load and return Pydat object from filepath; alias for from_fspath"""
        return cls.from_fspath(fspath=filepath)

    @classmethod
    def from_dat(cls, filepath: FsPath) -> Pydat:
        """Load data from dat file into Pydat object given a fspath

        Args:
            filepath: fspath to the dat file

        Returns:
            Pydat Object

        """
        return load_scattered_data_from_fspath(filepath)

    @classmethod
    def from_ann(cls, filepath: FsPath) -> Pydat:
        """Load data from ann file into Pydat object given a fspath

        Args:
            filepath: fspath to the ann file

        Returns:
            Pydat Object

        """
        return load_scattered_data_from_fspath(filepath)

    @classmethod
    def from_pdat(cls, filepath: FsPath) -> Pydat:
        """Load data from pdat file into Pydat object given a fspath

        Args:
            filepath: fspath to the pdat file

        Returns:
            Pydat Object

        """
        return load_scattered_data_from_fspath(filepath)

    @classmethod
    def from_scattered_data(cls, filepath: FsPath) -> Pydat:
        """Load data from scattere-data file into Pydat object given a fspath

        Args:
            filepath: fspath to the scattered data file

        Returns:
            Pydat Object

        """
        return load_scattered_data_from_fspath(filepath)

    @classmethod
    def from_path(cls, filepath: FsPath) -> Pydat:
        """Load data from path file into Pydat object given a fspath

        Args:
            filepath (str): string path to the path file

        Returns:
            Pydat object

        """
        return load_scattered_data_from_fspath(filepath)

    @classmethod
    def from_prod(cls, filepath: FsPath) -> Pydat:
        """Load data from prod file into Pydat object given a fspath

        Args:
            filepath (str): string path to the prod file

        Returns:
            Pydat object

        """
        return load_scattered_data_from_fspath(filepath)

    def to_dataframe(self) -> pd.DataFrame:
        """Convert a dgpy.Pydat object to a pandas.DataFrame object"""
        return self.dataframe

    def to_dict(self, orient: str = "list") -> dict[str, Any]:
        """Return the Pydat object as a dictionary"""
        return {
            "head": self.head.model_dump(),
            "dataframe": self.dataframe.to_dict(orient="list"),
        }

    def to_pdat(self, filepath: FsPath) -> None:
        """Write Pydat to a dat file"""
        # ensure fields in header with columns in dataframe
        fields_header = [i.name.lower() for i in self.head.dfields]
        columns_df = [i.lower() for i in self.dataframe.columns]
        if fields_header != columns_df:
            # Add df-only columns to header, all in the proper order
            head_dfield_dict = {i.name.lower(): i for i in self.head.dfields}
            self.head.dfields = [
                head_dfield_dict.get(
                    col, DatField(name=col, ditto=False, units="unknown")
                )
                for col in columns_df
            ]

        for col in ["x", "y", "z"]:
            if col not in fields_header:
                raise ValueError(
                    f"Pydat is missing {col} field, which is required in a .pdat file. (x,y,z all required)"
                )
        if self.df.empty:
            raise ValueError("Pydat dataframe is empty - not writing to file.")

        header = self.head.to_string()

        self.df = self.df.fillna("")
        with open(filepath, "w") as f:
            f.write(header)
            self.df.to_csv(
                f,
                sep="\t",
                header=False,
                index=False,
                lineterminator="\n",
                quoting=csv.QUOTE_NONNUMERIC,
                quotechar='"',
            )

    def to_dat(self, filepath: FsPath) -> None:
        """Write Pydat to a dat file"""
        # ensure fields in header with columns in dataframe
        fields_header = [i.name.lower() for i in self.head.dfields]
        columns_df = [i.lower() for i in self.dataframe.columns]
        if fields_header != columns_df:
            # Add df-only columns to header, all in the proper order
            head_dfield_dict = {i.name.lower(): i for i in self.head.dfields}
            self.head.dfields = [
                head_dfield_dict.get(
                    col, DatField(name=col, ditto=False, units="unknown")
                )
                for col in columns_df
            ]

        for col in ["x", "y"]:
            if col not in fields_header:
                raise ValueError(
                    f"Pydat is missing {col} field, which is required in a .dat file."
                )
        if self.df.empty:
            raise ValueError("Pydat dataframe is empty - not writing to file.")

        header = self.head.to_string()

        self.df = self.df.fillna("")
        with open(filepath, "w") as f:
            f.write(header)
            self.df.to_csv(
                f,
                sep="\t",
                header=False,
                index=False,
                lineterminator="\n",
                quoting=csv.QUOTE_NONNUMERIC,
                quotechar='"',
            )

    @classmethod
    def from_dict(cls, data: dict[str, Any], *, orient: str = "columns") -> Pydat:
        """Create and return a Pydat from a given dictionary of data"""
        data["dataframe"] = pd.DataFrame.from_dict(data["dataframe"], orient=orient)
        return cls(**data)

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
        orient = kwargs.pop("orient", "columns")
        head_json_str = self.head.to_json(fmt=fmt, pretty=pretty, sort_keys=sort_keys)
        body_json_str = self.dataframe.to_json(
            orient=orient,
            indent=2 if (pretty or fmt) else None,
        )
        parts = ['{"head":', head_json_str, ',"dataframe":', body_json_str, "}"]
        if append_newline:
            parts.append("\n")
        return "".join(parts)

    @classmethod
    def from_json(cls, json_string: bytes | str) -> Pydat:
        """Create and return a Pydat from a JSON string"""
        return cls.from_dict(JSON.loads(json_string))

    @classmethod
    def from_dataframe(cls, dataframe: pd.DataFrame) -> Pydat:
        """Create and return a Pydat from a dataframe"""
        raise NotImplementedError()  # TODO

    def to_numpy(self, dtype: Any = None, *, copy: bool = False) -> npt.NDArray:
        """Return the data as a numpy array"""
        return self.dataframe.to_numpy(dtype=dtype, copy=copy)

    def __str__(self) -> str:
        """Return string representation of Pydat"""
        return "\n".join([
            "__HEADER_(dgpy.PydatHeader)__",
            self.head.__str__().replace("\n", "    \n"),
            "__BODY_(pd.DataFrame)__",
            self.dataframe.__str__().replace("\n", "    \n"),
        ])

    def _repr_html_(self) -> str:
        return "\n".join([
            "<pre>__HEADER_(dgpy.PydatHeader)__",
            self._repr_html_(),
            "__BODY_(pd.DataFrame)__",
            self.dataframe.to_html().replace("\n", "    \n"),
            "</pre>",
        ])

    def is_multiindex(self) -> bool:
        """Return True if pydat dataframe is pandas.MultiIndex; False otherwise"""
        return is_multiindex(self.df)

    def xy_df(self) -> pd.DataFrame:
        _df = self.dataframe.loc[:, ("x", "y")]
        return _df

    def xyz_df(self) -> pd.DataFrame:
        _df = self.dataframe.loc[:, ("x", "y", "z")]
        return _df


def get_sep(line: str, nfields: int) -> str:
    """Guess and return the sep character for a scattered data file"""
    if len(line.split("\t")) == nfields:
        return "\t"
    if len(shplit(line)) == nfields:
        return r"\s+"
    if len(line.split(",")) == nfields:
        return ","
    return "\t"  # default to tab


def get_first_line(string: str) -> str:
    """Return the first line of a string"""
    return string.split("\n", maxsplit=1)[0].rstrip("\n\r")


def load_pydat_from_free_fmt(
    header_string: str, body_string: str, filepath: FsPath
) -> Pydat:
    """Load a free format file into a pydat

    Args:
        header_string (str): header string
        body_string (str): body/data as a string
        filepath: fspath to free-format file

    Returns:
        pydat object with the data from the free format file

    """
    header_data = parse_header_string(header_string, filepath)
    pydat_header = PydatHeader.from_dict(header_data)
    _header_lines = header_string.splitlines(keepends=False)
    format_lines = [
        line
        for line in _header_lines
        if "format" in line.lower() and "fixed" in line.lower()
    ]
    if format_lines:
        raise ValueError(f"format_lines should be empty; format_lines: {format_lines}")

    header_field_lines = (line for line in _header_lines if "# field:" in line.lower())
    ditto_fields = list(parse_ditto_fields(_header_lines))
    fields_shplit = [shplit(e) for e in header_field_lines]
    fields = [e[3].lower() for e in fields_shplit]
    if len(fields) != len(set(fields)):
        counts = Counter(fields)
        duplicate_fields = {e for e, c in counts.items() if c > 1}
        fields = [
            (
                e[3].lower()
                if e[3].lower() not in duplicate_fields
                else "_".join(e[3:]).lower()
            )
            for e in fields_shplit
        ]
        pydat_header.dfields = [
            DatField(**{**dfield.model_dump(), "name": field})
            for dfield, field in zip(pydat_header.dfields, fields, strict=False)
        ]

    if body_string:
        first_line = get_first_line(body_string)
        sep_string = get_sep(first_line, len(fields))
        df = pd.read_csv(StringIO(body_string), names=fields, sep=sep_string)
        _pydat = Pydat(dataframe=df, head=pydat_header)
    else:
        df = pd.DataFrame(columns=fields)
        _pydat = Pydat(dataframe=pd.DataFrame(df, columns=fields), head=pydat_header)
    _pydat.dataframe = _pydat.dataframe.replace("", np.nan)
    for ditto_field in ditto_fields:
        _pydat.dataframe[ditto_field] = _pydat.dataframe[ditto_field].ffill()
    return _pydat


def load_pydat_from_fixed_fmt(
    header_string: str, body_string: str, filepath: FsPath
) -> Pydat:
    """Load data from fixed format file into Pydat object given a fspath

    Args:
        header_string (str): header string
        body_string (str): body/data as a string
        filepath: fspath to the fixed format data file

    Returns:
        Pydat Object

    """
    head_lines = header_string.splitlines(keepends=False)
    header_data = parse_header_string(header_string, filepath=filepath)
    pydat_header = PydatHeader.from_dict(header_data)
    body_buffer = StringIO(body_string)
    header_field_lines = [line for line in head_lines if "field" in line.lower()]
    _fields = [[e.strip().lower() for e in shplit(f)][2:5] for f in header_field_lines]
    _field_names, _field_start, _field_stop = (
        list(el) for el in zip(*_fields, strict=False)
    )
    _field_start = [int(n) - 1 for n in _field_start]
    _field_stop = [int(n) for n in _field_stop]
    df = pd.read_fwf(
        body_buffer,
        colspecs=list(zip(_field_start, _field_stop, strict=False)),
        header=None,
        names=_field_names,
    )
    return Pydat(dataframe=df, head=pydat_header)


def load_pydat_from_free_fmt_filepath(filepath: FsPath) -> Pydat:
    """Load data from scattere-data file into Pydat object given a fspath

    Args:
        filepath: fspath to the scattered data file

    Returns:
        Pydat Object

    """
    _string = fs.read_str(str(filepath))
    _header_string, _body_string = head_body_strings(_string)
    if "fixed" in _header_string:
        return load_pydat_from_fixed_fmt(
            header_string=_header_string,
            body_string=_body_string,
            filepath=str(filepath),
        )
    return load_pydat_from_free_fmt(
        header_string=_header_string, body_string=_body_string, filepath=str(filepath)
    )


def load_scattered_data_from_string(string: str, fspath: FsPath | None = None) -> Pydat:
    _header_string, _body_string = head_body_strings(string)
    if "fixed" in _header_string:
        return load_pydat_from_fixed_fmt(
            header_string=_header_string,
            body_string=_body_string,
            filepath=str(fspath),
        )
    return load_pydat_from_free_fmt(
        header_string=_header_string, body_string=_body_string, filepath=str(fspath)
    )


def load_scattered_data_from_fspath(filepath: FsPath) -> Pydat:
    """Load data from scattere-data file into Pydat object given a fspath

    Args:
        filepath: fspath to the scattered data file

    Returns:
        Pydat Object

    """
    _string = fs.read_str(str(filepath))
    return load_scattered_data_from_string(_string, filepath)


def load_scattered_data_from_filepath(filepath: FsPath) -> Pydat:
    """Load data from scattere-data file into Pydat object given a fspath

    Args:
        filepath: fspath to the scattered data file

    Returns:
        Pydat Object

    """
    return load_scattered_data_from_fspath(filepath)


def lheader(filepath: str) -> PydatHeader:
    """Return the header data as a dictionary given a fspath"""
    _hl = header_lines(filepath)
    return PydatHeader.from_dict(
        {"fspath": filepath, **parse_header_lines(_hl, filepath)}, sanitize=True
    )
