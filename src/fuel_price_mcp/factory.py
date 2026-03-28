"""Client factory — selects real or demo client based on settings."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fuel_price_mcp.client import TankerkoenigClient

if TYPE_CHECKING:
    from fuel_price_mcp.config import Settings
    from fuel_price_mcp.demo import DemoClient


def create_client(settings: Settings) -> TankerkoenigClient | DemoClient:
    """Create the appropriate client based on demo_mode setting.

    Falls back to DemoClient automatically when no API key is configured.
    """
    if settings.demo_mode or not settings.tankerkoenig_api_key:
        from fuel_price_mcp.demo import DemoClient

        return DemoClient(scenario=settings.demo_scenario)
    return TankerkoenigClient(settings)
