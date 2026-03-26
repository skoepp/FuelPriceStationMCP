"""Demo client with configurable scenarios for development and eval workflows."""

import logging

from fuel_price_mcp.models import Station, StationListResponse

logger = logging.getLogger("fuel_price_mcp.demo")

SCENARIOS: dict[str, list[Station]] = {
    "default": [
        Station(
            id="demo-1",
            name="Aral Tankstelle",
            brand="Aral",
            street="Hauptstraße",
            houseNumber="10",
            postCode=10115,
            place="Berlin",
            lat=52.5200,
            lng=13.4050,
            dist=0.8,
            is_open=True,
            e5=1.879,
            e10=1.819,
            diesel=1.669,
        ),
        Station(
            id="demo-2",
            name="Shell Station",
            brand="Shell",
            street="Friedrichstraße",
            houseNumber="42",
            postCode=10117,
            place="Berlin",
            lat=52.5170,
            lng=13.3880,
            dist=2.1,
            is_open=True,
            e5=1.899,
            e10=1.839,
            diesel=1.689,
        ),
        Station(
            id="demo-3",
            name="ESSO Tankstelle",
            brand="ESSO",
            street="Alexanderplatz",
            houseNumber="1",
            postCode=10178,
            place="Berlin",
            lat=52.5219,
            lng=13.4132,
            dist=3.5,
            is_open=True,
            e5=1.859,
            e10=1.799,
            diesel=1.649,
        ),
        Station(
            id="demo-4",
            name="JET Tankstelle",
            brand="JET",
            street="Prenzlauer Allee",
            houseNumber="88",
            postCode=10405,
            place="Berlin",
            lat=52.5320,
            lng=13.4210,
            dist=5.2,
            is_open=True,
            e5=None,
            e10=1.769,
            diesel=None,
        ),
        Station(
            id="demo-5",
            name="TotalEnergies",
            brand="TotalEnergies",
            street="Kurfürstendamm",
            houseNumber="200",
            postCode=10719,
            place="Berlin",
            lat=52.5040,
            lng=13.3260,
            dist=8.2,
            is_open=True,
            e5=1.849,
            e10=1.789,
            diesel=1.639,
        ),
    ],
    "empty": [],
    "all_closed": [
        Station(
            id="closed-1",
            name="Nachtruhe Tankstelle",
            brand="Aral",
            street="Schloßstraße",
            houseNumber="5",
            postCode=12163,
            place="Berlin",
            lat=52.4580,
            lng=13.3200,
            dist=1.0,
            is_open=False,
            e5=1.879,
            e10=1.819,
            diesel=1.669,
        ),
        Station(
            id="closed-2",
            name="Feierabend Station",
            brand="Shell",
            street="Kantstraße",
            houseNumber="33",
            postCode=10625,
            place="Berlin",
            lat=52.5070,
            lng=13.3150,
            dist=2.5,
            is_open=False,
            e5=1.899,
            e10=1.839,
            diesel=1.689,
        ),
        Station(
            id="closed-3",
            name="Spät Tanke",
            brand="ESSO",
            street="Berliner Straße",
            houseNumber="77",
            postCode=10713,
            place="Berlin",
            lat=52.4830,
            lng=13.3310,
            dist=4.0,
            is_open=False,
            e5=1.859,
            e10=1.799,
            diesel=1.649,
        ),
    ],
    "single_result": [
        Station(
            id="single-1",
            name="Einzige Tankstelle",
            brand="Aral",
            street="Musterweg",
            houseNumber="1",
            postCode=10115,
            place="Berlin",
            lat=52.5200,
            lng=13.4050,
            dist=1.0,
            is_open=True,
            e5=1.859,
            e10=1.799,
            diesel=1.649,
        ),
    ],
}


class DemoClient:
    """Mock client that returns scenario-based data without HTTP calls."""

    def __init__(self, scenario: str = "default") -> None:
        if scenario not in SCENARIOS:
            logger.warning("Unknown demo scenario '%s', falling back to 'default'", scenario)
            scenario = "default"
        self._scenario = scenario

    async def search_stations(
        self,
        lat: float,
        lng: float,
        radius_km: float,
        fuel_type: str = "all",
    ) -> StationListResponse:
        """Return pre-defined stations for the configured scenario."""
        stations = SCENARIOS[self._scenario]
        logger.info(
            "Demo mode: returning %d stations for scenario '%s'",
            len(stations),
            self._scenario,
        )
        return StationListResponse(
            ok=True,
            license="DEMO",
            data="DEMO",
            status="ok",
            stations=stations,
        )
