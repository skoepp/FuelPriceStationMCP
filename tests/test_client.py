"""Tests for the Tankerkoenig API client using respx mocks."""

import httpx
import pytest
import respx

from fuel_price_mcp.client import TankerkoenigClient
from fuel_price_mcp.config import Settings
from fuel_price_mcp.exceptions import TankerkoenigAPIError, TankerkoenigTimeoutError
from tests.fixtures.api_responses import make_api_response


@pytest.fixture
def settings() -> Settings:
    return Settings(
        tankerkoenig_api_key="test-key",
        tankerkoenig_base_url="https://test.tankerkoenig.de/json",
    )


@pytest.fixture
def client(settings: Settings) -> TankerkoenigClient:
    return TankerkoenigClient(settings)


class TestSearchStations:
    @respx.mock
    async def test_success(self, client: TankerkoenigClient):
        respx.get("https://test.tankerkoenig.de/json/list.php").mock(
            return_value=httpx.Response(200, json=make_api_response())
        )
        result = await client.search_stations(lat=52.52, lng=13.405, radius_km=10)
        assert result.ok is True
        assert len(result.stations) == 3

    @respx.mock
    async def test_api_error_response(self, client: TankerkoenigClient):
        respx.get("https://test.tankerkoenig.de/json/list.php").mock(
            return_value=httpx.Response(
                200, json=make_api_response(ok=False, message="apikey invalid", stations=[])
            )
        )
        with pytest.raises(TankerkoenigAPIError, match="apikey invalid"):
            await client.search_stations(lat=52.52, lng=13.405, radius_km=10)

    @respx.mock
    async def test_http_error(self, client: TankerkoenigClient):
        respx.get("https://test.tankerkoenig.de/json/list.php").mock(
            return_value=httpx.Response(500)
        )
        with pytest.raises(TankerkoenigAPIError, match="HTTP 500"):
            await client.search_stations(lat=52.52, lng=13.405, radius_km=10)

    @respx.mock
    async def test_timeout(self, client: TankerkoenigClient):
        respx.get("https://test.tankerkoenig.de/json/list.php").mock(
            side_effect=httpx.ReadTimeout("timeout")
        )
        with pytest.raises(TankerkoenigTimeoutError):
            await client.search_stations(lat=52.52, lng=13.405, radius_km=10)

    @respx.mock
    async def test_sort_dist_for_type_all(self, client: TankerkoenigClient):
        route = respx.get("https://test.tankerkoenig.de/json/list.php").mock(
            return_value=httpx.Response(200, json=make_api_response())
        )
        await client.search_stations(lat=52.52, lng=13.405, radius_km=10, fuel_type="all")
        assert route.called
        request = route.calls[0].request
        assert "sort=dist" in str(request.url)

    @respx.mock
    async def test_no_sort_for_specific_type(self, client: TankerkoenigClient):
        route = respx.get("https://test.tankerkoenig.de/json/list.php").mock(
            return_value=httpx.Response(200, json=make_api_response())
        )
        await client.search_stations(lat=52.52, lng=13.405, radius_km=10, fuel_type="e10")
        request = route.calls[0].request
        assert "sort=" not in str(request.url)
