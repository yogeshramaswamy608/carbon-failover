# carbon-failover

Code and data pipeline for the study "Carbon-Aware Failover Without Losing Reliability" (Yogesh Ramaswamy).

The study asks where traffic should go when a cloud region fails, if carbon is one of the criteria: how much carbon a carbon-aware failover saves against a nearest-region failover, and what it costs in recovery time and in exposure to a correlated second failure.

## Status

The study design is written in `docs/preregistration.md` (version 1, Mon Nov 16, 2026), with the outage coding rules in `docs/event_codebook.md` and the coding instruction in `docs/coding_prompt.md`. After two independent reviews it is frozen by the commit that adds `prereg_hashes.txt` with the SHA-256 of those three files and `src/cfo/factors.py`; the same four files are deposited on Zenodo that day. Any change after the freeze is listed in `docs/deviations.md`. No result has been produced yet.

## Data pipeline

1. `scripts/fetch_eia930.sh data/eia` downloads the EIA-930 hourly balance files, 2018 to 2026.
2. `python -m cfo.eia data/eia/*.csv > ci.csv` writes hourly production-based carbon intensity per balancing authority, each hour labelled by its start in UTC.

Emission factors are the lifecycle medians of IPCC AR5 WG III Annex III, Table A.III.2 (see `src/cfo/factors.py`); fuels the table does not list are marked ASSUMED there and varied in the sensitivity runs. Storage output is excluded, and imports are not traced.

Third-party data keeps its own license and is not redistributed here; the scripts fetch it.

## Licenses

Code: Apache License 2.0 (`LICENSE`). The design documents in `docs/` and the data created for this study: Creative Commons Attribution 4.0.

## Assistance

The author approved the data sources and the test bed, codes the blind sample of the outage coding, reads the results and the paper before submission, and is responsible for every claim. Claude models from Anthropic drafted the design and the text, write and run the code and the test bed, and code the outage events; `docs/ai_use.md` lists each use.
