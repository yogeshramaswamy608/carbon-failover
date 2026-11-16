# Preregistration: Carbon-Aware Failover Without Losing Reliability

Study 2 of Yogesh Ramaswamy (Independent Researcher, Sunnyvale, California, United States).

Written on Sun Nov 15 and Mon Nov 16, 2026 (Pacific time) as version 1. It is frozen by the last commit that adds `prereg_hashes.txt`, which records the SHA-256 of this file, `docs/event_codebook.md`, `docs/coding_prompt.md` and `src/cfo/factors.py`. The same four files are deposited on Zenodo on the day of that commit, and the deposit's date is the freeze date.

## 1. What is frozen

The research questions, hypotheses, data rules, model, policies, scenarios, outcomes, analysis, test bed protocol, seeds and budget below are fixed before any failover policy is run on any outage event.

Data preparation may run after the freeze, because it produces no outcome: coding the outage events, building the region table and building the hourly carbon tables. It follows the rules fixed here.

What existed at the freeze: the outage corpus had been read and coded for study 1, for trigger and fault classes only, and its coded fields hold the day of each incident and no region, start time or end time. The code that turns EIA-930 files into hourly carbon intensity had been written and tested. No outage of this study had been coded, so no carbon value had been joined to an outage, and no simulator, failover run or policy outcome existed. A first freeze commit of the same night (8194cba, 12:50am Pacific) was withdrawn before the deposit and before any data preparation, to take six corrections from a further independent review. The files deposited on Zenodo are those of the final freeze commit.

Any change after the freeze is written to `docs/deviations.md` with its date, its reason and its effect on the results, before the affected run. Nothing changes silently.

## 2. Research questions and hypotheses

RQ1. How much carbon does a carbon-aware failover save compared with a nearest-region failover?

RQ2. What does a carbon-aware failover cost in exposure to a correlated second failure, in recovery time and in service level objective (SLO) breach?

RQ3. Which settings of a budget-bounded policy keep reliability within a stated budget while they still save carbon?

H1. The lowest-carbon policy and the budget-bounded policy at its primary setting each emit less carbon than the nearest-region policy on the same events (paired differences shifted above zero).

H2. The lowest-carbon policy is exposed to correlated failure more often than the nearest-region policy. The budget-bounded policy at its primary setting is expected to stay close to the nearest-region policy.

H3. Some settings of the budget-bounded policy keep at least 95 percent of events within the budget of section 8 while their mean carbon saving stays above zero.

Every test is two-sided. A direction in H1 to H3 is the expectation, not the test.

## 3. Data

### 3.1 Outage events

Source: the companion corpus of 497 public post-incident reports (dataset DOI 10.5281/zenodo.23973151), the corpus of study 1.

Providers kept: Amazon Web Services (AWS, 18 reports), Microsoft Azure (81 reports) and Google Cloud (172 reports), 271 reports in all. Cloudflare (42 reports) and GitHub (184 reports) are excluded at the start, because their customers do not choose a provider region to run in, so a regional failover decision does not exist for them. Their counts are reported.

Each kept report is coded under `docs/event_codebook.md`. Reports of one provider whose impact windows overlap form one event when their region sets share a region, or when both are global. The event takes the union of their regions, the earliest start, the latest end and the widest scope among them, and it is multi-region when the union holds two or more regions and no report is global. Each merge is logged.

An event that impairs several named regions gives one event-home instance per impaired region: that region is the home, and the other impaired regions are the impaired set of that instance. An instance starts at its home's own start when the codebook records one (`region_starts`), else at the event start, and it ends at the event end.

An event-home instance enters the primary analysis when all seven rules hold:

1. The report names the region, or a zone inside it, where customer-facing service was impaired.
2. The event's scope is regional or multi-region. Zonal events (one zone of a region, the rest serving) and global events (all regions of the affected service) leave the policy comparison and are counted.
3. The instance lasted 30 minutes or more.
4. The report gives the start to the hour or better, or gives the day together with the duration. A start known only to the day gets an hour drawn uniformly by the "start-hour" stream of section 10 from the 24 hours of that day in the report's own time zone; the end follows from the duration, and the instance is flagged.
5. The home region is in the region table of section 3.3.
6. The home has two or more candidate destinations at the instance start (section 3.3). With one candidate every policy makes the same choice, so no decision exists.
7. Hourly carbon intensity exists for every candidate destination for every hour of the instance's window and for the hour before it, which the persistence forecast of section 5 reads at the first decision.

Each exclusion is counted by its rule, in this order, and the counts are reported. The primary analysis holds every event with at least one instance that meets all seven rules.

Coding method: a script sets the fields that a report states in a fixed form (the Google Cloud lines that give when the incident began and ended and the locations affected, and the Azure lines that give the impact window in UTC). The language model codes every report in batches of at most 10, each batch in a fresh session that holds only the frozen prompt `docs/coding_prompt.md` and those reports' text. Each output is kept in `logs/coding/` with the model, its version and the date, and is released without report text. Where the script and the model both set a field and differ, the script's value stands, since it copies the report's own line, and the difference is logged.

The author's blind check: the author codes 30 reports, 10 per provider, drawn by the "author-sample" stream of section 10 from the 271 kept reports, working from each report alone, without the coded rows. Agreement is counted per field: scope and the impaired region set must match exactly, start and end must fall within 15 minutes. A field under 80 percent agreement gets one codebook revision, a full recode of that field and a fresh sample from the same stream (10 per provider from the reports not drawn before, and the 8 that are left for AWS), whose agreement is reported whatever it shows. Where the two codes differ in a sample, the author's code stands. The author's codes are released with the data.

Report text is used only to code. It is not stored in this repository and is not released. The release carries each report's link and the coded fields, as study 1 does.

### 3.2 Carbon intensity

Signal: hourly average production-based carbon intensity of each grid zone, in grams of carbon dioxide equivalent per kilowatt-hour (gCO2eq/kWh). Intensity is generation by fuel times a lifecycle emission factor, divided by total generation, over fuels with positive generation. Storage output is excluded; where a source reports hydro and pumped storage in one column, it counts as hydro, and the paper says so. Imports are not traced. Carbon here is attributional, computed from average intensity; it is not the marginal emissions caused by moving the load.

Factors: `src/cfo/factors.py` is frozen with this file. It holds one value for every fuel label that the three sources showed when they were read on Mon Nov 16, 2026 (the EIA-930 files of July to December 2018 and January to June 2026, the NESO generation mix, and the Energy-Charts public power series of 14 countries), and the table that maps each label to its value. The values are the lifecycle medians of IPCC AR5 Working Group III, Annex III, Table A.III.2, read on the table itself that day, where the table lists the fuel; every other value is marked ASSUMED in the file. A label the file does not hold stops the build, and is added with its value by an entry in `docs/deviations.md`. One factor set serves every zone, so every zone is measured the same way.

Sources, all reached without a key:

1. United States: the U.S. Energy Information Administration Form EIA-930 six-month balance files, one zone per balancing authority, through `scripts/fetch_eia930.sh` and `cfo.eia`. The files carry generation by fuel from July 2018; the file of January to June 2018 has none.
2. Great Britain: the generation mix of the National Energy System Operator (NESO) Carbon Intensity API, under the Creative Commons Attribution 4.0 (CC BY 4.0) license, with the same factors. Imports are removed from the mix, the remaining shares are rescaled to 100 percent, and the two half-hours of an hour get equal weight. NESO's own published forecast is used only in the forecast sensitivity run.
3. Other European countries: the public power generation by type of Energy-Charts (Fraunhofer Institute for Solar Energy Systems), CC BY 4.0, with the same factors.

All times are UTC, and every hourly value is labelled by the start of its hour in UTC. Readings finer than one hour are averaged within the hour, weighted by generation where generation is given. A missing hour is not filled: the instance fails rule 7 of section 3.1.

### 3.3 Regions, candidates and latency

Region table: every general-purpose region of the three providers in the United States, in Great Britain or in a European country of the Energy-Charts country list, with its metro area from the provider's own region documentation and its general-availability date from the provider's own announcement (the page and the date read are kept per row). Government, sovereign and restricted-access regions are left out. A region is a candidate only for instances that start after its general-availability date; a region whose date is not found is left out of the candidate sets, and the count is reported.

Grid zone: in the United States, the EIA balancing authority whose area serves the region's metro, with the source kept per row; in Great Britain, the NESO national zone; elsewhere in Europe, the country. The table is fixed before the runs.

Candidate destinations of a home region: the same provider's other regions in the same geography (the United States, or Europe with Great Britain) that lie within the latency bound below. Crossing geographies is out, as data residency usually requires.

Latency: the added round-trip time of serving from another region is modeled as the round-trip time between the two regions: 2 x great-circle distance x a route factor of 1.5, divided by 200,000 kilometres per second in fibre, plus 2 milliseconds. The model is checked against Microsoft's published Azure inter-region round-trip table where it can be read, and its median absolute error is reported. The latency bound is 50 milliseconds of added round-trip time.

## 4. Model and parameters

A service with an information technology (IT) load of 1 megawatt runs in its home region. At the instance start the home fails. The first decision time is the start plus the detection time. At each decision time the policy ranks the candidates it has not left, using the forecast of that moment, and its chosen destination takes the whole load. No policy spills load to a second destination: the destination scales up when it lacks headroom.

Recovery time is detection, plus traffic steering, plus scale-up when the destination lacks headroom, plus making the data serve writes at the destination. A destination in the impaired set fails when the recovery into it ends, or at its own start if that comes after the end of the recovery. The next decision time is that moment plus the detection time. With no candidate left, the service is unavailable until the outage ends, and the load stays assigned to its last destination. A recovery still running when the outage ends stops, and the service returns home.

Carbon counts every minute from the first decision time to the end of the outage, at the region the load is assigned to in that minute, recovery minutes included: the load times the power usage effectiveness (PUE) times that region's hourly intensity. The window is the same for every policy. After the outage the load returns home under every policy, so that part is equal and not counted.

| Parameter | Primary value | Sensitivity values | Basis |
|---|---|---|---|
| Detection time | 5 minutes | 1 and 15 minutes | Confirmed by the author against his production experience (Mon Nov 16, 2026), an automated detection and decision |
| Traffic steering time | 1 minute | 0.5 and 5 minutes | Confirmed by the author against his production experience (Mon Nov 16, 2026), a DNS time to live of 60 seconds (30 and 300 seconds) |
| Data promotion, replica present | 2 minutes | 1 and 10 minutes | Confirmed by the author against his production experience (Mon Nov 16, 2026) |
| Data restore, no replica | 60 minutes | 30 and 240 minutes | Confirmed by the author against his production experience (Mon Nov 16, 2026) |
| Scale-up round | 3 minutes, adding 25 percent of the displaced load | 1 and 10 minutes | Confirmed by the author against his production experience (Mon Nov 16, 2026), node start and readiness |
| PUE | 1.2 in every region | 1.1 and 1.5 | ASSUMED; equal PUE cancels in relative savings |
| Route factor | 1.5 | 1.2 and 2.0 | ASSUMED, checked against the Azure table |
| Latency bound | 50 milliseconds added round trip | 30 and 80 milliseconds | Confirmed by the author against his production experience (Mon Nov 16, 2026) |
| Minimum instance duration | 30 minutes | 15 and 60 minutes | Confirmed by the author against his production experience (Mon Nov 16, 2026) |

The author's confirmation covers the primary values. The sensitivity values, the PUE and the route factor are ASSUMED.

With these values every first failover in the primary scenario takes 8 minutes under every policy, so recovery-time cost there comes only from second failovers, at 8 minutes each.

## 5. Policies

A candidate is healthy for a policy unless it is the home or a region the service has already left in this instance. No policy but the oracle observes other regions' impairment. This is the worst case for correlated failure, an assumption the author confirmed on Mon Nov 16, 2026; a sensitivity run of section 8 gives the other end.

Nearest-region: the healthy candidate with the smallest added latency.

Lowest-carbon: the healthy candidate with the lowest forecast intensity.

Budget-bounded: the healthy candidate with the lowest forecast intensity among those that meet three bounds, else the nearest-region choice. Each bound is set against the nearest-region choice: estimated recovery time at most beta times the nearest-region recovery time; load at most (1 + kappa) times the destination's headroom; co-failure count at most that of the nearest-region choice plus m.

Co-failure count: for home h, destination d and decision time t, the number of the provider's regional and multi-region events that impaired both h and d and whose reports were published before the day of t. A policy therefore uses only what was public when it decides.

Primary setting: beta 1.0, kappa 0, m 0. Grid for RQ3: beta 1.0, 1.25, 1.5, 2.0 and 9.0; kappa 0, 0.5 and 1.0; m 0, 1, 2 and no bound.

Ties: equal forecast intensity goes to the smaller added latency, and equal latency to the region code that sorts first.

Baselines: a random healthy candidate (sanity, the "random-policy" stream of section 10), and an oracle that knows the impaired set and the realized intensity and picks, among the candidates outside the impaired set, the one with the lowest carbon over the window, else the nearest-region choice (upper bound).

Forecasts: persistence holds the intensity of the last hour that ended at or before the decision time for the whole window (primary, available in every zone); oracle, the realized intensity (bound); NESO's published forecast (Great Britain only, sensitivity).

## 6. Scenarios

Primary scenario: flat load, full headroom at every destination, a data replica in every candidate, persistence forecast, and the primary values of section 4.

Secondary factors, each changed alone from the primary scenario and run with every policy: full headroom in the nearest region and headroom for half the displaced load elsewhere; a data replica only in the nearest region; a diurnal load of `1 + 0.3 * cos(2 * pi * (hour - 14) / 24)` megawatts, where hour is the local hour of the home region, so the load peaks at 2pm; the oracle forecast.

## 7. Outcomes

Primary, per event-home instance, each policy against the nearest-region policy on the same instance:

1. Carbon saved, as a share of the nearest-region carbon over the same window (RQ1). The kilograms of carbon dioxide equivalent per megawatt of IT load are reported beside it.
2. Correlated-failure exposure: whether the first chosen destination was in the impaired set (RQ2).

Secondary: recovery-time cost in minutes against the nearest-region policy, reported for every scenario and not tested; SLO breach minutes, which are the unavailable minutes since no candidate lies beyond the latency bound, and their share of a monthly error budget at 99.95 percent availability, a target the author confirmed against his production experience on Mon Nov 16, 2026 (21.9 minutes: 0.05 percent of an average month of 43,829 minutes, 365.2425 days over 12 months); decision regret, the carbon gap between the persistence choice and the oracle-forecast choice; the absolute carbon per outage hour.

## 8. Analysis

Unit: the event. The paired differences of an event's instances are averaged, so an event with several impaired regions counts once.

Count: the number of events in the primary analysis is fixed after data preparation and before any policy run, and is written with its date to `docs/counts.md`.

Primary tests: four comparisons on the primary scenario only, lowest-carbon and budget-bounded each against nearest-region, on carbon saved and on exposure, at a family-wise alpha of 0.05 with the Holm correction. Carbon saved is tested with `scipy.stats.wilcoxon` (`zero_method="wilcox"`, `method="auto"`). Exposure differences take few distinct values, so they are tested with the exact two-sided sign test, `scipy.stats.binomtest` on the events with a nonzero difference. The NumPy and SciPy versions are pinned in `pyproject.toml`. A comparison with no nonzero difference is reported as such and is not significant. Each comparison reports the share of events with a nonzero difference and the mean paired difference with a 95 percent percentile bootstrap interval from 10,000 resamples of events; carbon saved also reports the Hodges-Lehmann estimate with its interval and the matched-pairs rank-biserial correlation.

Minimum sample: with fewer than 30 events in the primary analysis, all results are reported as descriptive statistics only, with no tests. The decision to go on to a paper is made on that count, before any policy run, and is written to `docs/counts.md` with its date. Every result is posted in this repository whatever it shows.

RQ3: an event is within budget when none of its instances needed a second failover and its recovery-time cost is at most 2 minutes, about a tenth of the monthly error budget of section 7 (ASSUMED). The same budget holds for every setting and every scenario. The frontier plots mean carbon saved against the share of events within budget, across the grid of section 5, in each scenario.

Hour analysis: each event is replayed at every hourly start of its own calendar year, with its duration and impaired set kept, and with the co-failure counts as they stood at the real decision time. Hours that lack carbon data for the window are skipped and counted. It shows how much of the saving depends on the hour. It adds no independent failures and enters no test.

Sensitivity runs: every value in the sensitivity column of section 4; the ASSUMED factors set to 11 and to 820 gCO2eq/kWh, the lowest and highest medians that `src/cfo/factors.py` takes from the table; policies that also avoid regions whose own impairment began before the decision time; day-only starts removed; events naming two or more services only; correlated and isolated events separately. None replaces a primary result.

## 9. Test bed check of the recovery model

Setup: three single-node kind clusters (Kubernetes in Docker) for the home, a near and a far region, on one standard GitHub-hosted Linux runner of a public repository, which GitHub's runner documentation gives 4 processors and 16 gigabytes. An Envoy proxy steers 100 requests per second to the home cluster, with an active health check every 2 seconds, a timeout of 1 second and ejection after 3 failures. The added round trip is 10 milliseconds to the near cluster and 40 to the far one, set with Linux traffic control (netem) as half in each direction.

Run: after a steady minute, the home cluster's node container is stopped. Two destinations (near and far) and two headroom levels (full, and half with a scripted scale-up) give four cells, with 10 repeats each from the same starting state.

Measures: detection (failure to ejection of the home upstream), steering (ejection to 99 percent of requests served at the destination), scale-up (steering to the added replicas ready), and recovery (failure to the first 10-second window with 99.9 percent success and latency within the bound). Each is reported as a median and interquartile range over the repeats.

What it checks: the model's structure. First, that measured recovery equals the sum of measured detection, steering and scale-up, within the measured interquartile range, so that no term is missing. Second, that recovery into the far cluster does not differ from recovery into the near cluster by more than that range, as the model assumes when it gives every destination the same recovery time. A failed check is reported and named as a limit of the model. The test bed replaces no value of section 4, whose terms model an automated decision, DNS steering and node start, which kind cannot reproduce.

## 10. Seeds and reproducibility

Master seed: the text "20261115:carbon-failover". Each random stream is `numpy.random.Generator(numpy.random.PCG64(int.from_bytes(hashlib.sha256(f"{master}:{name}".encode()).digest()[:8], "big")))`, for the names "start-hour", "random-policy", "bootstrap" and "author-sample".

Draws: "start-hour" draws `rng.integers(0, 24)` once per flagged instance, in the row order of `corpus.csv` in version 1.0.0 of the dataset (its numbers run 1 to 447, then P1 to P50), then by home region code. "random-policy" draws `rng.integers(0, n)` over the n healthy candidates sorted by region code, once per decision, instances in the same order and decisions in time order. "bootstrap" draws `rng.integers(0, n, size=(10000, n))` once per comparison, in the order lowest-carbon carbon, lowest-carbon exposure, budget-bounded carbon, budget-bounded exposure. "author-sample" draws `rng.choice(numbers, size=10, replace=False)` over each provider's corpus numbers in that row order, in the order AWS, Azure, Google Cloud; a fresh sample continues the same stream, leaves out reports already drawn, and takes every report that is left when fewer than 10 are.

Every run writes a record with its configuration, the commit, the seed of each stream and the SHA-256 of every input file, so that every figure can be rebuilt from the release.

## 11. Budget

The pipeline calls no language model API; the event coding runs in sessions of the author's paid language-model subscription. Compute: GitHub Actions on standard runners of this public repository, free under GitHub's billing terms. No cloud spend. Data: free public sources only.

## 12. Roles and assistance

The author approved the data sources and the test bed of this design (Thu Nov 5, 2026), confirmed the primary values of the recovery model, the availability target and the visibility assumption against his production experience (sections 4, 5 and 7, Mon Nov 16, 2026), codes the blind sample of section 3.1, reads the results and the paper before submission, and is responsible for every claim. Claude models from Anthropic drafted the design and this text, write and run the code and the test bed, and code the outage events under the codebook. `docs/ai_use.md` lists each model and version with its dates and its work, and each commit names its AI co-author.

## 13. Data and licenses

Code: Apache License 2.0 (`LICENSE`). The design documents in `docs/` and the data produced for this study (the coded events, the region table, the results): CC BY 4.0. Third-party data keeps its own license: EIA data is in the public domain; NESO and Energy-Charts data are CC BY 4.0 and credited. Report text is never redistributed.
