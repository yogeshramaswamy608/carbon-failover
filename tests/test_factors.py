import pytest

from cfo import factors

EIA_2026 = ["Coal", "Natural Gas", "Nuclear", "All Petroleum Products", "Hydropower Excluding Pumped Storage",
            "Pumped Storage", "Solar without Integrated Battery Storage", "Solar with Integrated Battery Storage",
            "Wind without Integrated Battery Storage", "Wind with Integrated Battery Storage", "Battery Storage",
            "Other Energy Storage", "Unknown Energy Storage", "Geothermal", "Other Fuel Sources", "Unknown Fuel Sources"]
EIA_2018 = ["Coal", "Natural Gas", "Nuclear", "All Petroleum Products", "Hydropower and Pumped Storage", "Solar",
            "Wind", "Other Fuel Sources", "Unknown Fuel Sources"]


def test_every_fuel_has_one_positive_value():
    assert not set(factors.AR5_MEDIAN) & set(factors.ASSUMED)
    assert all(v > 0 for v in factors.FACTORS.values())
    assert not set(factors.FACTORS) & set(factors.STORAGE)


def test_sensitivity_bounds_are_the_table_extremes():
    assert min(factors.AR5_MEDIAN.values()) == 11.0 and max(factors.AR5_MEDIAN.values()) == 820.0


def test_every_label_read_on_the_sources_maps_to_a_value_or_to_storage():
    keys = [factors.key_for("eia930", x) for x in EIA_2026 + EIA_2018]
    keys += [factors.key_for("neso", x) for x in factors.NESO]
    keys += [factors.key_for("energy_charts", x) for x in factors.ENERGY_CHARTS]
    assert all(k in factors.FACTORS or k in factors.STORAGE for k in keys)
    assert factors.key_for("eia930", "Solar with Integrated Battery Storage") == "solar"
    assert factors.key_for("energy_charts", "Wind offshore") == "wind_offshore"


def test_series_that_are_not_generation_map_to_none():
    assert factors.key_for("neso", "imports") is None
    assert all(factors.key_for("energy_charts", x) is None for x in factors.ENERGY_CHARTS_NOT_GENERATION)


def test_unknown_label_stops_the_build():
    for source, label in (("eia930", "Tidal"), ("neso", "tidal"), ("energy_charts", "Marine"), ("eia930", "Solar Thermal")):
        with pytest.raises(ValueError):
            factors.key_for(source, label)
