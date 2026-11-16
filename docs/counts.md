# Counts

Section 8 of the preregistration fixes the number of events in the primary analysis after data preparation and before any policy run. Data preparation ends with the author's blind check of section 3.1, which can lead to one codebook revision and a recode. So the counts below are the state before that check. They are fixed, with their date, once the check is done, and no policy has been run.

## State of Mon Nov 16, 2026, before the author's blind check

Reports kept: 271 (AWS 18, Azure 81, Google Cloud 172). Coded: 270. Not coded: 1 (corpus P9, an Azure review of Nov 12, 2021 that the Azure history page no longer holds; Azure keeps reviews 5 years).

Events after merging reports of one incident: 256 (12 merges, `dataset/merges.csv`). Event-home instances: 1,795.

Exclusions in the order of section 3.1. An instance counts at the first rule it fails. An event counts at the furthest rule any of its instances reached; an event that names no region counts at rule 1.

| Rule | Text | Instances excluded | Events excluded |
|---|---|---|---|
| 1 | region named | 0 | 65 |
| 2 | regional or multi-region scope | 1285 | 68 |
| 3 | lasted 30 minutes or more | 20 | 6 |
| 4 | start to the hour, or day with duration | 0 | 0 |
| 5 | home in the region table | 218 | 25 |
| 6 | two or more candidates | 8 | 8 |
| 7 | hourly carbon for every candidate | 11 | 3 |
| kept | meets all seven rules | 253 | 81 |

Events in the primary analysis: 81 (instances 253; Google Cloud 160 instances, Azure 93, AWS 0). This is 30 or more, so the tests of section 8 apply once the count is fixed.

Region table: 58 general-purpose regions, 57 used. Azure West US is left out of the candidate sets because no public source names the place of its data centres, so its grid zone is not established (section 3.3).

The decision to go on to a paper is made on the fixed count, before any policy run.
