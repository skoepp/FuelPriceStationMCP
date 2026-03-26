"""Pydantic v2 models for Tankerkoenig API request/response data."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Station(BaseModel):
    """A fuel station as returned by the Tankerkoenig list API."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    brand: str = ""
    street: str = ""
    house_number: str = Field(default="", alias="houseNumber")
    post_code: int | None = Field(default=None, alias="postCode")
    place: str = ""
    lat: float
    lng: float
    dist: float = 0.0
    is_open: bool = Field(alias="isOpen")
    e5: float | None = None
    e10: float | None = None
    diesel: float | None = None


class StationListResponse(BaseModel):
    """Response from the Tankerkoenig list.php endpoint."""

    ok: bool
    license: str = ""
    data: str = ""
    status: str = ""
    message: str | None = None
    stations: list[Station] = Field(default_factory=list)


class FuelSearchRequest(BaseModel):
    """Parameters for a fuel price search."""

    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    radius_km: float = Field(default=15.0, gt=0, le=25)
    fuel_type: Literal["e5", "e10", "diesel"] = Field(default="e10")
    max_results: int = Field(default=10, gt=0, le=50)


class StationResult(BaseModel):
    """A station result formatted for MCP tool output."""

    name: str
    brand: str
    address: str
    distance_km: float
    is_open: bool
    e5: float | None = None
    e10: float | None = None
    diesel: float | None = None
