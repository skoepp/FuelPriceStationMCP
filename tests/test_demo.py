"""Tests for demo client, factory, and demo mode integration."""

from unittest.mock import MagicMock

import pytest

from fuel_price_mcp.client import TankerkoenigClient
from fuel_price_mcp.config import Settings
from fuel_price_mcp.demo import SCENARIOS, DemoClient
from fuel_price_mcp.exceptions import NoStationsFoundError
from fuel_price_mcp.factory import create_client
from fuel_price_mcp.server import AppContext, search_fuel_prices


class TestDemoClient:
    async def test_default_scenario_returns_stations(self):
        client = DemoClient(scenario="default")
        result = await client.search_stations(lat=52.52, lng=13.405, radius_km=10)
        assert result.ok is True
        assert len(result.stations) == 5

    async def test_empty_scenario(self):
        client = DemoClient(scenario="empty")
        result = await client.search_stations(lat=52.52, lng=13.405, radius_km=10)
        assert result.ok is True
        assert len(result.stations) == 0

    async def test_all_closed_scenario(self):
        client = DemoClient(scenario="all_closed")
        result = await client.search_stations(lat=52.52, lng=13.405, radius_km=10)
        assert all(not s.is_open for s in result.stations)
        assert len(result.stations) == 3

    async def test_single_result_scenario(self):
        client = DemoClient(scenario="single_result")
        result = await client.search_stations(lat=52.52, lng=13.405, radius_km=10)
        assert len(result.stations) == 1
        assert result.stations[0].is_open is True

    async def test_unknown_scenario_falls_back_to_default(self):
        client = DemoClient(scenario="nonexistent")
        result = await client.search_stations(lat=0, lng=0, radius_km=5)
        assert len(result.stations) == len(SCENARIOS["default"])


class TestFactory:
    def test_demo_mode_returns_demo_client(self):
        settings = Settings(demo_mode=True, demo_scenario="default")
        client = create_client(settings)
        assert isinstance(client, DemoClient)

    def test_normal_mode_returns_real_client(self):
        settings = Settings(demo_mode=False, tankerkoenig_api_key="key")
        client = create_client(settings)
        assert isinstance(client, TankerkoenigClient)


def _demo_ctx(scenario: str = "default") -> MagicMock:
    """Create a mock MCP Context with a real DemoClient."""
    settings = Settings(demo_mode=True, demo_scenario=scenario)
    app = AppContext(settings=settings, client=DemoClient(scenario=scenario))
    ctx = MagicMock()
    ctx.request_context.lifespan_context = app
    return ctx


class TestDemoIntegration:
    async def test_full_pipeline_with_demo(self):
        ctx = _demo_ctx("default")

        results = await search_fuel_prices(lat=52.52, lng=13.405, ctx=ctx)

        assert isinstance(results, list)
        assert len(results) > 0
        assert all(hasattr(r, "name") for r in results)
        assert all(hasattr(r, "e10") for r in results)

    async def test_empty_scenario_raises_no_stations(self):
        ctx = _demo_ctx("empty")

        with pytest.raises(NoStationsFoundError):
            await search_fuel_prices(lat=52.52, lng=13.405, ctx=ctx)

    async def test_all_closed_raises_no_stations(self):
        ctx = _demo_ctx("all_closed")

        with pytest.raises(NoStationsFoundError):
            await search_fuel_prices(lat=52.52, lng=13.405, ctx=ctx)
