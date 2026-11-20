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

## Deviation 3, Thu Nov 19, 2026: the codebook revision of section 3.1 for scope and for end

What changed: `docs/event_codebook.md` is version 2 (sections 3, 5 and 7, and a new section 9) and `docs/coding_prompt.md` is version 2 (rules 3 and 7, and a Recode instruction). `src/cfo/script_code.py` gained `gcp_ir_end` and `code_v2`: for Google Cloud the script now reads the end from the incident report's own "Incident End" line instead of the dashboard header's "ended at" time, and sets none where that line is absent, unreadable, or before the header's begin time. Nothing else in the script changed. Scope, `end_utc` and `end_basis` of every report were recoded in 27 fresh sessions (`logs/coding/v2/manifest.json`).

Why: this is the revision section 3.1 itself provides. The author's blind check agreed with the coded rows on 23 of 30 scopes (76.7 percent) and 20 of 30 ends (66.7 percent), both under 80 percent. Section 9 of the codebook gives each change and the reports behind it.

Effect on the results: 95 of the 269 recoded rows changed (46 in scope, 34 in end; `dataset/recode_v2_changes.csv`); 34 fields where the script and the model differed take the script's value (`dataset/script_model_diffs_v2.csv`). Report 79 could not be recoded, since its Azure review was gone on Thu Nov 19, 2026, and keeps its version 1 codes. The author's codes stand for his 30 reports. The state counts are in `docs/counts.md`; the count is fixed only after the author's check of the fresh sample of 28 (`dataset/author_sample_2.csv`), whose agreement is reported whatever it shows.

The fresh sample, Thu Nov 19, 2026 (`dataset/author_check_2.csv`): scope 28 of 28, end 27 of 28, so no second revision is needed; the author's end for P3 stands.

A diagnostic, not the registered test: on the author's own 30 reports, the version 2 coding gives his scope for 30 of 30 and his end, within 15 minutes, for 28 of 30. These are the reports the revision was written from, so the figure shows only that version 2 states his reading; the fresh sample is the test.
