"""Lifecycle emission factors, gCO2eq/kWh, one value for every fuel the three sources list.

Source: IPCC AR5 WG III, Annex III, Table A.III.2, lifecycle emissions including albedo,
median column (https://www.ipcc.ch/site/assets/uploads/2018/02/ipcc_wg3_ar5_annex-iii.pdf,
page 7 of the PDF). The first seven values were read on that PDF on Nov 6, 2026. The biomass
(dedicated) and offshore wind medians were read on Nov 15, 2026 from Table 8 of a 2024 article in
Science and Technology for Energy Transition (stet-review.org), which reproduces Table A.III.2,
because the IPCC PDF did not open that day. Fuels the table does not list are marked ASSUMED and
varied in the sensitivity runs.
"""
from __future__ import annotations

AR5_MEDIAN = {
    "coal": 820.0,           # Coal, PC
    "natural_gas": 490.0,    # Gas, combined cycle
    "biomass": 230.0,        # Biomass, dedicated
    "nuclear": 12.0,
    "hydro": 24.0,
    "solar": 48.0,           # Solar PV, utility
    "wind": 11.0,            # Wind onshore
    "wind_offshore": 12.0,   # Wind offshore
    "geothermal": 38.0,
}
ASSUMED = {
    "lignite": 820.0,           # ASSUMED: not in Table A.III.2; set to the coal median
    "coal_derived_gas": 820.0,  # ASSUMED: set to the coal median
    "oil_shale": 820.0,         # ASSUMED: set to the coal median
    "peat": 820.0,              # ASSUMED: set to the coal median
    "petroleum": 820.0,         # ASSUMED: oil; set to the coal median as an upper fossil value
    "waste": 490.0,             # ASSUMED: set to the gas median
    "other": 490.0,             # ASSUMED: EIA "Other Fuel Sources" and other "other" categories; the gas median
    "unknown": 490.0,           # ASSUMED: EIA "Unknown Fuel Sources"; the gas median
}
FACTORS = {**AR5_MEDIAN, **ASSUMED}
STORAGE = ("pumped_storage", "battery", "other_storage", "unknown_storage")  # excluded: re-delivered energy
