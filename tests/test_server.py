"""Integration tests for the MCP server tool function."""

from unittest.mock import AsyncMock, patch

import pytest

from fuel_price_mcp.exceptions import FuelPriceMCPError, NoStationsFoundError
from fuel_price_mcp.models import StationListResponse, StationResult
from fuel_price_mcp.server import search_fuel_prices
from tests.fixtures.api_responses import make_api_response


def _mock_settings(mock):
    """Configure a mock settings object with required attributes."""
    mock.return_value.log_level = "INFO"
    mock.return_value.tankerkoenig_api_key = "test-key"
    mock.return_value.default_radius_km = 15.0


class TestSearchFuelPrices:
    @patch("fuel_price_mcp.server.get_settings")
    @patch("fuel_price_mcp.server.create_client")
    async def test_returns_filtered_sorted_results(self, mock_create_client, mock_settings):
        _mock_settings(mock_settings)

        api_data = make_api_response()
        mock_client = AsyncMock()
        mock_client.search_stations.return_value = StationListResponse.model_validate(api_data)
        mock_create_client.return_value = mock_client

        results = await search_fuel_prices(lat=52.52, lng=13.405)

        assert isinstance(results, list)
        assert all(isinstance(r, StationResult) for r in results)
        # Closed station should be filtered out
        assert len(results) == 2
        # Should be sorted by e10 price (default fuel_type)
        assert results[0].e10 is not None
        assert results[1].e10 is not None
        assert results[0].e10 <= results[1].e10

    @patch("fuel_price_mcp.server.get_settings")
    @patch("fuel_price_mcp.server.create_client")
    async def test_no_stations_raises(self, mock_create_client, mock_settings):
        _mock_settings(mock_settings)

        api_data = make_api_response(stations=[])
        mock_client = AsyncMock()
        mock_client.search_stations.return_value = StationListResponse.model_validate(api_data)
        mock_create_client.return_value = mock_client

        with pytest.raises(NoStationsFoundError):
            await search_fuel_prices(lat=52.52, lng=13.405)

    @patch("fuel_price_mcp.server.get_settings")
    @patch("fuel_price_mcp.server.create_client")
    async def test_max_results_limits_output(self, mock_create_client, mock_settings):
        _mock_settings(mock_settings)

        api_data = make_api_response()
        mock_client = AsyncMock()
        mock_client.search_stations.return_value = StationListResponse.model_validate(api_data)
        mock_create_client.return_value = mock_client

        results = await search_fuel_prices(lat=52.52, lng=13.405, max_results=1)
        assert len(results) == 1

    @patch("fuel_price_mcp.server.get_settings")
    @patch("fuel_price_mcp.server.create_client")
    async def test_unexpected_error_wraps_in_fuel_price_mcp_error(
        self, mock_create_client, mock_settings
    ):
        _mock_settings(mock_settings)

        mock_client = AsyncMock()
        mock_client.search_stations.side_effect = RuntimeError("something broke")
        mock_create_client.return_value = mock_client

        with pytest.raises(FuelPriceMCPError, match="Internal error"):
            await search_fuel_prices(lat=52.52, lng=13.405)

    @patch("fuel_price_mcp.server.get_settings")
    async def test_uses_default_radius_from_settings(self, mock_settings):
        _mock_settings(mock_settings)
        mock_settings.return_value.default_radius_km = 10.0

        mock_client = AsyncMock()
        mock_client.search_stations.return_value = StationListResponse.model_validate(
            make_api_response()
        )

        with patch("fuel_price_mcp.server.create_client", return_value=mock_client):
            await search_fuel_prices(lat=52.52, lng=13.405)

        _, kwargs = mock_client.search_stations.call_args
        assert kwargs["radius_km"] == 10.0

    @patch("fuel_price_mcp.server.get_settings")
    async def test_invalid_lat_raises_fuel_price_mcp_error(self, mock_settings):
        _mock_settings(mock_settings)

        with pytest.raises(FuelPriceMCPError, match="Invalid parameters"):
            await search_fuel_prices(lat=999.0, lng=13.405)

    @patch("fuel_price_mcp.server.get_settings")
    async def test_invalid_fuel_type_raises_fuel_price_mcp_error(self, mock_settings):
        _mock_settings(mock_settings)

        with pytest.raises(FuelPriceMCPError, match="Invalid parameters"):
            await search_fuel_prices(lat=52.52, lng=13.405, fuel_type="lpg")

    @patch("fuel_price_mcp.server.get_settings")
    async def test_radius_over_max_raises_fuel_price_mcp_error(self, mock_settings):
        _mock_settings(mock_settings)

        with pytest.raises(FuelPriceMCPError, match="Invalid parameters"):
            await search_fuel_prices(lat=52.52, lng=13.405, radius_km=30.0)
