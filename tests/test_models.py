"""Tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from fuel_price_mcp.models import (
    FuelSearchRequest,
    Station,
    StationListResponse,
    StationResult,
)


class TestStation:
    def test_parse_with_aliases(self):
        data = {
            "id": "abc",
            "name": "Test",
            "lat": 52.0,
            "lng": 13.0,
            "isOpen": True,
            "houseNumber": "42",
            "postCode": 10115,
        }
        station = Station.model_validate(data)
        assert station.is_open is True
        assert station.house_number == "42"
        assert station.post_code == 10115

    def test_parse_with_python_names(self):
        station = Station(
            id="abc",
            name="Test",
            lat=52.0,
            lng=13.0,
            is_open=False,
            house_number="7",
        )
        assert station.is_open is False
        assert station.house_number == "7"

    def test_optional_prices_default_none(self):
        station = Station(id="x", name="X", lat=0, lng=0, isOpen=True)
        assert station.e5 is None
        assert station.e10 is None
        assert station.diesel is None

    def test_full_station(self):
        station = Station(
            id="full",
            name="Full",
            brand="Shell",
            lat=52.0,
            lng=13.0,
            dist=3.5,
            isOpen=True,
            e5=1.859,
            e10=1.799,
            diesel=1.659,
        )
        assert station.e5 == 1.859
        assert station.dist == 3.5


class TestStationListResponse:
    def test_parse_ok_response(self):
        data = {
            "ok": True,
            "license": "CC BY 4.0",
            "data": "MTS-K",
            "status": "ok",
            "stations": [{"id": "1", "name": "S1", "lat": 52.0, "lng": 13.0, "isOpen": True}],
        }
        resp = StationListResponse.model_validate(data)
        assert resp.ok is True
        assert len(resp.stations) == 1

    def test_parse_error_response(self):
        data = {"ok": False, "message": "apikey invalid"}
        resp = StationListResponse.model_validate(data)
        assert resp.ok is False
        assert resp.message == "apikey invalid"

    def test_empty_stations(self):
        data = {"ok": True}
        resp = StationListResponse.model_validate(data)
        assert resp.stations == []


class TestFuelSearchRequest:
    def test_defaults(self):
        req = FuelSearchRequest(lat=52.0, lng=13.0)
        assert req.radius_km == 15.0
        assert req.fuel_type == "e10"
        assert req.max_results == 10

    def test_valid_fuel_types(self):
        for fuel in ("e5", "e10", "diesel"):
            req = FuelSearchRequest(lat=52.0, lng=13.0, fuel_type=fuel)
            assert req.fuel_type == fuel

    def test_invalid_fuel_type(self):
        with pytest.raises(ValidationError):
            FuelSearchRequest(lat=52.0, lng=13.0, fuel_type="lpg")

    def test_lat_out_of_range(self):
        with pytest.raises(ValidationError):
            FuelSearchRequest(lat=91.0, lng=0.0)

    def test_lng_out_of_range(self):
        with pytest.raises(ValidationError):
            FuelSearchRequest(lat=0.0, lng=181.0)

    def test_radius_zero_invalid(self):
        with pytest.raises(ValidationError):
            FuelSearchRequest(lat=0.0, lng=0.0, radius_km=0)

    def test_radius_over_max_invalid(self):
        with pytest.raises(ValidationError):
            FuelSearchRequest(lat=0.0, lng=0.0, radius_km=26)


class TestStationResult:
    def test_serialization(self):
        result = StationResult(
            name="Test",
            brand="Shell",
            address="Main St 1, 10115 Berlin",
            distance_km=2.3,
            is_open=True,
            e5=1.859,
            e10=1.799,
            diesel=None,
        )
        data = result.model_dump()
        assert data["name"] == "Test"
        assert data["diesel"] is None
