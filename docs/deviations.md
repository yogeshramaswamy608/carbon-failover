# Deviations from the preregistration

Every change to `docs/preregistration.md`, `docs/event_codebook.md`, `docs/coding_prompt.md` or `src/cfo/factors.py` after the freeze is listed here before the run it affects: its date, what changed, why, and its effect on the results.

## Deviation 1, Mon Nov 16, 2026: two Energy-Charts labels added to `src/cfo/factors.py`

What changed: the Energy-Charts public power series of Italy (from 2024) and Spain carry two labels that `src/cfo/factors.py` did not hold when it was frozen: "Battery" and "Battery Consumption". As section 3.2 of the preregistration requires, the build stopped on the first of them. "Battery" now maps to `battery`, which is storage output and is excluded, and "Battery Consumption" is listed with the series that are not generation, beside "Hydro pumped storage consumption". No factor value changed and no value was added.

Why: section 3.2 already excludes storage output and counts only generation, so the two labels take the treatment the frozen rules give them. The labels were absent from the series read on Mon Nov 16, 2026 before the freeze, which covered other countries and periods.

Effect on the results: none on any zone or hour without battery data. Where batteries ran, their discharge is left out of the intensity, as pumped storage is. The SHA-256 of `src/cfo/factors.py` in `prereg_hashes.txt` is that of the frozen file; the changed file's hash is recorded with each run.

## Deviation 2, Mon Nov 16, 2026: one EIA-930 label added to `src/cfo/factors.py`

What changed: the EIA-930 balance files from July to December 2024 onward carry the header "Net Generation (MW) from Solar witho Integrated Battery Storage", a truncated form of "without", which the frozen pattern did not match, so the build stopped as section 3.2 requires. The label now maps to `solar`, as both "Solar with" and "Solar without Integrated Battery Storage" already did. No factor value changed.

Why: the label is solar generation whichever word was cut, and the frozen table maps both full forms to solar.

Effect on the results: none beyond letting the files from July 2024 be read; without it every United States hour from July 2024 would be missing.
