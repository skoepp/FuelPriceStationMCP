"""FastMCP server with fuel price search tool."""

import logging

from mcp.server.fastmcp import FastMCP
from pydantic import ValidationError

from fuel_price_mcp.client import TankerkoenigClient
from fuel_price_mcp.config import Settings, get_settings
from fuel_price_mcp.demo import DemoClient
from fuel_price_mcp.exceptions import FuelPriceMCPError, NoStationsFoundError
from fuel_price_mcp.factory import create_client
from fuel_price_mcp.filters import (
    filter_by_fuel_availability,
    filter_open_stations,
    sort_by_lowest_price,
)
from fuel_price_mcp.logging import setup_logging
from fuel_price_mcp.models import FuelSearchRequest, StationResult

logger = logging.getLogger("fuel_price_mcp.server")

mcp = FastMCP("FuelPriceStation")

_settings: Settings | None = None
_client: TankerkoenigClient | DemoClient | None = None


def _get_settings() -> Settings:
    """Return cached settings, creating on first call."""
    global _settings
    if _settings is None:
        _settings = get_settings()
    return _settings


def _get_client() -> TankerkoenigClient | DemoClient:
    """Return cached client, creating on first call."""
    global _client
    if _client is None:
        _client = create_client(_get_settings())
    return _client


@mcp.tool()
async def search_fuel_prices(
    lat: float,
    lng: float,
    radius_km: float | None = None,
    fuel_type: str = "e10",
    max_results: int = 10,
) -> list[StationResult]:
    """Search for fuel stations near given coordinates, sorted by lowest price.

    Args:
        lat: Latitude of the search center (-90 to 90).
        lng: Longitude of the search center (-180 to 180).
        radius_km: Search radius in kilometers (default from settings, max 25).
        fuel_type: Fuel type to sort by — "e5", "e10", or "diesel" (default "e10").
        max_results: Maximum number of stations to return (default 10, max 50).

    Returns:
        List of station results with name, address, distance, and fuel prices.
    """
    settings = _get_settings()

    if radius_km is None:
        radius_km = settings.default_radius_km

    try:
        request = FuelSearchRequest(
            lat=lat,
            lng=lng,
            radius_km=radius_km,
            fuel_type=fuel_type,
            max_results=max_results,
        )
    except ValidationError as exc:
        msg = f"Invalid parameters: {exc}"
        raise FuelPriceMCPError(msg) from exc

    client = _get_client()

    try:
        response = await client.search_stations(
            lat=request.lat,
            lng=request.lng,
            radius_km=request.radius_km,
            fuel_type="all",
        )

        stations = response.stations
        stations = filter_open_stations(stations)
        stations = filter_by_fuel_availability(stations)
        stations = sort_by_lowest_price(stations, fuel_type=request.fuel_type)
        stations = stations[: request.max_results]

        if not stations:
            raise NoStationsFoundError(
                f"No open stations with fuel availability found within {request.radius_km}km"
            )

        return [
            StationResult(
                name=s.name,
                brand=s.brand,
                address=f"{s.street} {s.house_number}, {s.post_code or ''} {s.place}".strip(),
                distance_km=round(s.dist, 2),
                is_open=s.is_open,
                e5=s.e5,
                e10=s.e10,
                diesel=s.diesel,
            )
            for s in stations
        ]

    except FuelPriceMCPError:
        raise
    except Exception as exc:
        logger.exception("Unexpected error during fuel price search")
        msg = f"Internal error: {exc}"
        raise FuelPriceMCPError(msg) from exc


def main() -> None:
    """Entry point for the MCP server."""
    settings = _get_settings()
    setup_logging(settings.log_level)
    if settings.demo_mode:
        logger.info("Demo mode active, scenario: %s", settings.demo_scenario)
    mcp.run()


if __name__ == "__main__":
    main()
