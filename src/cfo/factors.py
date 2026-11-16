"""Lifecycle emission factors, gCO2eq/kWh, and the table that maps each source's fuel label to one.

Values: IPCC AR5 Working Group III, Annex III, Table A.III.2, the column "Lifecycle emissions
(incl. albedo effect)", median (https://www.ipcc.ch/site/assets/uploads/2018/02/ipcc_wg3_ar5_annex-iii.pdf,
page 7 of the PDF, page 1335 of the report). All nine medians below were read on that page on
Nov 16, 2026. A fuel the table does not list is marked ASSUMED and varied in the sensitivity runs.

Labels: every fuel label the three sources showed when they were read on Nov 16, 2026: the
EIA-930 balance files of July to December 2018 and January to June 2026, the generation mix of the
NESO Carbon Intensity API, and the Energy-Charts public power series of 14 countries (AT, BE, CH,
DE, DK, ES, FI, FR, IE, IT, NL, NO, PL, SE). A label this file does not hold stops the build; it is
added, with its value, by an entry in docs/deviations.md.

This file is frozen with docs/preregistration.md.
"""
from __future__ import annotations

import re

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
    "lignite": 820.0,           # ASSUMED: not in the table; the coal median
    "coal_derived_gas": 820.0,  # ASSUMED: the coal median
    "peat": 820.0,              # ASSUMED: the coal median
    "petroleum": 820.0,         # ASSUMED: oil; the coal median as an upper fossil value
    "waste": 490.0,             # ASSUMED: the gas median
    "other": 490.0,             # ASSUMED: "other" fuel categories; the gas median
    "unknown": 490.0,           # ASSUMED: EIA "Unknown Fuel Sources"; the gas median
    "other_renewables": 230.0,  # ASSUMED: the dedicated biomass median, the highest renewable median
}
FACTORS = {**AR5_MEDIAN, **ASSUMED}
STORAGE = ("pumped_storage", "battery", "other_storage", "unknown_storage")  # excluded: re-delivered energy

# EIA-930: the text after "Net Generation (MW) from ", first match wins.
EIA_930 = [
    (r"^Coal$", "coal"), (r"^Natural Gas$", "natural_gas"), (r"^Nuclear$", "nuclear"),
    (r"^All Petroleum Products$", "petroleum"),
    (r"^Hydropower and Pumped Storage$", "hydro"),  # one column in the older files: counted as hydro
    (r"^Hydropower Excluding Pumped Storage$", "hydro"),
    (r"^Pumped Storage$", "pumped_storage"),
    (r"^Solar( with| without) Integrated Battery Storage$|^Solar$", "solar"),
    (r"^Wind( with| without) Integrated Battery Storage$|^Wind$", "wind"),
    (r"^Battery Storage$", "battery"), (r"^Other Energy Storage$", "other_storage"),
    (r"^Unknown Energy Storage$", "unknown_storage"), (r"^Geothermal$", "geothermal"),
    (r"^Other Fuel Sources$", "other"), (r"^Unknown Fuel Sources$", "unknown"),
]

# NESO generation mix: fuel name to key. "imports" is removed and the rest rescaled to 100 percent.
NESO = {
    "biomass": "biomass", "coal": "coal", "gas": "natural_gas", "nuclear": "nuclear",
    "other": "other", "hydro": "hydro", "solar": "solar", "wind": "wind",
}
NESO_NOT_GENERATION = ("imports",)

# Energy-Charts public power: production type to key.
ENERGY_CHARTS = {
    "Biomass": "biomass",
    "Fossil brown coal / lignite": "lignite",
    "Fossil coal-derived gas": "coal_derived_gas",
    "Fossil gas": "natural_gas",
    "Fossil hard coal": "coal",
    "Fossil oil": "petroleum",
    "Fossil peat": "peat",
    "Geothermal": "geothermal",
    "Hydro Run-of-River": "hydro",
    "Hydro water reservoir": "hydro",
    "Hydro pumped storage": "pumped_storage",
    "Nuclear": "nuclear",
    "Other renewables": "other_renewables",
    "Others": "other",
    "Solar": "solar",
    "Waste": "waste",
    "Wind offshore": "wind_offshore",
    "Wind onshore": "wind",
}
ENERGY_CHARTS_NOT_GENERATION = (
    "Cross border electricity trading", "Hydro pumped storage consumption", "Load", "Residual load",
    "Renewable share of generation", "Renewable share of load",
)


def key_for(source: str, label: str) -> str | None:
    """The factor key of a source's fuel label; None for a series that is not generation.

    Raises ValueError for a label this file does not hold.
    """
    label = " ".join(label.split())
    if source == "eia930":
        for pattern, key in EIA_930:
            if re.search(pattern, label):
                return key
    elif source == "neso":
        if label in NESO_NOT_GENERATION:
            return None
        if label in NESO:
            return NESO[label]
    elif source == "energy_charts":
        if label in ENERGY_CHARTS_NOT_GENERATION:
            return None
        if label in ENERGY_CHARTS:
            return ENERGY_CHARTS[label]
    else:
        raise ValueError(f"unknown source: {source}")
    raise ValueError(f"unmapped fuel label for {source}: {label}")
