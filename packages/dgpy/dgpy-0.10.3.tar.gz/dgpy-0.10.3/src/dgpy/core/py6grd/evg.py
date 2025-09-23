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
"""Earth vision grid [tokens] ~ evg"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from functools import lru_cache
from typing import Final, TypedDict, TypeVar


class InvalidEvgTokenError(Exception):
    """Invalid Evg token error"""

    token: int

    def __init__(self, token: int) -> None:
        """Initialize with token"""
        super().__init__(f"Invalid Evg token: {token}")

    def __str__(self) -> str:
        return f"Invalid Evg token: {self.token} - {super().__str__()}"


class UnknownEvgTokenError(Exception):
    """Unknown Evg token error"""

    token: str | int

    def __init__(self, token: str | int) -> None:
        """Initialize with token"""
        self.token = token
        super().__init__(f"Invalid Evg token: {token}")

    def __str__(self) -> str:
        return f"Invalid Evg token: {self.token} - {super().__str__()}"


class EvgTokenDict1(TypedDict):
    dgpy_attr: str
    dtype_str: str
    fmtstr: str
    token_name: str


GRD_TOKENS: dict[int, EvgTokenDict1] = {
    2: {
        "dgpy_attr": "version",
        "dtype_str": "int",
        "fmtstr": "I",
        "token_name": "Evg_version",
    },
    3: {
        "dgpy_attr": "xmin",
        "dtype_str": "double",
        "fmtstr": "d",
        "token_name": "Evg_xmin",
    },
    4: {
        "dgpy_attr": "xmax",
        "dtype_str": "double",
        "fmtstr": "d",
        "token_name": "Evg_xmax",
    },
    5: {
        "dgpy_attr": "ymin",
        "dtype_str": "double",
        "fmtstr": "d",
        "token_name": "Evg_ymin",
    },
    6: {
        "dgpy_attr": "ymax",
        "dtype_str": "double",
        "fmtstr": "d",
        "token_name": "Evg_ymax",
    },
    7: {
        "dgpy_attr": "zmin",
        "dtype_str": "double",
        "fmtstr": "d",
        "token_name": "Evg_zmin",
    },
    8: {
        "dgpy_attr": "zmax",
        "dtype_str": "double",
        "fmtstr": "d",
        "token_name": "Evg_zmax",
    },
    9: {
        "dgpy_attr": "xcol",
        "dtype_str": "int",
        "fmtstr": "I",
        "token_name": "Evg_xcol",
    },
    10: {
        "dgpy_attr": "yrow",
        "dtype_str": "int",
        "fmtstr": "I",
        "token_name": "Evg_yrow",
    },
    11: {
        "dgpy_attr": "zlev",
        "dtype_str": "int",
        "fmtstr": "I",
        "token_name": "Evg_zlev",
    },
    12: {
        "dgpy_attr": "dat",
        "dtype_str": "char",
        "fmtstr": "s",
        "token_name": "Evg_dat",
    },
    13: {
        "dgpy_attr": "field",
        "dtype_str": "char",
        "fmtstr": "s",
        "token_name": "Evg_field",
    },
    14: {
        "dgpy_attr": "vfault",
        "dtype_str": "char",
        "fmtstr": "s",
        "token_name": "Evg_vfault",
    },
    15: {
        "dgpy_attr": "nvfault",
        "dtype_str": "char",
        "fmtstr": "s",
        "token_name": "Evg_nvfault",
    },
    16: {
        "dgpy_attr": "thr",
        "dtype_str": "char",
        "fmtstr": "s",
        "token_name": "Evg_thr",
    },
    17: {
        "dgpy_attr": "projection",
        "dtype_str": "int",
        "fmtstr": "i",
        "token_name": "Evg_projection",
    },
    18: {
        "dgpy_attr": "zone",
        "dtype_str": "int",
        "fmtstr": "I",
        "token_name": "Evg_zone",
    },
    19: {
        "dgpy_attr": "xyunits",
        "dtype_str": "int",
        "fmtstr": "I",
        "token_name": "Evg_xyunits",
    },
    20: {
        "dgpy_attr": "proj_parms",
        "dtype_str": "double",
        "fmtstr": "d",
        "token_name": "Evg_projParms",
    },
    21: {
        "dgpy_attr": "zunits",
        "dtype_str": "int",
        "fmtstr": "i",
        "token_name": "Evg_zunits",
    },
    22: {
        "dgpy_attr": "punits",
        "dtype_str": "int",
        "fmtstr": "i",
        "token_name": "Evg_punits",
    },
    23: {
        "dgpy_attr": "desc",
        "dtype_str": "char",
        "fmtstr": "s",
        "token_name": "Evg_desc",
    },
    24: {
        "dgpy_attr": "history",
        "dtype_str": "char",
        "fmtstr": "s",
        "token_name": "Evg_history",
    },
    25: {
        "dgpy_attr": "geometry",
        "dtype_str": "int",
        "fmtstr": "B",
        "token_name": "Evg_geometry",
    },
    27: {
        "dgpy_attr": "xvec",
        "dtype_str": "double",
        "fmtstr": "d",
        "token_name": "Evg_xvec",
    },
    28: {
        "dgpy_attr": "yvec",
        "dtype_str": "double",
        "fmtstr": "d",
        "token_name": "Evg_yvec",
    },
    29: {
        "dgpy_attr": "zvec",
        "dtype_str": "double",
        "fmtstr": "d",
        "token_name": "Evg_zvec",
    },
    30: {
        "dgpy_attr": "values_32",  # was 'values'
        "dtype_str": "float",
        "fmtstr": "f",
        "token_name": "Evg_values",
    },
    32: {
        "dgpy_attr": "z_influence",
        "dtype_str": "double",
        "fmtstr": "d",
        "token_name": "Evg_zInfluence",
    },
    34: {
        "dgpy_attr": "slice_plane",
        "dtype_str": "int",
        "fmtstr": "I",
        "token_name": "Evg_slicePlane",
    },
    35: {
        "dgpy_attr": "slice_grid",
        "dtype_str": "char",
        "fmtstr": "s",
        "token_name": "Evg_sliceGrid",
    },
    36: {
        "dgpy_attr": "slice_value",
        "dtype_str": "double",
        "fmtstr": "d",
        "token_name": "Evg_sliceValue",
    },
    41: {
        "dgpy_attr": "clip_poly",
        "dtype_str": "char",
        "fmtstr": "s",
        "token_name": "Evg_clipPoly",
    },
    42: {
        "dgpy_attr": "clip_top",
        "dtype_str": "char",
        "fmtstr": "s",
        "token_name": "Evg_clipTop",
    },
    43: {
        "dgpy_attr": "clip_bottom",
        "dtype_str": "char",
        "fmtstr": "s",
        "token_name": "Evg_clipBottom",
    },
    44: {
        "dgpy_attr": "clip_top_expansion",
        "dtype_str": "double",
        "fmtstr": "d",
        "token_name": "Evg_clipTopExpansion",
    },
    45: {
        "dgpy_attr": "clip_bottom_expansion",
        "dtype_str": "double",
        "fmtstr": "d",
        "token_name": "Evg_clipBottomExpansion",
    },
    47: {
        "dgpy_attr": "pclip",
        "dtype_str": "float",
        "fmtstr": "f",
        "token_name": "Evg_pclip",
    },
    52: {
        "dgpy_attr": "xform_type",
        "dtype_str": "int",
        "fmtstr": "i",
        "token_name": "Evg_xformType",
    },
    53: {
        "dgpy_attr": "xform_top",
        "dtype_str": "char*",
        "fmtstr": "s",
        "token_name": "Evg_xformTop",
    },
    54: {
        "dgpy_attr": "xform_bottom",
        "dtype_str": "char*",
        "fmtstr": "s",
        "token_name": "Evg_xformBottom",
    },
    55: {
        "dgpy_attr": "xform_top_shift",
        "dtype_str": "double",
        "fmtstr": "d",
        "token_name": "Evg_xformTopShift",
    },
    56: {
        "dgpy_attr": "xform_bottom_shift",
        "dtype_str": "double",
        "fmtstr": "d",
        "token_name": "Evg_xformBottomShift",
    },
    57: {
        "dgpy_attr": "xform_top_percent",
        "dtype_str": "int",
        "fmtstr": "i",
        "token_name": "Evg_xformTopPercent",
    },
    58: {
        "dgpy_attr": "xform_bottom_percent",
        "dtype_str": "int",
        "fmtstr": "i",
        "token_name": "Evg_xformBottomPercent",
    },
    61: {
        "dgpy_attr": "trend_order",
        "dtype_str": "int",
        "fmtstr": "i",
        "token_name": "Evg_trendOrder",
    },
    62: {
        "dgpy_attr": "trend_coefficients",
        "dtype_str": "int",
        "fmtstr": "i",
        "token_name": "Evg_trendCoefficients",
    },
    63: {
        "dgpy_attr": "bpoly",
        "dtype_str": "char",
        "fmtstr": "s",
        "token_name": "Evg_bpoly",
    },
    64: {
        "dgpy_attr": "xform_bottom_grid",
        "dtype_str": "float",
        "fmtstr": "f",
        "token_name": "Evg_xformBottomGrid",
    },
    65: {
        "dgpy_attr": "xform_z_spacing",
        "dtype_str": "float",
        "fmtstr": "f",
        "token_name": "Evg_xformZSpacing",
    },
    66: {
        "dgpy_attr": "xform_divider",
        "dtype_str": "int",
        "fmtstr": "I",
        "token_name": "Evg_xformDivider",
    },
    67: {
        "dgpy_attr": "xform_x_spacing",
        "dtype_str": "float",
        "fmtstr": "f",
        "token_name": "Evg_xformXSpacing",
    },
    68: {
        "dgpy_attr": "nulls_in_grid",
        "dtype_str": "int",
        "fmtstr": "I",
        "token_name": "Evg_nullsInGrid",
    },
    69: {"dgpy_attr": "vf", "dtype_str": "int", "fmtstr": "I", "token_name": "Evg_vf"},
    70: {
        "dgpy_attr": "nvf",
        "dtype_str": "int",
        "fmtstr": "I d d",
        "token_name": "Evg_nvf",
    },
    71: {
        "dgpy_attr": "trend_offsets",
        "dtype_str": "int",
        "fmtstr": "i",
        "token_name": "Evg_trendOffsets",
    },
    72: {
        "dgpy_attr": "rotation",
        "dtype_str": "float",
        "fmtstr": "f",
        "token_name": "Evg_rotation",
    },
    73: {
        "dgpy_attr": "space",
        "dtype_str": "int",
        "fmtstr": "IIdddddIII",  # fmt string was: "IIddddIII"
        "token_name": "Evg_space",
    },
    74: {
        "dgpy_attr": "clamp",
        "dtype_str": "double",
        "fmtstr": "f",
        "token_name": "Evg_clamp",
    },
    75: {
        "dgpy_attr": "property_node",
        "dtype_str": "int",
        "fmtstr": "i",
        "token_name": "Evg_property_node",
    },
    76: {
        "dgpy_attr": "node_range",
        "dtype_str": "double,double",
        "fmtstr": "f",
        "token_name": "Evg_nodeRange",
    },
    78: {
        "dgpy_attr": "data_order",
        "dtype_str": "enum",
        "fmtstr": "I",
        "token_name": "Evg_dataOrder",
    },
    81: {
        "dgpy_attr": "bit_factor",
        "dtype_str": "double",
        "fmtstr": "f",
        "token_name": "Evg_bitFactor",
    },
    82: {
        "dgpy_attr": "bit_shift",
        "dtype_str": "double",
        "fmtstr": "f",
        "token_name": "Evg_bitShift",
    },
    83: {
        "dgpy_attr": "values_8",  # was "8bit_values"
        "dtype_str": "double",
        "fmtstr": "B",
        "token_name": "Evg_8bitValues",
    },
    84: {
        "dgpy_attr": "date",
        "dtype_str": "char*",
        "fmtstr": "s",
        "token_name": "Evg_date",
    },
    87: {
        "dgpy_attr": "seismic_line_and_trace_labels",
        "dtype_str": "int",
        "fmtstr": "I",  # Was "IIIII"
        "token_name": "Evg_seismicLineAndTraceLabels",
    },
    88: {
        "dgpy_attr": "values_16",
        "dtype_str": "double",
        "fmtstr": "H",  # Was "d"
        "token_name": "Evg_16bitValues",
    },
    90: {
        "dgpy_attr": "coordinate_system_id",
        "dtype_str": "char*",
        "fmtstr": "s",
        "token_name": "Evg_coordinateSystemId",
    },
    91: {
        "dgpy_attr": "coordinate_system_name",
        "dtype_str": "char*",
        "fmtstr": "s",
        "token_name": "Evg_coordinateSystemName",
    },
    92: {
        "dgpy_attr": "64bit_null_count",
        "dtype_str": "int",
        "fmtstr": "I",
        "token_name": "Evg_64bitNullCount",
    },
    93: {
        "dgpy_attr": "end_of_header",
        "dtype_str": "char",
        "fmtstr": "s",
        "token_name": "Evg_endOfHeader",
    },
    94: {
        "dgpy_attr": "punits_string",
        "dtype_str": "char",
        "fmtstr": "s",
        "token_name": "Evg_punitsString",
    },
    95: {
        "dgpy_attr": "alias",
        "dtype_str": "char*",
        "fmtstr": "s",
        "token_name": "Evg_alias",
    },
    96: {
        "dgpy_attr": "padding",
        "dtype_str": "char*",
        "fmtstr": "s",
        "token_name": "Evg_padding",
    },
    100: {
        "dgpy_attr": "RESERVED",
        "dtype_str": "char*",
        "fmtstr": "s",
        "token_name": "RESERVED",
    },
}

EVG_TOKEN_NAME_2_ENUM = {v["token_name"]: k for k, v in GRD_TOKENS.items()}

_TEvgToken = TypeVar("_TEvgToken", bound="EvgToken")


class EvgTokenDict(TypedDict):
    evg: int
    dgpy_attr: str
    dtype_str: str
    fmtstr: str
    token_name: str
    deprecated: bool


@dataclass()
class EvgToken:
    """Evg token info object

    Examples:
        >>> EvgToken(evg=2, dgpy_attr='version', dtype_str='int', fmtstr='I', token_name='Evg_version', deprecated=False)
        EvgToken(evg=2, dgpy_attr='version', dtype_str='int', fmtstr='I', token_name='Evg_version', deprecated=False)
        >>> EvgToken.from_int(2)
        EvgToken(evg=2, dgpy_attr='version', dtype_str='int', fmtstr='I', token_name='Evg_version', deprecated=False)
        >>> str(EvgToken.from_int(2))
        "EvgToken(evg=2, dgpy_attr='version', dtype_str='int', fmtstr='I', token_name='Evg_version', deprecated=False)"

    """

    __slots__ = (
        "deprecated",
        "dgpy_attr",
        "dtype_str",
        "evg",
        "fmtstr",
        "token_name",
    )

    evg: int
    dgpy_attr: str
    dtype_str: str
    fmtstr: str
    token_name: str
    deprecated: bool

    def __init__(
        self,
        *,
        evg: int,
        dgpy_attr: str,
        dtype_str: str,
        fmtstr: str,
        token_name: str,
        deprecated: bool = False,
    ) -> None:
        """Initialize evg token info object

        Args:
            evg (int): Evg token integer value
            dgpy_attr (str): Dgpy attribute name
            dtype_str (str): Data type string
            fmtstr (str): Format string for the token
            token_name (str): Token name
            deprecated (bool, optional): Whether the token is deprecated. Defaults to False.

        """
        self.evg = evg
        self.dgpy_attr = dgpy_attr
        self.dtype_str = dtype_str
        self.fmtstr = fmtstr
        self.token_name = token_name
        self.deprecated = deprecated

    @staticmethod
    def from_int(token: int) -> EvgToken:
        return int2evg(token)

    def enum(self) -> Evg:
        """Return Evg enum"""
        return Evg(self.evg)

    def is_header_token(self) -> bool:
        return not (self.evg == 30 or self.evg == 83 or self.evg == 88)

    def to_dict(self) -> EvgTokenDict:
        return {
            "evg": self.evg,
            "dgpy_attr": self.dgpy_attr,
            "dtype_str": self.dtype_str,
            "fmtstr": self.fmtstr,
            "token_name": self.token_name,
            "deprecated": self.deprecated,
        }

    def __hash__(self) -> int:
        return hash(self.evg)

    def __eq__(self, other: _TEvgToken | int) -> bool:  # type: ignore[override]
        _other_evg = other if isinstance(other, int) else other.evg
        return self.evg == _other_evg

    def __lt__(self, other: _TEvgToken | int) -> bool:
        _other_evg = other if isinstance(other, int) else other.evg
        return self.evg < _other_evg

    def __gt__(self, other: _TEvgToken | int) -> bool:
        _other_evg = other if isinstance(other, int) else other.evg
        return self.evg > _other_evg

    @staticmethod
    def _deprecated_tokens() -> tuple[int, ...]:
        return (3, 4, 5, 6, 7, 8, 17, 18, 19, 20, 21)

    @staticmethod
    def _grid_values_tokens() -> tuple[int, ...]:
        return (30, 83, 88)


class EvgNodeType(IntEnum):
    """Evg node type enum; default value is 0 (standard)"""

    standard = 0
    slice_data = 1
    seismic = 4
    next_node_type = 6


class Evg(IntEnum):
    """Evg tokens enum"""

    version = 2
    xmin = 3
    xmax = 4
    ymin = 5
    ymax = 6
    zmin = 7
    zmax = 8
    xcol = 9
    yrow = 10
    zlev = 11
    dat = 12
    field = 13
    vfault = 14
    nvfault = 15
    thr = 16
    projection = 17
    zone = 18
    xyunits = 19
    projParms = 20
    zunits = 21
    punits = 22
    desc = 23
    history = 24
    geometry = 25
    xvec = 27
    yvec = 28
    zvec = 29
    values = 30
    zInfluence = 32
    slicePlane = 34
    sliceGrid = 35
    sliceValue = 36
    clipPoly = 41
    clipTop = 42
    clipBottom = 43
    clipTopExpansion = 44
    clipBottomExpansion = 45
    pclip = 47
    xformType = 52
    xformTop = 53
    xformBottom = 54
    xformTopShift = 55
    xformBottomShift = 56
    xformTopPercent = 57
    xformBottomPercent = 58
    trendOrder = 61
    trendCoefficients = 62
    bpoly = 63
    xformBottomGrid = 64
    xformZSpacing = 65
    xformDivider = 66
    xformXSpacing = 67
    nullsInGrid = 68
    vf = 69
    nvf = 70
    trendOffsets = 71
    rotation = 72
    space = 73
    clamp = 74
    property_node = 75
    nodeRange = 76
    dataOrder = 78
    bitFactor = 81
    bitShift = 82
    _8bitValues = 83
    values_8bit = 83
    date = 84
    seismicLineAndTraceLabels = 87
    _16bitValues = 88
    values_16bit = 88
    coordinateSystemId = 90
    coordinateSystemName = 91
    _64bitNullCount = 92
    endOfHeader = 93
    punitsString = 94
    alias = 95
    padding = 96
    RESERVED = 100

    # =========================================================================
    # snake_case
    # =========================================================================
    proj_parms = 20
    z_influence = 32
    slice_plane = 34
    slice_grid = 35
    slice_value = 36
    clip_poly = 41
    clip_top = 42
    clip_bottom = 43
    clip_top_expansion = 44
    clip_bottom_expansion = 45
    xform_type = 52
    xform_top = 53
    xform_bottom = 54
    xform_top_shift = 55
    xform_bottom_shift = 56
    xform_top_percent = 57
    xform_bottom_percent = 58
    trend_order = 61
    trend_coefficients = 62
    xform_bottom_grid = 64
    xform_z_spacing = 65
    xform_divider = 66
    xform_x_spacing = 67
    nulls_in_grid = 68
    trend_offsets = 71
    node_range = 76
    data_order = 78
    bit_factor = 81
    bit_shift = 82
    _8bit_values = 83
    seismic_line_and_trace_labels = 87
    _16bit_values = 88
    coordinate_system_id = 90
    coordinate_system_name = 91
    _64bit_null_count = 92
    end_of_header = 93
    punits_string = 94

    @staticmethod
    def token_to_token_name(token: int) -> str:
        """Return token name from token int"""
        return str(GRD_TOKENS[token]["token_name"])

    @staticmethod
    def evg_token(token: int) -> EvgToken:
        return EvgToken.from_int(token)

    @staticmethod
    def token_is_values(token: int) -> bool:
        """Return True if token represents grid values"""
        return token in {30, 83, 88}


@lru_cache(maxsize=256)
def int2evg(token: int) -> EvgToken:
    """Return EvgTokenInfo object from a token int"""
    # if not between 0 and 255, raise error
    if not 0 <= token <= 255:
        raise InvalidEvgTokenError(token)
    if token not in _EVG_TOKENS:
        raise UnknownEvgTokenError(token)
    return _EVG_TOKENS[token]


@lru_cache(maxsize=256)
def evg_str2int(token_name: str) -> int:
    """Return the Evg token int from a `Evg_XXX` style token_name string"""
    _t = _EVG_TOKEN_NAME_2_ENUM.get(token_name, None)
    if _t is None:
        raise UnknownEvgTokenError(token_name)
    return _t


_EVG_TOKENS: Final[dict[int, EvgToken]] = {
    2: EvgToken(
        evg=2,
        dgpy_attr="version",
        dtype_str="int",
        fmtstr="I",
        token_name="Evg_version",
        deprecated=False,
    ),
    3: EvgToken(
        evg=3,
        dgpy_attr="xmin",
        dtype_str="double",
        fmtstr="d",
        token_name="Evg_xmin",
        deprecated=True,
    ),
    4: EvgToken(
        evg=4,
        dgpy_attr="xmax",
        dtype_str="double",
        fmtstr="d",
        token_name="Evg_xmax",
        deprecated=True,
    ),
    5: EvgToken(
        evg=5,
        dgpy_attr="ymin",
        dtype_str="double",
        fmtstr="d",
        token_name="Evg_ymin",
        deprecated=True,
    ),
    6: EvgToken(
        evg=6,
        dgpy_attr="ymax",
        dtype_str="double",
        fmtstr="d",
        token_name="Evg_ymax",
        deprecated=True,
    ),
    7: EvgToken(
        evg=7,
        dgpy_attr="zmin",
        dtype_str="double",
        fmtstr="d",
        token_name="Evg_zmin",
        deprecated=True,
    ),
    8: EvgToken(
        evg=8,
        dgpy_attr="zmax",
        dtype_str="double",
        fmtstr="d",
        token_name="Evg_zmax",
        deprecated=True,
    ),
    9: EvgToken(
        evg=9,
        dgpy_attr="xcol",
        dtype_str="int",
        fmtstr="I",
        token_name="Evg_xcol",
        deprecated=False,
    ),
    10: EvgToken(
        evg=10,
        dgpy_attr="yrow",
        dtype_str="int",
        fmtstr="I",
        token_name="Evg_yrow",
        deprecated=False,
    ),
    11: EvgToken(
        evg=11,
        dgpy_attr="zlev",
        dtype_str="int",
        fmtstr="I",
        token_name="Evg_zlev",
        deprecated=False,
    ),
    12: EvgToken(
        evg=12,
        dgpy_attr="dat",
        dtype_str="char",
        fmtstr="s",
        token_name="Evg_dat",
        deprecated=False,
    ),
    13: EvgToken(
        evg=13,
        dgpy_attr="field",
        dtype_str="char",
        fmtstr="s",
        token_name="Evg_field",
        deprecated=False,
    ),
    14: EvgToken(
        evg=14,
        dgpy_attr="vfault",
        dtype_str="char",
        fmtstr="s",
        token_name="Evg_vfault",
        deprecated=False,
    ),
    15: EvgToken(
        evg=15,
        dgpy_attr="nvfault",
        dtype_str="char",
        fmtstr="s",
        token_name="Evg_nvfault",
        deprecated=False,
    ),
    16: EvgToken(
        evg=16,
        dgpy_attr="thr",
        dtype_str="char",
        fmtstr="s",
        token_name="Evg_thr",
        deprecated=False,
    ),
    17: EvgToken(
        evg=17,
        dgpy_attr="projection",
        dtype_str="int",
        fmtstr="i",
        token_name="Evg_projection",
        deprecated=True,
    ),
    18: EvgToken(
        evg=18,
        dgpy_attr="zone",
        dtype_str="int",
        fmtstr="I",
        token_name="Evg_zone",
        deprecated=True,
    ),
    19: EvgToken(
        evg=19,
        dgpy_attr="xyunits",
        dtype_str="int",
        fmtstr="I",
        token_name="Evg_xyunits",
        deprecated=True,
    ),
    20: EvgToken(
        evg=20,
        dgpy_attr="proj_parms",
        dtype_str="double",
        fmtstr="d",
        token_name="Evg_projParms",
        deprecated=True,
    ),
    21: EvgToken(
        evg=21,
        dgpy_attr="zunits",
        dtype_str="int",
        fmtstr="i",
        token_name="Evg_zunits",
        deprecated=True,
    ),
    22: EvgToken(
        evg=22,
        dgpy_attr="punits",
        dtype_str="int",
        fmtstr="i",
        token_name="Evg_punits",
        deprecated=False,
    ),
    23: EvgToken(
        evg=23,
        dgpy_attr="desc",
        dtype_str="char",
        fmtstr="s",
        token_name="Evg_desc",
        deprecated=False,
    ),
    24: EvgToken(
        evg=24,
        dgpy_attr="history",
        dtype_str="char",
        fmtstr="s",
        token_name="Evg_history",
        deprecated=False,
    ),
    25: EvgToken(
        evg=25,
        dgpy_attr="geometry",
        dtype_str="int",
        fmtstr="B",
        token_name="Evg_geometry",
        deprecated=False,
    ),
    27: EvgToken(
        evg=27,
        dgpy_attr="xvec",
        dtype_str="double",
        fmtstr="d",
        token_name="Evg_xvec",
        deprecated=False,
    ),
    28: EvgToken(
        evg=28,
        dgpy_attr="yvec",
        dtype_str="double",
        fmtstr="d",
        token_name="Evg_yvec",
        deprecated=False,
    ),
    29: EvgToken(
        evg=29,
        dgpy_attr="zvec",
        dtype_str="double",
        fmtstr="d",
        token_name="Evg_zvec",
        deprecated=False,
    ),
    30: EvgToken(
        evg=30,
        dgpy_attr="values_32",
        dtype_str="float",
        fmtstr="f",
        token_name="Evg_values",
        deprecated=False,
    ),
    32: EvgToken(
        evg=32,
        dgpy_attr="z_influence",
        dtype_str="double",
        fmtstr="d",
        token_name="Evg_zInfluence",
        deprecated=False,
    ),
    34: EvgToken(
        evg=34,
        dgpy_attr="slice_plane",
        dtype_str="int",
        fmtstr="I",
        token_name="Evg_slicePlane",
        deprecated=False,
    ),
    35: EvgToken(
        evg=35,
        dgpy_attr="slice_grid",
        dtype_str="char",
        fmtstr="s",
        token_name="Evg_sliceGrid",
        deprecated=False,
    ),
    36: EvgToken(
        evg=36,
        dgpy_attr="slice_value",
        dtype_str="double",
        fmtstr="d",
        token_name="Evg_sliceValue",
        deprecated=False,
    ),
    41: EvgToken(
        evg=41,
        dgpy_attr="clip_poly",
        dtype_str="char",
        fmtstr="s",
        token_name="Evg_clipPoly",
        deprecated=False,
    ),
    42: EvgToken(
        evg=42,
        dgpy_attr="clip_top",
        dtype_str="char",
        fmtstr="s",
        token_name="Evg_clipTop",
        deprecated=False,
    ),
    43: EvgToken(
        evg=43,
        dgpy_attr="clip_bottom",
        dtype_str="char",
        fmtstr="s",
        token_name="Evg_clipBottom",
        deprecated=False,
    ),
    44: EvgToken(
        evg=44,
        dgpy_attr="clip_top_expansion",
        dtype_str="double",
        fmtstr="d",
        token_name="Evg_clipTopExpansion",
        deprecated=False,
    ),
    45: EvgToken(
        evg=45,
        dgpy_attr="clip_bottom_expansion",
        dtype_str="double",
        fmtstr="d",
        token_name="Evg_clipBottomExpansion",
        deprecated=False,
    ),
    47: EvgToken(
        evg=47,
        dgpy_attr="pclip",
        dtype_str="float",
        fmtstr="f",
        token_name="Evg_pclip",
        deprecated=False,
    ),
    52: EvgToken(
        evg=52,
        dgpy_attr="xform_type",
        dtype_str="int",
        fmtstr="i",
        token_name="Evg_xformType",
        deprecated=False,
    ),
    53: EvgToken(
        evg=53,
        dgpy_attr="xform_top",
        dtype_str="char*",
        fmtstr="s",
        token_name="Evg_xformTop",
        deprecated=False,
    ),
    54: EvgToken(
        evg=54,
        dgpy_attr="xform_bottom",
        dtype_str="char*",
        fmtstr="s",
        token_name="Evg_xformBottom",
        deprecated=False,
    ),
    55: EvgToken(
        evg=55,
        dgpy_attr="xform_top_shift",
        dtype_str="double",
        fmtstr="d",
        token_name="Evg_xformTopShift",
        deprecated=False,
    ),
    56: EvgToken(
        evg=56,
        dgpy_attr="xform_bottom_shift",
        dtype_str="double",
        fmtstr="d",
        token_name="Evg_xformBottomShift",
        deprecated=False,
    ),
    57: EvgToken(
        evg=57,
        dgpy_attr="xform_top_percent",
        dtype_str="int",
        fmtstr="i",
        token_name="Evg_xformTopPercent",
        deprecated=False,
    ),
    58: EvgToken(
        evg=58,
        dgpy_attr="xform_bottom_percent",
        dtype_str="int",
        fmtstr="i",
        token_name="Evg_xformBottomPercent",
        deprecated=False,
    ),
    61: EvgToken(
        evg=61,
        dgpy_attr="trend_order",
        dtype_str="int",
        fmtstr="i",
        token_name="Evg_trendOrder",
        deprecated=False,
    ),
    62: EvgToken(
        evg=62,
        dgpy_attr="trend_coefficients",
        dtype_str="int",
        fmtstr="i",
        token_name="Evg_trendCoefficients",
        deprecated=False,
    ),
    63: EvgToken(
        evg=63,
        dgpy_attr="bpoly",
        dtype_str="char",
        fmtstr="s",
        token_name="Evg_bpoly",
        deprecated=False,
    ),
    64: EvgToken(
        evg=64,
        dgpy_attr="xform_bottom_grid",
        dtype_str="float",
        fmtstr="f",
        token_name="Evg_xformBottomGrid",
        deprecated=False,
    ),
    65: EvgToken(
        evg=65,
        dgpy_attr="xform_z_spacing",
        dtype_str="float",
        fmtstr="f",
        token_name="Evg_xformZSpacing",
        deprecated=False,
    ),
    66: EvgToken(
        evg=66,
        dgpy_attr="xform_divider",
        dtype_str="int",
        fmtstr="I",
        token_name="Evg_xformDivider",
        deprecated=False,
    ),
    67: EvgToken(
        evg=67,
        dgpy_attr="xform_x_spacing",
        dtype_str="float",
        fmtstr="f",
        token_name="Evg_xformXSpacing",
        deprecated=False,
    ),
    68: EvgToken(
        evg=68,
        dgpy_attr="nulls_in_grid",
        dtype_str="int",
        fmtstr="I",
        token_name="Evg_nullsInGrid",
        deprecated=False,
    ),
    69: EvgToken(
        evg=69,
        dgpy_attr="vf",
        dtype_str="int",
        fmtstr="I",
        token_name="Evg_vf",
        deprecated=False,
    ),
    70: EvgToken(
        evg=70,
        dgpy_attr="nvf",
        dtype_str="int",
        fmtstr="I d d",
        token_name="Evg_nvf",
        deprecated=False,
    ),
    71: EvgToken(
        evg=71,
        dgpy_attr="trend_offsets",
        dtype_str="int",
        fmtstr="i",
        token_name="Evg_trendOffsets",
        deprecated=False,
    ),
    72: EvgToken(
        evg=72,
        dgpy_attr="rotation",
        dtype_str="float",
        fmtstr="f",
        token_name="Evg_rotation",
        deprecated=False,
    ),
    73: EvgToken(
        evg=73,
        dgpy_attr="space",
        dtype_str="int",
        fmtstr="IIdddddIII",
        token_name="Evg_space",
        deprecated=False,
    ),
    74: EvgToken(
        evg=74,
        dgpy_attr="clamp",
        dtype_str="double",
        fmtstr="f",
        token_name="Evg_clamp",
        deprecated=False,
    ),
    75: EvgToken(
        evg=75,
        dgpy_attr="property_node",
        dtype_str="int",
        fmtstr="i",
        token_name="Evg_property_node",
        deprecated=False,
    ),
    76: EvgToken(
        evg=76,
        dgpy_attr="node_range",
        dtype_str="double,double",
        fmtstr="f",
        token_name="Evg_nodeRange",
        deprecated=False,
    ),
    78: EvgToken(
        evg=78,
        dgpy_attr="data_order",
        dtype_str="enum",
        fmtstr="I",
        token_name="Evg_dataOrder",
        deprecated=False,
    ),
    81: EvgToken(
        evg=81,
        dgpy_attr="bit_factor",
        dtype_str="double",
        fmtstr="f",
        token_name="Evg_bitFactor",
        deprecated=False,
    ),
    82: EvgToken(
        evg=82,
        dgpy_attr="bit_shift",
        dtype_str="double",
        fmtstr="f",
        token_name="Evg_bitShift",
        deprecated=False,
    ),
    83: EvgToken(
        evg=83,
        dgpy_attr="values_8",
        dtype_str="double",
        fmtstr="B",
        token_name="Evg_8bitValues",
        deprecated=False,
    ),
    84: EvgToken(
        evg=84,
        dgpy_attr="date",
        dtype_str="char*",
        fmtstr="s",
        token_name="Evg_date",
        deprecated=False,
    ),
    87: EvgToken(
        evg=87,
        dgpy_attr="seismic_line_and_trace_labels",
        dtype_str="int",
        fmtstr="I",
        token_name="Evg_seismicLineAndTraceLabels",
        deprecated=False,
    ),
    88: EvgToken(
        evg=88,
        dgpy_attr="values_16",
        dtype_str="double",
        fmtstr="H",
        token_name="Evg_16bitValues",
        deprecated=False,
    ),
    90: EvgToken(
        evg=90,
        dgpy_attr="coordinate_system_id",
        dtype_str="char*",
        fmtstr="s",
        token_name="Evg_coordinateSystemId",
        deprecated=False,
    ),
    91: EvgToken(
        evg=91,
        dgpy_attr="coordinate_system_name",
        dtype_str="char*",
        fmtstr="s",
        token_name="Evg_coordinateSystemName",
        deprecated=False,
    ),
    92: EvgToken(
        evg=92,
        dgpy_attr="64bit_null_count",
        dtype_str="int",
        fmtstr="I",
        token_name="Evg_64bitNullCount",
        deprecated=False,
    ),
    93: EvgToken(
        evg=93,
        dgpy_attr="end_of_header",
        dtype_str="char",
        fmtstr="s",
        token_name="Evg_endOfHeader",
        deprecated=False,
    ),
    94: EvgToken(
        evg=94,
        dgpy_attr="punits_string",
        dtype_str="char",
        fmtstr="s",
        token_name="Evg_punitsString",
        deprecated=False,
    ),
    95: EvgToken(
        evg=95,
        dgpy_attr="alias",
        dtype_str="char*",
        fmtstr="s",
        token_name="Evg_alias",
        deprecated=False,
    ),
    96: EvgToken(
        evg=96,
        dgpy_attr="padding",
        dtype_str="char*",
        fmtstr="s",
        token_name="Evg_padding",
        deprecated=False,
    ),
    100: EvgToken(
        evg=100,
        dgpy_attr="RESERVED",
        dtype_str="char*",
        fmtstr="s",
        token_name="RESERVED",
        deprecated=False,
    ),
}
_EVG_TOKEN_NAME_2_ENUM: Final[dict[str, int]] = {
    v.token_name: k for k, v in _EVG_TOKENS.items()
}
