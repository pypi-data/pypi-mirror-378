from typing import Optional

from pydantic import BaseModel


class GetGeometryPayload(BaseModel):
    id_entity: str
    entity_name: str


class GeometryPayload(BaseModel):
    id_entity: str
    entity_name: str
    coords: dict
    representation: Optional[str] = None
    geom_type: str
    zoom: Optional[int] = None


class GeometryResponse(GeometryPayload):
    id: str
    suuid: str
    coords: Optional[dict] = None


class SGLFeature(BaseModel):
    id: Optional[str] = ""
    suuid: Optional[str] = ""
    coords: dict
    entity: Optional[str] = ""
    entityId: Optional[str] = ""
    geomType: str
    representation: Optional[str] = ""
    zoom: Optional[str] = ""
