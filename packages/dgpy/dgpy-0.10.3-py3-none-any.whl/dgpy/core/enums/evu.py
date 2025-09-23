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
"""Earth vision units"""

from __future__ import annotations

from enum import Enum
from functools import cache

__all__ = (
    "Evu",
    "evu_enum_to_string",
    "evu_string_to_enum",
    "evu_validate",
)


class Evu(Enum):
    """Earth vision units enum"""

    downward = 0x1000  # AKA 4096

    # For use specifically in extended units i.e. combinations of
    # units that are not represented by any specific ... value.
    extended = -11
    ten = -10
    integer = -3
    nonNumeric = -2
    unknown = -1
    # Returned by stringToUnits if parsing fails else corrected in caller
    error = 0
    # Distance
    inches = 1
    # International feet 1ft = 0.3048m exactly
    feet = 2
    us_survey_feet = 68
    imperial_feet = 84
    indian_feet = 69
    sears_feet = 70
    yards = 3
    indian_yards = 79
    fathoms = 23
    kilofeet = 160
    miles = 4
    nautical_miles = 154
    nanometers = 155
    micrometers = 156
    mm = 5
    cm = 6
    dm = 7
    meters = 8
    km = 9
    # Angle
    degrees_of_arc = 10
    minutes_of_arc = 55
    seconds_of_arc = 11
    radians = 27
    # Time
    # Micro second
    us = 104
    ms = 12
    seconds = 13
    minutes = 62
    hours = 63
    days = 64
    weeks = 65
    months = 66
    years = 67
    # Ratio
    fraction = 56
    percent = 26
    parts_per_thousand = 14
    parts_per_million = 15
    parts_per_billion = 16
    dB = 24
    specific_gravity = 54
    porosity_units = 113
    gas_units = 114
    # Density
    kg_per_m3 = 129
    # Temperature
    degrees_C = 17
    degrees_F = 18
    kelvins = 19
    # Velocity
    feet_per_sec = 20
    feet_per_hour = 105
    meters_per_sec = 21
    km_per_sec = 22
    meters_per_hour = 90
    kft_per_sec = 151
    knots = 157
    miles_per_hour = 158
    km_per_hour = 159
    # Slowness
    ms_per_foot = 43
    sec_per_meter = 148
    min_per_meter = 149
    ms_per_meter = 150
    # Dogleg severity
    degrees_per_30ft = 74
    degrees_per_100ft = 34
    degrees_per_10m = 75
    degrees_per_30m = 33
    degrees_per_100m = 76
    radians_per_meter = 91
    # Concentration
    mg_per_liter = 31
    ug_per_liter = 32
    pounds_per_gallon = 35
    g_per_cc = 36
    # Resistivity
    ohm_meters = 28
    # Conductivity
    millimhos_per_meter = 30
    mhos_per_meter = 42
    # Pressure stress or elastic modulus
    psi = 37
    mPa = 44
    bars = 87
    millibars = 88
    Pa = 89
    psia = 116
    atm = 128
    MPa = 152
    GPa = 153
    # Flow
    cc_per_sec = 45
    m3_per_sec = 112
    km3_per_sec = 46
    liters_per_sec = 110
    gallons_per_hour = 111
    barrels_per_minute = 121
    barrels_per_hour = 122
    barrels_per_day = 123
    ft3_per_sec = 124
    liters_per_minute = 125
    liters_per_hour = 126
    imperial_gallons_per_hour = 127
    # Rotation velocity
    radians_per_sec = 48
    rpm = 40
    degrees_per_sec = 49
    degrees_per_minute = 50
    degrees_per_hour = 51
    per_second = 100
    # Acceleration
    milligals = 29
    microgals = 161
    gravity = 47
    meters_per_sec2 = 77
    feet_per_sec2 = 78
    # Force
    newtons = 52
    deca_newtons = 118
    k_newtons = 106
    pound_force = 146
    klb_force = 147
    # Gamma ray units
    api = 38
    # Torque
    kftlb = 41
    newton_meters = 53
    deca_newton_meters = 119
    kilo_newton_meters = 120
    # Voltage
    volts = 57
    millivolts = 58
    # Magnetic field strength
    nano_teslas = 59
    teslas = 71
    gauss = 72
    microGauss = 73
    # Current
    amperes = 107
    # Volume
    mcf = 60
    barrels = 61
    cubic_feet = 94
    cubic_meters = 96
    bcf = 98
    acre_feet = 99
    liters = 109
    cubic_inches = 130
    cubic_yards = 131
    cubic_Cm = 132
    cubic_Km = 133
    # prev known as Evu_gallons
    gallons_US = 108
    # prev known as Evu_imperialGallons
    gallons_UK = 134
    # Area and permeability
    acres = 92
    hectares = 93
    square_feet = 95
    square_meters = 97
    # permeability really has units of area
    millidarcies = 25
    # Mass
    grams = 101
    kg = 102
    tonnes = 103
    kilotonnes = 115
    klb = 39
    pounds = 135
    # Pressure gradient
    atm_per_foot = 136
    atm_per_meter = 137
    bar_per_meter = 138
    psi_per_K_foot = 139
    # Temperature gradient
    deg_C_per_foot = 140
    deg_F_per_foot = 141
    deg_C_per_meter = 142
    deg_F_per_meter = 143
    kelvins_per_meter = 145
    # API neutron units
    nAPI = 144
    # Viscosity
    centipoise = 117
    # Wellpath error modeling coefficients
    degrees_nano_teslas = 80
    per_meter = 81
    degrees_per_hour2 = 82
    degrees_per_sqrt_hour = 83
    degrees_per_meter = 85
    degrees_per_hour_per_gram = 86
    next_available = 162

    @staticmethod
    def enum2string(num: Evu | int) -> str:
        """Convert units enum to string"""
        return evu_enum_to_string(num)

    @staticmethod
    def string2enum(string: str) -> int:
        """Return the integervalue of the units string"""
        return evu_string_to_enum(string)


@cache
def evu_enum_to_string(n: int) -> str:
    """Convert units enum to string"""
    n = int(n)
    try:
        if n > 4096:
            return f"{Evu(n).name}_downward"
        return str(Evu(n).name)
    except RecursionError:
        return "unknown"
    except ValueError:
        return "unknown"


@cache
def evu_string_to_enum(string: str) -> int:
    """Return the enum integer value for a unit(s) string

    Args:
        string (str): EVU units string

    Returns:
        int: Integer enum value for the unit(s) string

    """
    if string == "unknown":
        return Evu.unknown.value
    if string.endswith("_downward"):
        return evu_string_to_enum(string[:-9]) + 4096
    return Evu.__members__[string].value


@cache
def evu_validate(val: str | int) -> str:
    """Validate evu value and return the units as a string"""
    try:
        return evu_enum_to_string(int(val))
    except TypeError:
        pass
    except ValueError:
        pass
    if "downward" in str(val):
        return f"{evu_validate(str(val)[:-9])}_downward"
    if str(val) in Evu.__members__:
        return str(val)
    raise ValueError(f"Invalid evu value given: {val}")
