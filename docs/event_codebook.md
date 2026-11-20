# Event codebook, version 2

For the study "Carbon-Aware Failover Without Losing Reliability". Written on Sun Nov 15 and Mon Nov 16, 2026 (Pacific time) and frozen with `docs/preregistration.md`. Changed only as section 3.1 of the preregistration allows, and logged in `docs/deviations.md`.

Version 2, Thu Nov 19, 2026: the one revision section 3.1 allows for `scope` (section 3) and for `end_utc` and `end_basis` (sections 5 and 7), after the author's blind check put both fields under 80 percent agreement. Every other rule is as in version 1 (commit d2a9a50). Section 9 lists the changes.

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

Code the scope from what the report says was impaired for customers, including the provider's region-wide operations (launching or creating resources, API and management calls), not only from where the fault began.

zonal: the impact stayed in one named zone. The report names one zone and says nothing of impact outside it, or says the region's other zones and its region-wide operations kept serving.

regional: one region is impaired beyond one zone: in more than one zone, as a whole, or in its region-wide operations. A fault that began in one zone is regional when the report says customers in other zones of that region, or the region's launch, API or management calls, were impaired.

multi_region: two or more regions are impaired, and the report does not say that all regions of the provider's public cloud were. This includes a report that says "multiple regions" or "several regions" without naming them (`regions` left empty, the reason in `notes`), a Google Cloud multi-region or dual-region location such as `us`, `eu` or `nam5`, and "all regions" of a separate or sovereign cloud (Azure Government, Azure China) or of one named geography, whose regions the report names or lists.

global: the report says the impact was global, worldwide, or in all regions of the provider's public cloud for the affected service, lists the location Global, or names every region of the provider.

unclear: the report names no region and gives no word on how many regions were impaired.

A report that names one zone and gives no word on anything outside it is coded zonal, with that fact in `notes`.

## 4. Regions and time zones

Regions are written as the provider's own region code: AWS as `us-east-1`; Azure as the programmatic name, `eastus` for "East US"; Google Cloud as `us-central1`. A zone is written as its code (`us-central1-a`) and its region is added to `regions`.

Google Cloud also lists locations that are not regions: Global, and multi-region or dual-region locations such as `us`, `eu` or `nam5`. Global sets `scope` to global. A multi-region or dual-region location adds no region code and is named in `notes`.

Time zones: Google Cloud incident reports give times in US/Pacific; AWS reports name PDT or PST beside each time; Azure post-incident reviews give UTC. Every time is converted to UTC with the daylight-saving rule of its date (the IANA zone America/Los_Angeles for Pacific time).

## 5. End of the event

The end is a moment the report itself states as the end of customer impact for the event as a whole: for example, the time the report says the event finished, all affected services returned to normal, the incident ended, or the issue was resolved for all affected users. Its basis is `impact_ended` when the statement is that impact ended or service was restored, `mitigated` when it is only that the event was mitigated, and `resolved` when it is only that everything was fully resolved.

The coder does not build an end from parts. Recovery times given service by service, or a statement that most customers or most resources had recovered, are not the end when the report says other services, customers or a zone stayed impaired after them. A stated moment is not the end when the report says customer impact went on after it; the next whole-event statement after it is taken, if there is one.

When the report states no such moment, `end_utc` and `end_basis` are left empty, with the reason in `notes`. A tail of backlog processing is outside the event only when the report states that customer impact had ended before it.

Google Cloud: a page that carries an incident report (a Mini Incident Report or a full Incident Report) gives the end in its own "Incident End" line, which is taken over the "ended at" time of the dashboard's header. When the page holds more than one report, the newest report that carries such a line is read (normally the full Incident Report); when that report gives several impact windows, the end is the latest of them. A date in that line that contradicts the dated updates of the same page (an "Incident End" before the header's "Incident began" time) is read from the page's dated updates, and the reason is written in `notes`. A page with no "Incident End" line takes the header's "ended at" time, unless the page says customer impact went on after it.

## 6. Merging reports of one incident

Reports of one provider whose impact windows overlap form one event when their region sets share a region, or when both are global. The event takes the union of their regions, the earliest start, the latest end and the widest scope among them, and it is multi_region when the union holds two or more regions and no report is global. Each merge is logged with the corpus numbers it joins.

## 7. Script and model

The script sets the fields a report states in a fixed form: the Google Cloud line that says when the incident began, the locations affected, and the end in the incident report's "Incident End" line (section 5; from version 2), and the Azure lines that give the impact window in UTC. For a Google Cloud page with no "Incident End" line, or one whose line is before the header's begin time, the script sets no end and the model codes it. The language model codes every report in batches of at most 10, each batch in a fresh session that holds only `docs/coding_prompt.md` and those reports' text. Each output is kept in `logs/coding/` with the model, its version and the date. Where the script and the model both set a field and differ, the script's value stands, since it copies the report's own line, and the difference is logged. Each row records who set its time and region fields.

## 8. The author's blind check

The author codes 30 reports, 10 per provider, drawn by the "author-sample" stream of the preregistration from the 271 kept reports. The author codes `scope`, `regions`, `start_utc` and `end_utc` from each report alone, without seeing the coded row. Agreement is counted per field: scope and the region set an exact match, times within 15 minutes. The rule of section 3.1 of the preregistration then applies, and the author's codes are released with the data.

## 9. Changes in version 2, Thu Nov 19, 2026

Why: the author's blind check of 30 reports (`dataset/author_check.csv`) agreed with the coded rows on 23 of 30 scopes and 20 of 30 ends. Section 3.1 of the preregistration then requires one revision of each field, a full recode of each, and a fresh sample.

Scope (section 3): version 1 coded zonal any report that named one zone. The author coded regional four AWS reports where one zone failed and region-wide calls failed with it; version 2 makes region-wide operations count. He coded multi_region a report that says "multiple regions" without names, a BigQuery US multi-region report, and an Azure Government report that says all regions of that cloud; version 1 gave unclear, unclear and global. Version 2 writes those three readings into the rule.

End (sections 5 and 7): version 1 took "restored for most customers" as the end and let the Google Cloud dashboard header set it. The author left the end empty for every AWS report of his sample (no single end of customer impact stated) and for two Google Cloud pages that say impact went on after the header's end, and took a Mini Incident Report's "Incident End" over the header in a third. Version 2 takes only a stated whole-event end, and for Google Cloud the incident report's own line.

Unchanged: the unit, every other field and its rule, regions and time zones, merging, the model's batches and logs, and the author's check. The author's codes stand for his 30 reports.
