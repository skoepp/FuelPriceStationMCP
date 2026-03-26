"""Factory functions for realistic Tankerkoenig API test data."""

from fuel_price_mcp.models import Station


def make_station(
    *,
    station_id: str = "station-1",
    name: str = "Test Station",
    brand: str = "TestBrand",
    street: str = "Teststraße",
    house_number: str = "1",
    post_code: int = 10115,
    place: str = "Berlin",
    lat: float = 52.52,
    lng: float = 13.405,
    dist: float = 1.5,
    is_open: bool = True,
    e5: float | None = 1.859,
    e10: float | None = 1.799,
    diesel: float | None = 1.659,
) -> Station:
    """Create a Station with sensible defaults for testing."""
    return Station(
        id=station_id,
        name=name,
        brand=brand,
        street=street,
        houseNumber=house_number,
        postCode=post_code,
        place=place,
        lat=lat,
        lng=lng,
        dist=dist,
        isOpen=is_open,
        e5=e5,
        e10=e10,
        diesel=diesel,
    )


def make_api_response(
    stations: list[dict] | None = None,
    ok: bool = True,
    message: str | None = None,
) -> dict:
    """Create a raw API response dict as returned by Tankerkoenig list.php."""
    if stations is None:
        stations = [
            {
                "id": "station-1",
                "name": "Cheap Station",
                "brand": "BrandA",
                "street": "Hauptstr.",
                "houseNumber": "10",
                "postCode": 10115,
                "place": "Berlin",
                "lat": 52.52,
                "lng": 13.405,
                "dist": 1.2,
                "isOpen": True,
                "e5": 1.859,
                "e10": 1.749,
                "diesel": 1.619,
            },
            {
                "id": "station-2",
                "name": "Medium Station",
                "brand": "BrandB",
                "street": "Nebenstr.",
                "houseNumber": "5",
                "postCode": 10117,
                "place": "Berlin",
                "lat": 52.521,
                "lng": 13.41,
                "dist": 2.5,
                "isOpen": True,
                "e5": 1.879,
                "e10": 1.799,
                "diesel": 1.649,
            },
            {
                "id": "station-3",
                "name": "Closed Station",
                "brand": "BrandC",
                "street": "Abendstr.",
                "houseNumber": "20",
                "postCode": 10119,
                "place": "Berlin",
                "lat": 52.525,
                "lng": 13.42,
                "dist": 3.0,
                "isOpen": False,
                "e5": 1.829,
                "e10": 1.769,
                "diesel": 1.599,
            },
        ]
    return {
        "ok": ok,
        "license": "CC BY 4.0 - https://creativecommons.tankerkoenig.de",
        "data": "MTS-K",
        "status": "ok",
        "message": message,
        "stations": stations,
    }
