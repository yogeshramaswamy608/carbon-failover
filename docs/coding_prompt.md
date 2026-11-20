# Coding prompt, version 2

The exact instruction each coding session receives, followed by up to 10 reports. Frozen with `docs/preregistration.md` as version 1; version 2 of Thu Nov 19, 2026 revises rules 3 and 7 to match the event codebook, version 2 (`docs/deviations.md`, deviation 3). The section Recode instruction is what the recode sessions of Thu Nov 19, 2026 received.

## Instruction

You code public cloud post-incident reports for a research study. Each report follows this instruction, with its corpus number, provider and link. Code each report on its own.

For each report, return one JSON object with exactly these keys: `corpus_no`, `provider`, `published_utc`, `scope`, `regions`, `zones`, `start_utc`, `start_precision`, `end_utc`, `end_basis`, `duration_min`, `region_starts`, `services_n`, `evidence`, `notes`. Return a JSON list of these objects and nothing else.

Rules:

1. Code only what the report states. Leave a field empty ("") when the report does not support it, and say why in `notes`. Never guess.
2. `published_utc`: the date the report itself shows as its publication date, as YYYY-MM-DD. If it shows none, leave it empty and write "no publication date shown" in `notes`.
3. `scope`: judge from what the report says was impaired for customers, including region-wide operations (launching or creating resources, API and management calls). zonal (the impact stayed in one named zone: no word on impact outside it, which you note, or the report says the other zones and region-wide operations kept serving); regional (one region impaired beyond one zone: more than one zone, the whole region, or its region-wide launch, API or management calls, even when the fault began in one zone); multi_region (two or more regions, not all regions of the provider's public cloud; also "multiple regions" or "several regions" without names, a Google Cloud multi-region or dual-region location such as us, eu or nam5, and "all regions" of a separate or sovereign cloud such as Azure Government, or of one named geography); global (the report says global, worldwide or all regions of the provider's public cloud for the affected service, lists the location Global, or names every region); unclear (no region named and no word on how many).
4. `regions` and `zones`: the provider's own codes, joined by ";". AWS as us-east-1; Azure as the programmatic name (eastus for "East US"); Google Cloud as us-central1. A named zone also adds its region. A Google Cloud multi-region or dual-region location (us, eu, nam5) is not a region: add no code for it and name it in `notes`.
5. Times: ISO 8601 in UTC, as YYYY-MM-DDTHH:MMZ. Google Cloud reports use US/Pacific; AWS reports name PDT or PST; Azure reports use UTC. Convert with the daylight-saving rule of the date.
6. `start_utc`: the first moment of customer impact the report states. `start_precision`: minute, hour or day, the finest unit the report gives.
7. `end_utc` and `end_basis`: a moment the report itself states as the end of customer impact for the event as a whole (the event finished, all affected services back to normal, the incident ended, resolved for all affected users). `end_basis` is impact_ended for a statement that impact ended or service was restored, mitigated for one that it was only mitigated, resolved for one that it was only fully resolved. Do not build an end from parts: recovery times service by service, or "most customers" or "most resources" recovered, are not the end when the report says other services, customers or a zone stayed impaired after them. A stated moment is not the end when the report says impact went on after it; take the next whole-event statement, if any. If the report states no such moment, leave both empty and say why in `notes`. Backlog processing is outside the event only when the report states that customer impact had ended before it. Google Cloud: the incident report's "Incident End" line (the newest report on the page that has one; the latest of several windows) is taken over the "ended at" time in the page header; if that line's date contradicts the page's dated updates, use the dated updates and say so in `notes`; a page with no "Incident End" line takes the header's "ended at" time unless the page says impact went on after it.
8. `duration_min`: only when the report states how long the impact lasted and gives no start and end pair, the length in whole minutes. Otherwise leave it empty.
9. `region_starts`: only when the report gives a different start for some region, as region=time pairs joined by ";".
10. `services_n`: the number of distinct products or services the report names as impaired.
11. `evidence`: for the start, the end and the regions, the report section and a paraphrase in your own words, at most 25 words each. Copy no sentence from the report.

## Recode instruction

Used Thu Nov 19, 2026 for the full recode of `scope` and of `end_utc` and `end_basis` that section 3.1 of the preregistration requires. The session receives the Instruction above, then this paragraph, then the reports.

Recode only `scope`, `end_utc` and `end_basis` under rules 1, 3, 5 and 7 above; every other field of the first coding stands. For each report return one JSON object with exactly these keys: `corpus_no`, `provider`, `scope`, `end_utc`, `end_basis`, `evidence`, `notes`. `evidence` holds, for the scope and for the end, the report section and a paraphrase in your own words, at most 25 words each; copy no sentence from the report. Return a JSON list of these objects and nothing else.
