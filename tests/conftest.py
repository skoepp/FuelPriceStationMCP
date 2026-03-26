"""Shared test fixtures."""

import pytest

import fuel_price_mcp.server as _server_module
from fuel_price_mcp.config import Settings
from fuel_price_mcp.models import Station
from tests.fixtures.api_responses import make_station


@pytest.fixture(autouse=True)
def _reset_server_cache():
    """Reset cached settings and client between tests."""
    _server_module._settings = None
    _server_module._client = None
    yield
    _server_module._settings = None
    _server_module._client = None


@pytest.fixture
def test_settings() -> Settings:
    """Settings configured for testing."""
    return Settings(
        tankerkoenig_api_key="test-api-key-00000000-0000-0000-0000-000000000000",
        log_level="DEBUG",
        default_radius_km=10.0,
    )


@pytest.fixture
def open_station_all_fuels() -> Station:
    return make_station(
        station_id="open-all",
        name="Open All Fuels",
        is_open=True,
        e5=1.859,
        e10=1.799,
        diesel=1.659,
    )


@pytest.fixture
def open_station_e10_only() -> Station:
    return make_station(
        station_id="open-e10",
        name="Open E10 Only",
        is_open=True,
        e5=None,
        e10=1.819,
        diesel=None,
    )


@pytest.fixture
def open_station_no_e10() -> Station:
    return make_station(
        station_id="open-no-e10",
        name="Open No E10",
        is_open=True,
        e5=1.899,
        e10=None,
        diesel=1.679,
    )


@pytest.fixture
def closed_station() -> Station:
    return make_station(
        station_id="closed",
        name="Closed Station",
        is_open=False,
        e5=1.829,
        e10=1.769,
        diesel=1.599,
    )
