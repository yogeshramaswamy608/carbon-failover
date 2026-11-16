# Data prepared for study 2 (preregistration section 3)

Built on Mon Nov 16, 2026 from version 1.0.0 of the companion corpus (10.5281/zenodo.23973151, `corpus.csv`, SHA-256 12f79715...59db2), under the frozen design (commit d2a9a50, 10.5281/zenodo.24275704) and the deviations listed in `docs/deviations.md`. No policy has been run. Report text is not stored or released; each row keeps the report's link and the coded fields.

| File | What it holds |
|---|---|
| `script_fields.csv` | The script's fields per kept report (the Google Cloud began/ended line and locations, the Azure UTC window); `src/cfo/script_run.py`, run in the workflow `script-coding`. |
| `coded.csv` | One row per kept report under `docs/event_codebook.md`: the model's codes with the script's fields standing where both set one. `link` is the page the coding read. |
| `script_model_diffs.csv` | Every field where the script and the model differed; the script's value stands. |
| `events.csv`, `merges.csv` | Events after merging reports of one incident (codebook section 6), and each merge. |
| `instances_ruled.csv` | Every event-home instance with the first rule of section 3.1 it fails, or `kept`, and its candidate destinations. |
| `exclusions.csv` | Counts by rule, for instances and events (`docs/counts.md`). |
| `region_table.csv` | The 58 general-purpose regions of the three providers in the United States and Europe: location from the provider's documentation, general-availability date with the page read, grid zone with its source. |
| `ci_hourly.csv.gz` | Hourly production-based carbon intensity per grid zone, gCO2eq/kWh, each hour labelled by its start in UTC; no hour filled. |
| `latency_check_azure.csv` | The latency model of section 3.3 against Microsoft's published Azure round-trip table (P50, 30 days to Jul 30, 2026). |
| `author_sample.csv` | The 30 reports of the author's blind check, drawn by the "author-sample" stream. His codes are added after his check. |

Readings recorded here, for review:
- Azure links: `aka.ms/AzPIR/ID` opens Microsoft's feedback form, so the coding read `https://azure.status.microsoft/en-us/status/history/?trackingId=ID`, and that link is released.
- General-availability dates are taken at the precision the provider's page gives. A year or a month counts from the end of that period. Five regions have no page announcing their own launch; each takes the earliest provider page that shows it available (`ga_precision` on_or_before): Azure North Central US, South Central US and North Europe from the Azure blog of Feb 22, 2010; Google Cloud us-central1 and europe-west1 from the Google Cloud Platform blog of Oct 1, 2015. Every corpus event of those providers starts years later.
- Azure West US is left out: no public source names its data-centre place, so its grid zone is not established.
- Azure West Central US takes WACM before 2026-04-01T00:00Z and BHBA from then, as EIA-930 retired WACM and activated BHBA (Black Hills Energy) that day.
- Coordinates: AWS from its own regions page; Azure and Google Cloud from the place the provider names (or the data-centre place for a state-only name), approximate and ASSUMED. Against Microsoft's table, the model's median absolute error is 6.3 ms, and it runs low.
- Great Britain 2018: the NESO API holds 5,517 hours of that year; the missing hours are not filled.

Sources and licenses: EIA-930 (public domain, U.S. Energy Information Administration); NESO Carbon Intensity API generation mix (CC BY 4.0, National Energy System Operator); Energy-Charts public power (CC BY 4.0, Fraunhofer ISE). The files here are CC BY 4.0.
