# Event codebook, version 1

For the study "Carbon-Aware Failover Without Losing Reliability". Written on Sun Nov 15 and Mon Nov 16, 2026 (Pacific time) and frozen with `docs/preregistration.md`. Changed only as section 3.1 of the preregistration allows, and logged in `docs/deviations.md`.

## 1. Unit

One row per kept report of the companion corpus (AWS, Azure and Google Cloud; section 3.1 of the preregistration). The row keeps the corpus number, the report's link and the coded fields. No report text is kept.

Code only what the report states. A field the report does not support is left empty with the reason in `notes`, never guessed.

## 2. Fields

| Field | Values | Rule |
|---|---|---|
| `corpus_no` | 1 to 447, or P1 to P50 | From the corpus, as the corpus writes it. |
| `provider` | aws, azure, gcp | From the corpus source. |
| `published_utc` | ISO 8601 date in UTC | The report's own publication date. When the report shows none, the end plus 14 days, flagged in `notes`. |
| `scope` | zonal, regional, multi_region, global, unclear | Section 3. |
| `regions` | provider region codes, separated by ";" | Every region the report names as impaired, normalized under section 4. |
| `zones` | zone codes, separated by ";" | Only when the report names zones. |
| `start_utc` | ISO 8601 in UTC | The first moment of customer impact the report states. |
| `start_precision` | minute, hour, day | The finest unit the report gives for the start. |
| `end_utc` | ISO 8601 in UTC | Section 5. |
| `end_basis` | impact_ended, mitigated, resolved | Section 5. |
| `duration_min` | integer | Only when the report states how long the impact lasted and gives no start and end pair. |
| `region_starts` | region=ISO time pairs, separated by ";" | Only when the report gives a different start for some region. |
| `services_n` | integer | The number of distinct products or services the report names as impaired. |
| `evidence` | text, at most 25 words per field | The report section and a paraphrase in our own words for the start, the end and the regions. |
| `coded_by` | script, model, author | Who set the row's time and region fields. |
| `notes` | text | Anything a reader needs, such as an empty field's reason. |

## 3. Scope

zonal: the report names one zone of a region and says or shows that the region's other zones kept serving.

regional: one region is impaired across more than one zone, or as a whole.

multi_region: two or more named regions are impaired, and the report does not say that all regions were.

global: the report says the impact was global, worldwide or in all regions for the affected service, lists the location Global, or names every region of the provider.

unclear: the report gives no region, or says "multiple regions" without naming them.

A report that names one zone and gives no word on the other zones is coded zonal, with that fact in `notes`.

## 4. Regions and time zones

Regions are written as the provider's own region code: AWS as `us-east-1`; Azure as the programmatic name, `eastus` for "East US"; Google Cloud as `us-central1`. A zone is written as its code (`us-central1-a`) and its region is added to `regions`.

Google Cloud also lists locations that are not regions: Global, and multi-region or dual-region locations such as `us`, `eu` or `nam5`. Global sets `scope` to global. A multi-region or dual-region location adds no region code and is named in `notes`.

Time zones: Google Cloud incident reports give times in US/Pacific; AWS reports name PDT or PST beside each time; Azure post-incident reviews give UTC. Every time is converted to UTC with the daylight-saving rule of its date (the IANA zone America/Los_Angeles for Pacific time).

## 5. End of the event

The end is the moment the report says customer impact ended, or the service was restored for most customers (`impact_ended`). When the report gives only a mitigation time, that is the end (`mitigated`). When it gives only the time everything was fully resolved, that is the end (`resolved`). A tail of backlog processing after impact ended is not part of the event.

## 6. Merging reports of one incident

Reports of one provider whose impact windows overlap form one event when their region sets share a region, or when both are global. The event takes the union of their regions, the earliest start, the latest end and the widest scope among them, and it is multi_region when the union holds two or more regions and no report is global. Each merge is logged with the corpus numbers it joins.

## 7. Script and model

The script sets the fields a report states in a fixed form: the Google Cloud lines that say when the incident began and ended and the locations affected, and the Azure lines that give the impact window in UTC. The language model codes every report in batches of at most 10, each batch in a fresh session that holds only `docs/coding_prompt.md` and those reports' text. Each output is kept in `logs/coding/` with the model, its version and the date. Where the script and the model both set a field and differ, the script's value stands, since it copies the report's own line, and the difference is logged. Each row records who set its time and region fields.

## 8. The author's blind check

The author codes 30 reports, 10 per provider, drawn by the "author-sample" stream of the preregistration from the 271 kept reports. The author codes `scope`, `regions`, `start_utc` and `end_utc` from each report alone, without seeing the coded row. Agreement is counted per field: scope and the region set an exact match, times within 15 minutes. The rule of section 3.1 of the preregistration then applies, and the author's codes are released with the data.
