from cfo import factors


def test_every_fuel_has_one_positive_value():
    assert not set(factors.AR5_MEDIAN) & set(factors.ASSUMED)
    assert all(v > 0 for v in factors.FACTORS.values())
    assert not set(factors.FACTORS) & set(factors.STORAGE)


def test_sensitivity_bounds_are_the_table_extremes():
    assert min(factors.AR5_MEDIAN.values()) == 11.0 and max(factors.AR5_MEDIAN.values()) == 820.0
