# Counts

Section 8 of the preregistration fixes the number of events in the primary analysis after data preparation and before any policy run. Data preparation ends with the author's blind check of section 3.1, which can lead to one codebook revision and a recode. So the counts below are the state before that check. They are fixed, with their date, once the check is done, and no policy has been run.

## The author's blind check, Thu Nov 19, 2026

The author coded the 30 reports of `dataset/author_sample.csv` from each report alone, on a private page, from Thu Nov 19, 2026, 1:39pm Pacific, to Thu Nov 19, 2026, 5:06pm Pacific (`dataset/author_check.csv`). Agreement with the coded rows, per field (section 3.1):

| Field | Agree | Share | Under 80 percent |
|---|---|---|---|
| Scope | 23 of 30 | 76.7 percent | yes |
| Impaired region set | 28 of 30 | 93.3 percent | no |
| Start, within 15 minutes | 24 of 30 | 80.0 percent | no |
| End, within 15 minutes | 20 of 30 | 66.7 percent | yes |

Where the codes differ, the author's code stands; the 30 rows of `dataset/coded.csv` carry his codes (`coded_by` author). Scope and end are under 80 percent, so section 3.1 now requires one codebook revision for each, a full recode of each, and a fresh sample from the "author-sample" stream (10 Azure, 10 Google Cloud and the 8 AWS reports left), whose agreement is reported whatever it shows. Of the 7 scope differences, 4 are AWS reports the model coded zonal and the author regional (one zone failed and region-wide calls failed with it); of the 10 end differences, 7 are AWS reports where the author found no single end of customer impact and left it empty.

## State after the codebook revision and recode, Thu Nov 19, 2026 (not fixed: the author's check of the fresh sample comes first)

Codebook version 2 and the recode of scope and end (`docs/deviations.md`, deviation 3), with the author's codes standing for his 30 reports. Report 79 keeps its version 1 codes (its Azure review was gone that day); P9 stays uncoded.

Events: 259 (10 merges). Event-home instances: 1,800.

| Rule | Text | Instances excluded | Events excluded |
|---|---|---|---|
| 1 | region named | 0 | 65 |
| 2 | regional or multi-region scope | 1289 | 59 |
| 3 | lasted 30 minutes or more | 28 | 16 |
| 4 | start to the hour, or day with duration | 0 | 0 |
| 5 | home in the region table | 218 | 28 |
| 6 | two or more candidates | 1 | 1 |
| 7 | hourly carbon for every candidate | 11 | 3 |
| kept | meets all seven rules | 253 | 87 |

Events that meet all seven rules: 87 (instances 253; Google Cloud 156, Azure 97, AWS 0). Rule 3 counts an instance with no end and no stated duration as failing, so an AWS report that states no end of customer impact leaves the analysis there.

The fresh sample of section 3.1: 28 reports drawn by the "author-sample" stream on Thu Nov 19, 2026, continuing after the first 30 (the first draw reproduced exactly): the 8 AWS reports left, 10 Azure and 10 Google Cloud (`dataset/author_sample_2.csv`). The author codes scope and end from each report alone.

## State after the author's codes, Thu Nov 19, 2026 (not fixed: the revision and recode of scope and end come first)

Events: 258 (11 merges). Event-home instances: 1,800.

| Rule | Text | Instances excluded | Events excluded |
|---|---|---|---|
| 1 | region named | 0 | 64 |
| 2 | regional or multi-region scope | 1279 | 64 |
| 3 | lasted 30 minutes or more | 29 | 15 |
| 4 | start to the hour, or day with duration | 0 | 0 |
| 5 | home in the region table | 223 | 27 |
| 6 | two or more candidates | 4 | 4 |
| 7 | hourly carbon for every candidate | 11 | 3 |
| kept | meets all seven rules | 254 | 81 |

Events that meet all seven rules: 81 (instances 254).

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
