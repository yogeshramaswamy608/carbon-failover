"""Lifecycle emission factors, gCO2eq/kWh.

Source: IPCC AR5 WG III, Annex III, Table A.III.2, lifecycle emissions including albedo,
median column (https://www.ipcc.ch/site/assets/uploads/2018/02/ipcc_wg3_ar5_annex-iii.pdf,
page 7 of the PDF, read Nov 6, 2026). Fuels the table does not list are marked ASSUMED and
varied in the sensitivity runs.
"""
from __future__ import annotations

AR5_MEDIAN = {
    "coal": 820.0,          # Coal, PC
    "natural_gas": 490.0,   # Gas, combined cycle
    "nuclear": 12.0,
    "hydro": 24.0,
    "solar": 48.0,          # Solar PV, utility
    "wind": 11.0,           # Wind onshore
    "geothermal": 38.0,
}
ASSUMED = {
    "petroleum": 820.0,     # ASSUMED: not in Table A.III.2; set to the coal median as an upper fossil value
    "other": 490.0,         # ASSUMED: EIA "Other Fuel Sources", set to the gas median
    "unknown": 490.0,       # ASSUMED: EIA "Unknown Fuel Sources", set to the gas median
}
FACTORS = {**AR5_MEDIAN, **ASSUMED}
STORAGE = ("pumped_storage", "battery", "other_storage", "unknown_storage")  # excluded: re-delivered energy
