"""Async HTTP client for the Tankerkoenig API."""

import logging

import httpx

from fuel_price_mcp.config import Settings
from fuel_price_mcp.exceptions import (
    TankerkoenigAPIError,
    TankerkoenigTimeoutError,
)
from fuel_price_mcp.models import StationListResponse

logger = logging.getLogger("fuel_price_mcp.client")


class TankerkoenigClient:
    """Async client for the Tankerkoenig fuel price API."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._base_url = settings.tankerkoenig_base_url
        self._api_key = settings.tankerkoenig_api_key
        self._timeout = httpx.Timeout(settings.request_timeout_seconds)

    async def search_stations(
        self,
        lat: float,
        lng: float,
        radius_km: float,
        fuel_type: str = "all",
    ) -> StationListResponse:
        """Search for fuel stations near the given coordinates.

        Args:
            lat: Latitude of the search center.
            lng: Longitude of the search center.
            radius_km: Search radius in kilometers (max 25).
            fuel_type: Fuel type filter — "e5", "e10", "diesel", or "all".

        Returns:
            Parsed station list response from the API.

        Raises:
            TankerkoenigAPIError: If the API returns an error or non-ok response.
            TankerkoenigTimeoutError: If the request times out.
        """
        params: dict[str, str | float] = {
            "lat": lat,
            "lng": lng,
            "rad": radius_km,
            "type": fuel_type,
            "apikey": self._api_key,
        }
        # type=all requires sort=dist per Tankerkoenig API docs
        if fuel_type == "all":
            params["sort"] = "dist"

        url = f"{self._base_url}/list.php"
        logger.info("Requesting stations at lat=%s lng=%s radius=%skm", lat, lng, radius_km)

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise TankerkoenigTimeoutError(
                f"Tankerkoenig API request timed out after {self._timeout.read}s"
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise TankerkoenigAPIError(
                f"Tankerkoenig API returned HTTP {exc.response.status_code}",
                status_code=exc.response.status_code,
            ) from exc

        data = response.json()
        parsed = StationListResponse.model_validate(data)

        if not parsed.ok:
            raise TankerkoenigAPIError(
                f"Tankerkoenig API error: {parsed.message or 'unknown error'}"
            )

        logger.info("Found %d stations", len(parsed.stations))
        return parsed
