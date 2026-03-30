"""Integration tests for the MCP server tool function."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from fuel_price_mcp.config import Settings
from fuel_price_mcp.exceptions import FuelPriceMCPError, NoStationsFoundError
from fuel_price_mcp.models import StationListResponse, StationResult
from fuel_price_mcp.server import AppContext, search_fuel_prices
from tests.fixtures.api_responses import make_api_response


def _make_ctx(
    api_data: dict | None = None,
    default_radius_km: float = 15.0,
    client_side_effect: Exception | None = None,
) -> MagicMock:
    """Create a mock MCP Context with an AppContext lifespan_context."""
    settings = Settings(
        tankerkoenig_api_key="test-key",
        log_level="INFO",
        default_radius_km=default_radius_km,
    )
    mock_client = AsyncMock()
    if client_side_effect is not None:
        mock_client.search_stations.side_effect = client_side_effect
    elif api_data is not None:
        mock_client.search_stations.return_value = StationListResponse.model_validate(api_data)
    else:
        mock_client.search_stations.return_value = StationListResponse.model_validate(
            make_api_response()
        )

    app = AppContext(settings=settings, client=mock_client)

    ctx = MagicMock()
    ctx.request_context.lifespan_context = app
    return ctx


class TestSearchFuelPrices:
    async def test_returns_filtered_sorted_results(self):
        ctx = _make_ctx()

        results = await search_fuel_prices(lat=52.52, lng=13.405, ctx=ctx)

        assert isinstance(results, list)
        assert all(isinstance(r, StationResult) for r in results)
        # Closed station should be filtered out
        assert len(results) == 2
        # Should be sorted by e10 price (default fuel_type)
        assert results[0].e10 is not None
        assert results[1].e10 is not None
        assert results[0].e10 <= results[1].e10

    async def test_no_stations_raises(self):
        ctx = _make_ctx(api_data=make_api_response(stations=[]))

        with pytest.raises(NoStationsFoundError):
            await search_fuel_prices(lat=52.52, lng=13.405, ctx=ctx)

    async def test_max_results_limits_output(self):
        ctx = _make_ctx()

        results = await search_fuel_prices(lat=52.52, lng=13.405, max_results=1, ctx=ctx)
        assert len(results) == 1

    async def test_unexpected_error_wraps_in_fuel_price_mcp_error(self):
        ctx = _make_ctx(client_side_effect=RuntimeError("something broke"))

        with pytest.raises(FuelPriceMCPError, match="Internal error"):
            await search_fuel_prices(lat=52.52, lng=13.405, ctx=ctx)

    async def test_uses_default_radius_from_settings(self):
        ctx = _make_ctx(default_radius_km=10.0)

        await search_fuel_prices(lat=52.52, lng=13.405, ctx=ctx)

        app: AppContext = ctx.request_context.lifespan_context
        _, kwargs = app.client.search_stations.call_args
        assert kwargs["radius_km"] == 10.0

    async def test_invalid_lat_raises_fuel_price_mcp_error(self):
        ctx = _make_ctx()

        with pytest.raises(FuelPriceMCPError, match="Invalid parameters"):
            await search_fuel_prices(lat=999.0, lng=13.405, ctx=ctx)

    async def test_invalid_fuel_type_raises_fuel_price_mcp_error(self):
        ctx = _make_ctx()

        with pytest.raises(FuelPriceMCPError, match="Invalid parameters"):
            await search_fuel_prices(lat=52.52, lng=13.405, fuel_type="lpg", ctx=ctx)

    async def test_radius_over_max_raises_fuel_price_mcp_error(self):
        ctx = _make_ctx()

        with pytest.raises(FuelPriceMCPError, match="Invalid parameters"):
            await search_fuel_prices(lat=52.52, lng=13.405, radius_km=30.0, ctx=ctx)

    async def test_no_context_raises(self):
        with pytest.raises(FuelPriceMCPError, match="Context not available"):
            await search_fuel_prices(lat=52.52, lng=13.405, ctx=None)
