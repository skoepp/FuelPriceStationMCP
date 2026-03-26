"""Pure functions for filtering and sorting fuel stations."""

from fuel_price_mcp.models import Station


def filter_open_stations(stations: list[Station]) -> list[Station]:
    """Return only stations that are currently open.

    NOTE: The list.php API only provides isOpen (boolean), not closing times.
    A future enhancement could call detail.php per station to check hours-before-close.
    """
    # TODO: Enhance with closing-time check via detail.php for "1hr before closing" requirement
    return [s for s in stations if s.is_open]


def filter_by_fuel_availability(stations: list[Station]) -> list[Station]:
    """Return stations where all fuel types are available, or at minimum E10 is available.

    A station passes if:
    - All three fuel types (e5, e10, diesel) have a price, OR
    - At least e10 has a price
    """
    return [s for s in stations if _all_fuels_available(s) or s.e10 is not None]


def sort_by_lowest_price(
    stations: list[Station],
    fuel_type: str = "e10",
) -> list[Station]:
    """Sort stations by the lowest price for the given fuel type.

    Stations without a price for the given fuel type are placed at the end.
    """

    def sort_key(station: Station) -> float:
        price: float | None = getattr(station, fuel_type, None)
        if price is None:
            return float("inf")
        return price

    return sorted(stations, key=sort_key)


def _all_fuels_available(station: Station) -> bool:
    """Check if a station has prices for all fuel types."""
    return station.e5 is not None and station.e10 is not None and station.diesel is not None
