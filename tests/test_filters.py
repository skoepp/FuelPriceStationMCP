"""Tests for station filtering and sorting logic."""

import pytest

from fuel_price_mcp.filters import (
    filter_by_fuel_availability,
    filter_open_stations,
    sort_by_lowest_price,
)
from tests.fixtures.api_responses import make_station


class TestFilterOpenStations:
    def test_returns_only_open(self, open_station_all_fuels, closed_station):
        result = filter_open_stations([open_station_all_fuels, closed_station])
        assert len(result) == 1
        assert result[0].id == "open-all"

    def test_empty_list(self):
        assert filter_open_stations([]) == []

    def test_all_closed(self, closed_station):
        assert filter_open_stations([closed_station]) == []

    def test_all_open(self, open_station_all_fuels, open_station_e10_only):
        result = filter_open_stations([open_station_all_fuels, open_station_e10_only])
        assert len(result) == 2


class TestFilterByFuelAvailability:
    def test_all_fuels_passes(self, open_station_all_fuels):
        result = filter_by_fuel_availability([open_station_all_fuels])
        assert len(result) == 1

    def test_e10_only_passes(self, open_station_e10_only):
        result = filter_by_fuel_availability([open_station_e10_only])
        assert len(result) == 1

    def test_no_e10_rejected(self, open_station_no_e10):
        result = filter_by_fuel_availability([open_station_no_e10])
        assert len(result) == 0

    def test_no_fuels_rejected(self):
        station = make_station(e5=None, e10=None, diesel=None)
        result = filter_by_fuel_availability([station])
        assert len(result) == 0

    def test_empty_list(self):
        assert filter_by_fuel_availability([]) == []

    def test_mixed(self, open_station_all_fuels, open_station_e10_only, open_station_no_e10):
        result = filter_by_fuel_availability(
            [open_station_all_fuels, open_station_e10_only, open_station_no_e10]
        )
        assert len(result) == 2
        ids = {s.id for s in result}
        assert ids == {"open-all", "open-e10"}


class TestSortByLowestPrice:
    def test_sort_by_e10(self):
        expensive = make_station(station_id="expensive", e10=1.899)
        cheap = make_station(station_id="cheap", e10=1.699)
        medium = make_station(station_id="medium", e10=1.799)
        result = sort_by_lowest_price([expensive, cheap, medium], fuel_type="e10")
        assert [s.id for s in result] == ["cheap", "medium", "expensive"]

    def test_sort_by_diesel(self):
        a = make_station(station_id="a", diesel=1.559)
        b = make_station(station_id="b", diesel=1.619)
        result = sort_by_lowest_price([b, a], fuel_type="diesel")
        assert [s.id for s in result] == ["a", "b"]

    def test_none_prices_go_last(self):
        with_price = make_station(station_id="priced", e10=1.799)
        no_price = make_station(station_id="no-price", e10=None)
        result = sort_by_lowest_price([no_price, with_price], fuel_type="e10")
        assert [s.id for s in result] == ["priced", "no-price"]

    def test_empty_list(self):
        assert sort_by_lowest_price([]) == []

    @pytest.mark.parametrize(
        ("fuel_type", "expected_first"),
        [
            ("e5", "cheap-e5"),
            ("e10", "cheap-e10"),
            ("diesel", "cheap-diesel"),
        ],
    )
    def test_parametrized_fuel_types(self, fuel_type, expected_first):
        stations = [
            make_station(station_id="cheap-e5", e5=1.700, e10=1.900, diesel=1.700),
            make_station(station_id="cheap-e10", e5=1.900, e10=1.700, diesel=1.900),
            make_station(station_id="cheap-diesel", e5=1.800, e10=1.800, diesel=1.500),
        ]
        result = sort_by_lowest_price(stations, fuel_type=fuel_type)
        assert result[0].id == expected_first
