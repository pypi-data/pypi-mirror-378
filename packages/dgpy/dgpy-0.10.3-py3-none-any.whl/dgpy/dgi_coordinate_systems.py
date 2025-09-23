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
"""Get coordinate system name from id"""

from __future__ import annotations

from functools import lru_cache
from os import path
from typing import TYPE_CHECKING, Any
from xml.etree import ElementTree as ET

from dgpy.core.config import config
from dgpy.dgpydantic import DgpyBaseModel

if TYPE_CHECKING:
    from collections.abc import Callable
    from xml.etree.ElementTree import Element

DGI_COORDINATE_SYSTEMS_XML = "dgi_coordinate_systems.xml"
DGI_COORDINATE_SYSTEMS_XML_NAMESPACE = "http://www.dgi.com/coordinate_systems"


# TODO
class GeographicCoordinateSystem(DgpyBaseModel):
    name: str
    proj4_def: str
    ellipsoid: str | None = None
    alias: tuple[str] | None = None


# TODO
class ProjectedCoordinateSystem(DgpyBaseModel): ...


class DgiCoordinateSystems:
    @staticmethod
    def filepath() -> str:
        if config().coviz_home_exists():
            return path.join(config().COVIZHOME, "etc", DGI_COORDINATE_SYSTEMS_XML)
        if config().evhome_exists():
            return path.join(config().EVHOME, "etc", DGI_COORDINATE_SYSTEMS_XML)
        raise Exception("COVIZHOME or EVHOME environment variable not set")

    @staticmethod
    def xml_string() -> str:
        with open(DgiCoordinateSystems.filepath()) as f:
            return f.read()

    @staticmethod
    def strip_dgi_coordinate_systems_namespace(string: str) -> str:
        # length of `{http://www.dgi.com/coordinate_systems}` is 39
        return string[39:] if string.startswith("{") else string


def xml_2_geographic_coordinate_system(element: Element) -> GeographicCoordinateSystem:
    d = element2dict(
        element, keyfn=DgiCoordinateSystems.strip_dgi_coordinate_systems_namespace
    )
    alias = d.get("alias", None)

    if isinstance(alias, str):
        d["alias"] = (alias,)
    if isinstance(alias, list):
        d["alias"] = tuple(alias)
    return GeographicCoordinateSystem.model_validate(d)


def attribs_dict(node: ET.Element) -> dict[str, Any] | None:
    if node.attrib:
        return dict(node.items())
    return None


def element2dict(
    node: Element, keyfn: Callable[[str], str] | None = None
) -> dict[str, Any]:
    """Transform xml-ElementTree node tree into a dictionary"""
    result: dict[str, Any] = {}

    for element in node:
        _tag = element.tag
        key = keyfn(_tag) if keyfn else _tag
        if "}" in key:
            # Remove namespace prefix
            key = key.split("}")[1]

        attribs = attribs_dict(element)
        if attribs:
            result["@attribs"] = attribs

        # Process element as tree element if the inner XML contains non-whitespace content
        value = (
            element.text
            if element.text and element.text.strip()
            else element2dict(element, keyfn=keyfn)
        )

        # Check if a node with this name at this depth was already found
        if key in result:
            if not isinstance(result[key], list):
                # We've seen it before, but only once, we need to convert it to a list
                _value = result[key]
                result[key] = [_value, value]
            else:
                # We've seen it at least once, it's already a list, just append the node's inner XML
                result[key].append(value)
        else:
            # First time we've seen it
            result[key] = value

    return result


@lru_cache(maxsize=1)
def coordinate_system_dict() -> dict:
    coordinate_systems_xml_string = DgiCoordinateSystems.filepath()

    tree = ET.parse(coordinate_systems_xml_string)
    root = tree.getroot()
    _coordinate_systems_dict = {}

    # Loop through the coordinate system types and add them to the dictionary
    cs_types = ("projected", "local", "geographic")
    for cs_type in cs_types:
        for cs in root.findall(
            f"ns:{cs_type}_coordinate_systems",
            namespaces={"ns": DGI_COORDINATE_SYSTEMS_XML_NAMESPACE},
        ):
            for i in cs:
                id = i.attrib["uid"]
                for j in i:
                    if j.tag == "{http://www.dgi.com/coordinate_systems}name":
                        _coordinate_systems_dict[id] = j.text

    return _coordinate_systems_dict


@lru_cache(maxsize=128)
def get_coordinate_system_name(cs_id: str) -> str:
    try:
        return coordinate_system_dict()[cs_id]
    except KeyError:
        raise KeyError(f"Coordinate system id {cs_id} not found") from None
