# Test bed pilot, Mon Nov 16, 2026

One repeat per cell of section 9 of the preregistration, workflow `testbed`, run 43856766395 (commit after 559de2b), standard GitHub-hosted Linux runner. Results: `pilot_2026-11-16.json`. The full run is 10 repeats per cell (`workflow_dispatch`, input `repeats` = 10).

| Cell | Detection, s | Steering, s | Scale-up, s | Recovery, s | Destination median latency, ms |
|---|---|---|---|---|---|
| Near, full headroom | 7.74 | 0.0 | 0.0 | 7.70 | 11.1 |
| Near, half headroom | 7.85 | 0.0 | 2.76 | 7.80 | 11.3 |
| Far, full headroom | 7.82 | 0.0 | 0.0 | 7.80 | 41.7 |
| Far, half headroom | 7.80 | 0.0 | 2.46 | 7.80 | 41.8 |

What the pilot shows:
- The delays hold: the destination answers 10 ms (near) and 40 ms (far) slower than the home cluster's 1.3 to 1.6 ms.
- Detection is about 7.8 s, as three failed checks 2 s apart with a 1 s timeout give.
- Steering is immediate: Envoy's priority failover sends every request to the destination from the ejection.
- With full headroom, recovery equals detection plus steering to within 0.1 s, and near and far differ by at most 0.1 s, so both structural checks pass in the pilot.
- With half headroom, recovery does not include the scale-up: two replicas of the echo server carry 100 requests per second, so kind does not reproduce a capacity shortfall. Under section 9 this is named as a limit of the model, not a failed check of its structure.
- The first pilot (run 43854881810) measured steering at the end of a 1-second window, which set a 1-second floor; the measure now takes the window's start.
