# Coding prompt, version 1

The exact instruction each coding session receives, followed by up to 10 reports. Frozen with `docs/preregistration.md`.

## Instruction

You code public cloud post-incident reports for a research study. Each report follows this instruction, with its corpus number, provider and link. Code each report on its own.

For each report, return one JSON object with exactly these keys: `corpus_no`, `provider`, `published_utc`, `scope`, `regions`, `zones`, `start_utc`, `start_precision`, `end_utc`, `end_basis`, `region_starts`, `services_n`, `evidence`, `notes`. Return a JSON list of these objects and nothing else.

Rules:

1. Code only what the report states. Leave a field empty ("") when the report does not support it, and say why in `notes`. Never guess.
2. `published_utc`: the date the report itself shows as its publication date, as YYYY-MM-DD. If it shows none, leave it empty and write "no publication date shown" in `notes`.
3. `scope`: zonal (one zone named, the region's other zones serving, or no word on them, which you note), regional (one region beyond one zone, or the whole region), multi_region (two or more named regions, not all), global (the report says global, worldwide or all regions for the affected service), unclear (no region named, or "multiple regions" without names).
4. `regions` and `zones`: the provider's own codes, joined by ";". AWS as us-east-1; Azure as the programmatic name (eastus for "East US"); Google Cloud as us-central1. A named zone also adds its region.
5. Times: ISO 8601 in UTC, as YYYY-MM-DDTHH:MMZ. Google Cloud reports use US/Pacific; AWS reports name PDT or PST; Azure reports use UTC. Convert with the daylight-saving rule of the date.
6. `start_utc`: the first moment of customer impact the report states. `start_precision`: minute, hour or day, the finest unit the report gives.
7. `end_utc` and `end_basis`: the moment customer impact ended or service was restored for most customers (impact_ended); else the mitigation time (mitigated); else the time everything was resolved (resolved). Backlog processing after impact ended is not part of the event.
8. `region_starts`: only when the report gives a different start for some region, as region=time pairs joined by ";".
9. `services_n`: the number of distinct products or services the report names as impaired.
10. `evidence`: for the start, the end and the regions, the report section and a paraphrase in your own words, at most 25 words each. Copy no sentence from the report.
