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
"""geojson models/schemas and utils; oh my!

GeoJSON spec: https://datatracker.ietf.org/doc/html/rfc7946

Notes:
    - GeoJSON implementation below enforces the same dimension (2d/3d) for all positions of a geometry

Example GeoJSON FeatureCollection:
    ```
   {
       "type": "FeatureCollection",
       "features": [{
           "type": "Feature",
           "geometry": {
               "type": "Point",
               "coordinates": [102.0, 0.5]
           },
           "properties": {
               "prop0": "value0"
           }
       }, {
           "type": "Feature",
           "geometry": {
               "type": "LineString",
               "coordinates": [
                   [102.0, 0.0],
                   [103.0, 1.0],
                   [104.0, 0.0],
                   [105.0, 1.0]
               ]
           },
           "properties": {
               "prop0": "value0",
               "prop1": 0.0
           }
       }, {
           "type": "Feature",
           "geometry": {
               "type": "Polygon",
               "coordinates": [
                   [
                       [100.0, 0.0],
                       [101.0, 0.0],
                       [101.0, 1.0],
                       [100.0, 1.0],
                       [100.0, 0.0]
                   ]
               ]
           },
           "properties": {
               "prop0": "value0",
                   "this": "that"
               }
           }
       }]
   }
   ```

Pre generics:
    ```python
    class FeatureABC(DgpyBaseModel, abc.ABC):  # type: ignore[misc]
        '''Feature'''

        type: str = Field(GeoJsonType.Feature, const=True)
        geometry: Union[
            Point,
            LineString,
            Polygon,
            MultiPoint,
            MultiLineString,
            MultiPolygon,
        ]

        properties: Optional[dict[str, Any]] = None
        id: Optional[T_FeatureId] = None
        bbox: Optional[BBox] = _bbox_field


        class Config:
            use_enum_values = True


        def __json_interface__(self) -> dict[str, Any]:
            _exclude: set[str] = set()
            if self.bbox is None:
                _exclude.add('bbox')
            if self.id is None:
                _exclude.add('id')
            return self.dict(exclude=_exclude)


        @property
        def __geo_interface__(self) -> dict[str, Any]:
            return self.__json_interface__()


    class PointFeature(FeatureABC):
        '''Point Feature'''

        geometry: Point


    class MultiPointFeature(FeatureABC):
        '''MultiPoint Feature'''

        geometry: MultiPoint


    class LineStringFeature(FeatureABC):
        '''LineString Feature'''

        geometry: LineString


    class MultiLineStringFeature(FeatureABC):
        '''MultiLineString Feature'''

        geometry: MultiLineString


    class PolygonFeature(FeatureABC):
        geometry: Polygon


    class MultiPolygonFeature(FeatureABC):
        geometry: MultiPolygon
    ```
"""

from __future__ import annotations

import abc

from enum import Enum
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Generic,
    Literal,
    TypeAlias,
    TypeVar,
    Union,
    cast,
)

from pydantic import ConfigDict, Field, field_validator
from typing_extensions import TypedDict

from dgpy.dgpydantic import DgpyBaseModel

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

__all__ = (
    "FEATURE_TYPES",
    "GEOMETRY_TYPES",
    "BBox",
    "BBox2D",
    "BBox3D",
    "Feature",
    "FeatureCollection",
    "GeoJsonType",
    "Geometry",
    "GeometryCollection",
    "LineString",
    "LineStringFeature",
    "MultiLineString",
    "MultiLineStringFeature",
    "MultiPoint",
    "MultiPointFeature",
    "MultiPolygon",
    "MultiPolygonFeature",
    "Point",
    "PointFeature",
    "Polygon",
    "Position",
    "Position2D",
    "Position3D",
    "T_FeatureId",
    "polygon",
)

T = TypeVar("T")

T_FeatureId: TypeAlias = str | int
BBox2D = tuple[float, float, float, float]  # 2D bbox
BBox3D = tuple[float, float, float, float, float, float]  # 3D bbox
BBox: TypeAlias = (
    tuple[float, float, float, float] | tuple[float, float, float, float, float, float]
)
_bbox_field = Field(
    default=None,
    description="Bounding box of the feature); "
    'The values of a "bbox" array are "[west, south, east, north]", '
    'not [minx, miny, maxx, maxy]" (see Section 5).',
)

GEOMETRY_TYPES = (
    "Point",
    "MultiPoint",
    "LineString",
    "MultiLineString",
    "Polygon",
    "MultiPolygon",
    "GeometryCollection",
)
FEATURE_TYPES = (
    "Feature",
    "FeatureCollection",
)


class GeoJsonError(ValueError):
    """GeoJSON error"""


class GeoJsonType(str, Enum):
    # geometries
    Point = "Point"
    MultiPoint = "MultiPoint"
    LineString = "LineString"
    MultiLineString = "MultiLineString"
    Polygon = "Polygon"
    MultiPolygon = "MultiPolygon"
    GeometryCollection = "GeometryCollection"

    # features
    Feature = "Feature"
    FeatureCollection = "FeatureCollection"


def position(val: list[float] | tuple[float, ...]) -> Position:
    if not isinstance(val, list | tuple):
        raise GeoJsonError(f"Invalid coord type: {type(val)}")
    if len(val) < 2 or len(val) > 3:
        raise GeoJsonError(f"Invalid coord length: {len(val)}")
    return cast("Position", tuple(val))


Position2D: TypeAlias = tuple[float, float]
Position3D: TypeAlias = tuple[float, float, float]
Coordinate2D: TypeAlias = tuple[float, float]
Coordinate3D: TypeAlias = tuple[float, float, float]
Position: TypeAlias = Position2D | Position3D
Coordinate: TypeAlias = Position
ListPosition2D: TypeAlias = list[Position2D]
ListPosition3D: TypeAlias = list[Position3D]
ListPosition: TypeAlias = list[Position]
Coordinates: TypeAlias = Position
LineStringCoords: TypeAlias = Annotated[list[Position], Field(min_length=2)]
LinearRing: TypeAlias = Annotated[list[Position], Field(min_length=4)]
MultiPointCoords: TypeAlias = list[Position]
MultiLineStringCoords: TypeAlias = list[LineStringCoords]
PolygonCoords: TypeAlias = list[LinearRing]
MultiPolygonCoords: TypeAlias = list[PolygonCoords]


# =============================================================================
# Geometry TypedDicts
# =============================================================================
class PointObj(TypedDict):
    type: Literal["Point"]
    coordinates: Position


class MultiPointObj(TypedDict):
    type: Literal["MultiPoint"]
    coordinates: list[Position]


class LineStringObj(TypedDict):
    type: Literal["LineString"]
    coordinates: list[Position]


class MultiLineStringObj(TypedDict):
    type: Literal["MultiLineString"]
    coordinates: list[list[Position]]


class PolygonObj(TypedDict):
    type: Literal["Polygon"]
    coordinates: list[list[Position]]


class MultiPolygonObj(TypedDict):
    type: Literal["MultiPolygon"]
    coordinates: list[list[list[Position]]]


class GeometryCollectionObj(TypedDict):
    type: Literal["GeometryCollection"]
    geometries: list[
        PointObj
        | MultiPointObj
        | LineStringObj
        | MultiLineStringObj
        | PolygonObj
        | MultiPolygonObj
    ]


class FeatureObj(TypedDict):
    type: Literal["Feature"]
    geometry: (
        PointObj
        | MultiPointObj
        | LineStringObj
        | MultiLineStringObj
        | PolygonObj
        | MultiPolygonObj
        | GeometryCollectionObj
    )
    properties: dict[str, Any]


class FeatureCollectionObj(TypedDict):
    type: Literal["FeatureCollection"]
    features: list[FeatureObj]


# =============================================================================
# pydantic geojson models
# =============================================================================


class _GeoJsonABC(DgpyBaseModel, abc.ABC):
    """Base class for geometry models

    TODO: add [to_]feature support

    def feature(
        self,
        properties: dict[str, Any] = None,
        bbox: BBox = None,
        id: T_FeatureId = None,
    ) -> Feature:
        raise NotImplementedError

    """

    type: str
    bbox: BBox | None = _bbox_field

    model_config = ConfigDict(
        extra="ignore",
    )

    @property
    def __geo_interface__(self) -> dict[str, Any]:
        raise NotImplementedError

    @property
    def has_z(self) -> bool:
        raise NotImplementedError


class _GeoJsonGeometryABC(_GeoJsonABC, abc.ABC):
    @property
    def __geo_interface__(self) -> dict[str, Any]:
        if self.bbox is None:
            return self.model_dump(exclude={"bbox"})
        return self.model_dump()


class Point(_GeoJsonGeometryABC):
    """GeoJSON-Point pydantic model"""

    type: Literal["Point"] = "Point"
    coordinates: Position

    @property
    def has_z(self) -> bool:
        return len(self.coordinates) == 3


class MultiPoint(_GeoJsonGeometryABC):
    """GeoJSON-MultiPoint pydantic model"""

    type: Literal["MultiPoint"]
    coordinates: ListPosition

    @property
    def has_z(self) -> bool:
        return any(len(c) == 3 for c in self.coordinates)


class LineString(_GeoJsonGeometryABC):
    """GeoJSON-LineString pydantic model"""

    type: Literal["LineString"] = "LineString"
    coordinates: ListPosition = Field(..., min_length=2)

    @property
    def has_z(self) -> bool:
        return any(len(c) == 3 for c in self.coordinates)


class MultiLineString(_GeoJsonGeometryABC):
    """GeoJSON-MultiLineString pydantic model"""

    type: Literal["MultiLineString"] = "MultiLineString"
    coordinates: list[LineStringCoords]

    @property
    def has_z(self) -> bool:
        return any(any(len(c) == 3 for c in line) for line in self.coordinates)

    @field_validator("coordinates")
    @classmethod
    def check_coordinates(cls, c: list[list[Position]]) -> list[list[Position]]:
        """Validate that Polygon coordinates pass the GeoJSON spec"""
        return [[position(coord) for coord in ring] for ring in c]


def validate_polygon_coordinates(polygon: list[list[Position]]) -> list[list[Position]]:
    if any(len(ring) < 4 for ring in polygon):
        raise ValueError("All linear rings must have four or more coordinates")
    if any(ring[-1] != ring[0] for ring in polygon):
        raise ValueError("All linear rings have the same start and end coordinates")
    return polygon


class Polygon(_GeoJsonGeometryABC):
    """GeoJSON-Polygon pydantic model"""

    type: Literal["Polygon"] = "Polygon"
    coordinates: list[LinearRing]

    @field_validator("coordinates")
    @classmethod
    def check_coordinates(cls, polygon: list[list[Position]]) -> list[list[Position]]:
        """Validate that Polygon coordinates pass the GeoJSON spec"""
        if len(polygon) == 0:
            return polygon
        validate_polygon_coordinates(polygon)
        return [[position(coord) for coord in ring] for ring in polygon]

    @property
    def exterior(self) -> ListPosition | None:
        """Return the exterior ring of the polygon"""
        return self.coordinates[0] if self.coordinates else None

    @property
    def interiors(self) -> Iterator[LinearRing]:
        """Interiors (Holes) of the polygon."""
        yield from (
            interior for interior in self.coordinates[1:] if len(self.coordinates) > 1
        )

    @classmethod
    def from_bounds(
        cls,
        xmin: float | int,
        ymin: float | int,
        xmax: float | int,
        ymax: float | int,
    ) -> Polygon:
        """Create a Polygon geometry from a boundingbox."""
        _xmin, _ymin, _xmax, _ymax = (
            float(xmin),
            float(ymin),
            float(xmax),
            float(ymax),
        )
        return cls(
            type="Polygon",
            coordinates=[
                [
                    (_xmin, _ymin),
                    (_xmax, _ymin),
                    (_xmax, _ymax),
                    (_xmin, _ymax),
                    (_xmin, _ymin),
                ]
            ],
        )

    @property
    def has_z(self) -> bool:
        return any(any(len(c) == 3 for c in line) for line in self.coordinates)


class MultiPolygon(_GeoJsonGeometryABC):
    """GeoJSON-MultiPolygon"""

    type: Literal["MultiPolygon"] = "MultiPolygon"
    coordinates: list[list[LinearRing]]

    @field_validator("coordinates")
    @classmethod
    def check_coordinates(
        cls, polygon: list[list[LinearRing]]
    ) -> list[list[LinearRing]]:
        """Validate that MultiPolygon coordinates pass the GeoJSON spec"""
        if len(polygon) == 0:
            return polygon
        for ring in polygon:
            validate_polygon_coordinates(ring)
        return [
            [[position(coord) for coord in ring] for ring in subpolygon]
            for subpolygon in polygon
        ]

    @property
    def has_z(self) -> bool:
        return any(
            any(any(len(c) == 3 for c in line) for line in lines)
            for lines in self.coordinates
        )


T_Geometry: TypeAlias = Union[
    Point,
    MultiPoint,
    LineString,
    MultiLineString,
    Polygon,
    MultiPolygon,
    "GeometryCollection",
]
Properties = dict[str, Any]
T_Properties = TypeVar("T_Properties", bound=dict[str, Any])
Geometry = Annotated[
    Union[
        Point,
        MultiPoint,
        LineString,
        MultiLineString,
        Polygon,
        MultiPolygon,
        "GeometryCollection",
    ],
    Field(discriminator="type"),
]

Geom = TypeVar("Geom", bound=Geometry)


class GeometryCollection(_GeoJsonGeometryABC, Generic[Geom]):
    """GeoJSON-GeometryCollection pydantic model"""

    type: Literal["GeometryCollection"] = "GeometryCollection"
    geometries: list[Geom] = Field(
        ..., description="List of geometries; should be at least 2 long"
    )

    def __len__(self) -> int:
        """Return geometries length"""
        return len(self.geometries)

    def geometry_ix(self, index: int) -> Geom:
        """Get geometry at a given index"""
        return self.geometries[index]

    def __getitem__(self, index: str | int) -> Geom:
        """Get geometry at a given index"""
        try:
            return self.geometries[index]  # type: ignore[index]
        except TypeError:
            ...
        return super().__getitem__(index)  # type: ignore[misc]

    @property
    def __geo_interface__(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "geometries": [geom.__geo_interface__ for geom in self.geometries],
        }

    def _geometry_collection_types(self) -> set[str]:
        return {el.type for el in self.geometries}


class Feature(_GeoJsonABC, Generic[Geom]):
    """GeoJSON Feature pydantic model ~ generic over geometry type"""

    type: Literal["Feature"] = "Feature"
    id: T_FeatureId | None = None
    geometry: Geom | None = Field(...)

    properties: Properties | None = None
    bbox: BBox | None = _bbox_field
    model_config = ConfigDict(
        use_enum_values=True, arbitrary_types_allowed=True, extra="allow"
    )

    @field_validator("geometry", mode="before")
    @classmethod
    def validate_geometry(cls, geometry: Geom) -> Geom:
        if hasattr(geometry, "__geo_interface__"):
            return geometry.__geo_interface__  # type: ignore[return-value]
        return geometry

    @property
    def __geo_interface__(self) -> dict[str, Any]:
        return self.__json_interface__()

    def __json_interface__(self) -> dict[str, Any]:
        _exclude: set[str] = set()
        if self.bbox is None:
            _exclude.add("bbox")
        if self.id is None:
            _exclude.add("id")
        d = self.model_dump(
            exclude=_exclude,
        )
        # delete the bbox if it is None
        if d.get("geometry") is not None and d["geometry"]["bbox"] is None:
            d["geometry"].pop("bbox", None)
        return d

    @property
    def geom(self) -> Geom:
        if self.geometry is None:
            raise ValueError("No geometry found")
        return self.geometry


PointFeature = Feature[Point]
MultiPointFeature = Feature[MultiPoint]
LineStringFeature = Feature[LineString]
MultiLineStringFeature = Feature[MultiLineString]
PolygonFeature = Feature[Polygon]
MultiPolygonFeature = Feature[MultiPolygon]


class FeatureCollection(_GeoJsonABC, Generic[Geom]):
    """FeatureCollection Model"""

    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: list[Feature[Geom]]
    bbox: BBox | None = _bbox_field

    model_config = ConfigDict(
        use_enum_values=True,
        arbitrary_types_allowed=True,
        extra="allow",
    )

    def __len__(self) -> int:
        """Return features length"""
        return len(self.features)

    def feature_ix(self, index: int) -> Feature[Geom]:
        return self.features[index]

    def __getitem__(self, index: int) -> Feature[Geom]:
        """Get feature at a given index"""
        return self.features[index]

    def __json_interface__(self) -> dict[str, Any]:
        _dict = {
            "type": self.type,
            "features": [feature.__json_interface__() for feature in self.features],
            "bbox": self.bbox,
        }
        if self.bbox is None:
            _dict.pop("bbox")
        return _dict

    @property
    def __geo_interface__(self) -> dict[str, Any]:
        return self.__json_interface__()


def point(
    coordinates: Coordinates,
    *,
    properties: Properties | None = None,
    bbox: BBox | None = None,
    id: T_FeatureId | None = None,
) -> PointFeature:
    return PointFeature(
        type="Feature",
        geometry=Point(type="Point", coordinates=coordinates),
        properties=properties,
        bbox=bbox,
        id=id,
    )


def multi_point(
    coordinates: list[Coordinates],
    *,
    properties: Properties | None = None,
    bbox: BBox | None = None,
    id: T_FeatureId | None = None,
) -> MultiPointFeature:
    return MultiPointFeature(
        type="Feature",
        geometry=MultiPoint(type="MultiPoint", coordinates=coordinates),
        properties=properties,
        bbox=bbox,
        id=id,
    )


def line_string(
    coordinates: list[Coordinates],
    *,
    properties: Properties | None = None,
    bbox: BBox | None = None,
    id: T_FeatureId | None = None,
) -> LineStringFeature:
    return LineStringFeature(
        type="Feature",
        geometry=LineString(type="LineString", coordinates=coordinates),
        properties=properties,
        bbox=bbox,
        id=id,
    )


def multi_line_string(
    coordinates: list[list[Coordinates]],
    *,
    properties: Properties | None = None,
    bbox: BBox | None = None,
    id: T_FeatureId | None = None,
) -> MultiLineStringFeature:
    return MultiLineStringFeature(
        type="Feature",
        geometry=MultiLineString(type="MultiLineString", coordinates=coordinates),
        properties=properties,
        bbox=bbox,
        id=id,
    )


def polygon(
    coordinates: list[list[Coordinates]],
    *,
    properties: Properties | None = None,
    bbox: BBox | None = None,
    id: T_FeatureId | None = None,
) -> PolygonFeature:
    return PolygonFeature(
        type="Feature",
        geometry=Polygon(type="Polygon", coordinates=coordinates),
        properties=properties,
        bbox=bbox,
        id=id,
    )


def multi_polygon(
    coordinates: list[list[list[Coordinates]]],
    *,
    properties: Properties | None = None,
    bbox: BBox | None = None,
    id: T_FeatureId | None = None,
) -> MultiPolygonFeature:
    return MultiPolygonFeature(
        type="Feature",
        geometry=MultiPolygon(type="MultiPolygon", coordinates=coordinates),
        properties=properties,
        bbox=bbox,
        id=id,
    )


def feature_collection(
    features: list[Feature[Geom]],
    *,
    bbox: BBox | None = None,
) -> FeatureCollection[Geom]:
    return FeatureCollection[Geom](
        type="FeatureCollection",
        features=features,
        bbox=bbox,
    )


def features2collection(
    features: Sequence[Feature[Geom]],
    *,
    bbox: BBox | None = None,
) -> FeatureCollection[Geom]:
    return FeatureCollection[Geom](
        type="FeatureCollection",
        features=list(features),
        bbox=bbox,
    )


def parse_geometry_obj(obj: Any) -> T_Geometry:
    """Parse a GeoJSON geometry object and return the corresponding pydantic model.

    `obj` is an object that is supposed to represent a GeoJSON geometry. This method returns the
    reads the `"type"` field and returns the correct pydantic T_Geometry model.
    """
    if obj is None:
        raise GeoJsonError("Parsing None")
    if "type" not in obj:
        raise GeoJsonError('Geometry object must have a "type" field')
    if obj["type"] == "Point":
        return Point.model_validate(obj)
    elif obj["type"] == "MultiPoint":
        return MultiPoint.model_validate(obj)
    elif obj["type"] == "LineString":
        return LineString.model_validate(obj)
    elif obj["type"] == "MultiLineString":
        return MultiLineString.model_validate(obj)
    elif obj["type"] == "Polygon":
        return Polygon.model_validate(obj)
    elif obj["type"] == "MultiPolygon":
        return MultiPolygon.model_validate(obj)
    elif obj["type"] == "GeometryCollection":
        return GeometryCollection.model_validate(obj)
    raise GeoJsonError(f"Unknown geometry type: {obj['type']}")


def parse_geojson(obj: Any) -> Geometry | Feature | FeatureCollection:
    """Parse a GeoJSON geometry object and return the corresponding pydantic model.

    `obj` is an object that is supposed to represent a GeoJSON geometry. This method returns the
    reads the `"type"` field and returns the correct pydantic T_Geometry model.
    """
    if obj is None:
        raise GeoJsonError("Parsing None")
    if "type" not in obj:
        raise GeoJsonError('Geometry object must have a "type" field')
    if obj["type"] == "Feature":
        return Feature.model_validate(obj)
    elif obj["type"] == "FeatureCollection":
        return FeatureCollection.model_validate(obj)
    return parse_geometry_obj(obj)
