# carbon-failover

Code and data pipeline for the study "Carbon-Aware Failover Without Losing Reliability" (Yogesh Ramaswamy).

## Data pipeline

1. `scripts/fetch_eia930.sh data/eia` downloads the EIA-930 hourly balance files, 2018 to 2026.
2. `python -m cfo.eia data/eia/*.csv > ci.csv` writes hourly production-based carbon intensity per balancing authority.

Emission factors are the lifecycle medians of IPCC AR5 WG III Annex III, Table A.III.2 (see `src/cfo/factors.py`); fuels the table does not list are marked ASSUMED there and varied in the sensitivity runs. Storage output is excluded, and imports are not traced.

Third-party data keeps its own license and is not redistributed here; the scripts fetch it.
