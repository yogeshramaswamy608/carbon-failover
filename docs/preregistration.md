# Preregistration: Carbon-Aware Failover Without Losing Reliability

Study 2 of Yogesh Ramaswamy (Independent Researcher, Sunnyvale, California, United States). Target journal: IEEE Transactions on Cloud Computing.

Written on Sun Nov 15, 2026 (Pacific time) as version 1. It is frozen after one independent review, by the commit that adds `prereg_hashes.txt`, which records the SHA-256 of this file and of `docs/event_codebook.md`.

## 1. What is frozen

The research questions, hypotheses, data rules, model, policies, scenarios, outcomes, analysis, test bed protocol, seeds and budget below are fixed before any failover policy is run on any outage event.

Data preparation may run after the freeze, because it produces no outcome: coding the outage events, building the region table and building the hourly carbon tables. It follows the rules fixed here.

Any change after the freeze is written to `docs/deviations.md` with its date, its reason and its effect on the results, before the affected run. Nothing changes silently.

## 2. Research questions and hypotheses

RQ1. How much carbon does a carbon-aware failover save compared with a nearest-region failover?

RQ2. What does a carbon-aware failover cost in recovery time, in service level objective (SLO) breach and in exposure to a correlated second failure?

RQ3. Which settings of a budget-bounded policy keep reliability within a stated budget while they still save carbon?

H1. The lowest-carbon policy and the budget-bounded policy at its primary setting each emit less carbon than the nearest-region policy on the same events (median paired difference above zero).

H2. The lowest-carbon policy has a longer recovery time and more exposure to correlated failure than the nearest-region policy. The budget-bounded policy at its primary setting does not differ from the nearest-region policy in recovery time.

H3. Some settings of the budget-bounded policy keep at least 95 percent of events within their recovery-time budget while their median carbon saving stays above zero.

Every test is two-sided. A direction in H1 to H3 is the expectation, not the test.

## 3. Data

### 3.1 Outage events

Source: the companion corpus of 497 public post-incident reports (dataset DOI 10.5281/zenodo.23973151), the same corpus as study 1.

Providers kept: Amazon Web Services (AWS, 18 reports), Microsoft Azure (81 reports) and Google Cloud (172 reports). Cloudflare (42 reports) and GitHub (184 reports) are excluded at the start, because their customers do not choose a provider region to run in, so a regional failover decision does not exist for them. Their counts are reported.

Each kept report is coded under `docs/event_codebook.md`. A report gives one event. An event that impairs several named regions gives one event-home instance per impaired region: that region is the home, and the other impaired regions are the event's impaired set for that instance.

An event-home instance enters the primary analysis when all six rules hold:

1. The report names the region, or a zone inside it, where customer-facing service was impaired.
2. Its scope is regional or multi-region. Zonal events (one zone of a region, the rest serving) and global events (all regions of the affected service) leave the policy comparison and are counted.
3. The impairment lasted 30 minutes or more.
4. The report gives the start time to the hour or better. A report that gives only the day stays in, with a start hour drawn from the seeded stream of section 10, and is flagged.
5. The home region lies in the United States or in a European country the carbon sources of section 3.2 cover.
6. Hourly carbon intensity exists for the home region and for every candidate destination for every hour of the event window.

Each exclusion is counted by its rule, in this order, and the counts are reported.

Coding method: a script reads the fields that a report states in a fixed form (the Google Cloud lines that give when the incident began and ended, and the locations affected; the Azure lines that give the impact window in UTC). The language model codes every remaining field from the report text, with a one-line evidence note in its own words. The author then codes a blind random sample of 20 event-home instances from the reports alone (section 10 gives the seed). Agreement is reported per field: start and end within 15 minutes, impaired region set an exact match. A field with agreement under 80 percent gets one codebook revision and is recoded for all events, once. The author's code stands wherever the two differ in the sample.

Report text is used only to code. It is not stored in this repository and is not released. The release carries each report's link and the coded fields, as study 1 does.

### 3.2 Carbon intensity

Signal: hourly average production-based carbon intensity of each grid zone, in grams of carbon dioxide equivalent per kilowatt-hour (gCO2eq/kWh). Intensity is generation by fuel times a lifecycle emission factor, divided by total generation, over fuels with positive generation, with storage output excluded and imports not traced.

Factors: the lifecycle medians of IPCC AR5 Working Group III, Annex III, Table A.III.2, as in `src/cfo/factors.py`. Fuels that a source lists and the file lacks (for example biomass, offshore wind and lignite) are added from the same table before any run. A fuel the table does not list is marked ASSUMED in that file and varied in the sensitivity runs. One factor set serves every zone, so every zone is measured the same way.

Sources, all reached without a key:

1. United States: the U.S. Energy Information Administration Form EIA-930 six-month balance files, one zone per balancing authority, through `scripts/fetch_eia930.sh` and `cfo.eia`. The first half-year file that carries generation by fuel is found by script and reported.
2. Great Britain: the generation mix of the National Energy System Operator (NESO) Carbon Intensity API, under the Creative Commons Attribution 4.0 (CC BY 4.0) license, with the same factors. NESO's own published forecast is used only in the forecast sensitivity run.
3. Other European countries: the public power generation by type of Energy-Charts (Fraunhofer Institute for Solar Energy Systems), CC BY 4.0, with the same factors.

All times are UTC. Readings finer than one hour are averaged to the hour, weighted by generation. A missing hour is not filled: the instance fails rule 6 of section 3.1.

### 3.3 Regions, candidates and latency

Region table: every general-purpose region of the three providers in the United States or in a covered European country, with its metro area from the provider's own region documentation (the page and the date read are kept per row). Government, sovereign and restricted-access regions are left out.

Grid zone: in the United States, the EIA balancing authority whose area serves the region's metro, with the source kept per row; in Great Britain, the NESO national zone; elsewhere in Europe, the country. The table is fixed before the runs.

Candidate destinations of a home region: the same provider's other regions in the same geography (United States, or Europe with Great Britain), within the latency bound below. Crossing geographies is out, as data residency usually requires.

Latency: the added round-trip time between two regions is 2 x great-circle distance x a route factor of 1.5, divided by 200,000 kilometres per second in fibre, plus 2 milliseconds. The model is checked against Microsoft's published Azure inter-region round-trip table where it can be read, and its median absolute error is reported. The latency bound is 50 milliseconds of added round-trip time.

## 4. Model and parameters

A service with an information technology (IT) load of 1 megawatt runs in its home region. At the event start the home region fails for the event's duration. The policy picks a destination at the decision time, which is the start plus the detection time, and the load moves there. Recovery time is detection, plus traffic steering, plus scale-up when the destination lacks headroom, plus making the data serve writes there. When the destination lies in the event's impaired set, it fails after the move, and the service fails over again to the policy's next choice, adding one more recovery each time. Carbon is the load times the power usage effectiveness (PUE) times the destination's hourly intensity, summed over the hours the destination serves, from the decision time to the end of the outage. After the outage the load returns home under every policy, so that part is equal and not counted.

| Parameter | Primary value | Sensitivity values | Basis |
|---|---|---|---|
| Detection time | 5 minutes | 1 and 15 minutes | ASSUMED, an automated detection and decision |
| Traffic steering time | 1 minute | measured on the test bed | ASSUMED, a 60-second DNS time to live |
| Data promotion, replica present | 2 minutes | 1 and 10 minutes | ASSUMED |
| Data restore, no replica | 60 minutes | 30 and 240 minutes | ASSUMED |
| Scale-up round | 3 minutes, adding 25 percent of the displaced load | 1 and 10 minutes | ASSUMED, node start and readiness |
| PUE | 1.2 in every region | 1.1 and 1.5 | ASSUMED; equal PUE cancels in relative savings |
| Route factor | 1.5 | 1.2 and 2.0 | ASSUMED, checked against the Azure table |
| Latency bound | 50 milliseconds added round trip | 30 and 80 milliseconds | ASSUMED |
| Minimum event duration | 30 minutes | 15 and 60 minutes | ASSUMED |

## 5. Policies

All policies choose among candidates that are healthy at the decision time. A policy does not know the impaired set in advance.

Nearest-region: the candidate with the smallest added latency, with load that exceeds its headroom spilling to the next.

Lowest-carbon: the candidate within the latency bound with the lowest forecast intensity.

Budget-bounded: the candidate within the latency bound with the lowest forecast intensity among those that meet three bounds, else the nearest-region choice. The bounds: estimated recovery time at most beta times the nearest-region recovery time; load at most (1 + kappa) times the destination's headroom; estimated probability of failing together with the home region at most epsilon.

Primary setting: beta 1.0, kappa 0, epsilon 0.05. Grid for RQ3: beta 1.0, 1.25, 1.5 and 2.0; kappa 0 and 0.5; epsilon 0, 0.05, 0.10 and 1.0 (no bound).

Correlated-failure estimate: for each same-provider pair, the share of earlier event-home instances at that home whose impaired set held the destination, shrunk toward the provider's earlier base rate with a weight of 10 instances. Only events that started before the event at hand are used. With fewer than 5 earlier events for the provider, the base rate pools all three providers; with none, it is 0.05 (ASSUMED).

Baselines: a random healthy candidate within the latency bound (sanity), and an oracle that knows the impaired set and the realized intensity and picks the lowest-carbon destination within the same bounds (upper bound).

Forecasts: persistence, the intensity at the decision hour held for the whole window (primary, available in every zone); oracle, the realized intensity (bound); NESO's published forecast (Great Britain only, sensitivity).

## 6. Scenarios

Primary scenario: flat load, full headroom at every destination, a data replica in every candidate, persistence forecast, and the primary values of section 4.

Secondary factors, each crossed with the policies: headroom for half the displaced load; a data replica only in the nearest region; a diurnal load of plus or minus 30 percent around the mean, peaking at 2pm local time of the home region; the oracle forecast.

## 7. Outcomes

Primary, per event-home instance, each policy against the nearest-region policy on the same instance:

1. Carbon saved, in kilograms of carbon dioxide equivalent per megawatt, and as a share of the nearest-region carbon (RQ1).
2. Recovery-time cost, in minutes (RQ2).
3. Correlated-failure exposure: whether the chosen destination was in the impaired set (RQ2).

Secondary: SLO breach minutes (unavailable minutes plus minutes served beyond the latency bound) and their share of a monthly error budget at 99.95 percent availability (21.9 minutes); decision regret (the carbon gap between the persistence choice and the oracle choice); the absolute carbon per outage hour.

## 8. Analysis

Unit: the event. The paired differences of an event's instances are averaged, so an event with several impaired regions counts once.

Primary tests: the Wilcoxon signed-rank test on the event-level paired differences for six comparisons (lowest-carbon and budget-bounded, each against nearest-region, on carbon saved, recovery-time cost and exposure), with the Holm correction across the six. Each comes with the median paired difference, a 95 percent bootstrap confidence interval from 10,000 resamples of events, and the matched-pairs rank-biserial correlation.

Minimum sample: with fewer than 30 events in the primary analysis, the results are reported as descriptive statistics only, with no tests, and the study's Fri Dec 18, 2026 checkpoint decides whether the paper goes ahead.

RQ3: the frontier of median carbon saved against the share of events within budget, across the grid of section 5, in each scenario. An event is within budget when its recovery-time cost is at most (beta minus 1) times the nearest-region recovery time and it needed no second failover.

Hour analysis: each event is replayed at every hourly start of its own calendar year, with its duration and impaired set kept. It shows how much of the saving depends on the hour. It adds no independent failures and enters no test.

Sensitivity runs: every value in the sensitivity column of section 4; the ASSUMED factors varied from the lowest to the highest median of the table; date-only events removed; events naming two or more services only; correlated and isolated events separately. None replaces a primary result.

## 9. Test bed check of the recovery model

Setup: three single-node kind clusters (Kubernetes in Docker) for the home, a near and a far region, on one standard GitHub-hosted Linux runner of a public repository (4 processors, 16 gigabytes, per GitHub's documentation read on Sun Nov 15, 2026). An Envoy proxy with active health checks steers a fixed request rate to the home cluster. Network delay to each cluster is set with Linux traffic control to the model's latency for its pair.

Run: after a steady minute, the home cluster's node container is stopped. Two destinations (near and far) and two headroom levels (full, and half with a scripted scale-up) give four cells, with 10 repeats each from the same starting state.

Measures: detection (failure to ejection of the home upstream), steering (ejection to 99 percent of requests served at the destination), scale-up (steering to the added replicas ready), and recovery (failure to the first 10-second window with 99.9 percent success and latency within the bound). Each is reported as a median and interquartile range over the repeats.

Comparison rule: a modeled term is compared with its measured median. When the gap exceeds the measured interquartile range, the evaluation is rerun with the measured value, and both results are reported. Node start and data promotion cannot be reproduced on kind; they stay ASSUMED and are said so.

## 10. Seeds and reproducibility

Master seed: the text "20261115:carbon-failover". Each random stream takes the first 8 bytes of the SHA-256 of the master seed joined with its name by a colon: "start-hour", "random-policy", "bootstrap" and "author-sample".

Every run writes a record with its configuration, the commit, the seed of each stream and the SHA-256 of every input file, so that every figure can be rebuilt from the release.

## 11. Budget

No paid model call: the pipeline calls no language model, and the event coding by the language model happens in the author's assistant sessions. Compute: GitHub Actions on standard runners of this public repository, free under GitHub's billing terms read on Sun Nov 15, 2026. No cloud spend. Data: free public sources only.

## 12. Roles and assistance

The author designed the study, runs and checks every experiment, codes the blind sample of section 3.1, and owns every claim. A language model from Anthropic (Claude Opus 5.5) drafted this text and the code and coded the outage events under the codebook, as declared in the paper.

## 13. Data and licenses

Code: Apache License 2.0 (`LICENSE`). Data the author creates (the coded events, the region table, the results): CC BY 4.0. Third-party data keeps its own license: EIA data is in the public domain; NESO and Energy-Charts data are CC BY 4.0 and credited. Report text is never redistributed.
