"""The seven rules of preregistration section 3.1, applied in order to every event-home instance.

Usage: python -m cfo.eligibility CORPUS_CSV BUILD_DIR REGION_TABLE CARBON_CSV

Writes BUILD_DIR/instances_ruled.csv (each instance with its first failed rule, or "kept") and
BUILD_DIR/exclusions.csv (counts by rule, for instances and for events), and prints the counts.
"""
from __future__ import annotations

import csv
import hashlib
import math
import os
import sys
from datetime import datetime, timedelta, timezone

import numpy as np

from .events import t, ts

MASTER = "20261115:carbon-failover"
ROUTE, FIBRE_KM_S, FIXED_MS, BOUND_MS, MIN_DUR = 1.5, 200_000.0, 2.0, 50.0, 30
RULES = {1: "region named", 2: "regional or multi-region scope", 3: "lasted 30 minutes or more",
         4: "start to the hour, or day with duration", 5: "home in the region table",
         6: "two or more candidates", 7: "hourly carbon for every candidate"}


def stream(name: str) -> np.random.Generator:
    seed = int.from_bytes(hashlib.sha256(f"{MASTER}:{name}".encode()).digest()[:8], "big")
    return np.random.Generator(np.random.PCG64(seed))


def km(a: tuple[float, float], b: tuple[float, float]) -> float:
    (la1, lo1), (la2, lo2) = [(math.radians(x), math.radians(y)) for x, y in (a, b)]
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371.0088 * math.asin(math.sqrt(h))


def added_rtt_ms(a, b, route: float = ROUTE) -> float:
    """Section 3.3: 2 x great-circle distance x route factor / 200,000 km/s, plus 2 ms."""
    return 2 * km(a, b) * route / FIBRE_KM_S * 1000 + FIXED_MS


def ga_end(date: str, precision: str) -> datetime | None:
    """The last moment of the stated GA period: a region counts only for instances starting after it."""
    if not date:
        return None
    if precision == "year" or len(date) == 4:
        return datetime(int(date[:4]) + 1, 1, 1, tzinfo=timezone.utc)
    if precision == "month" or len(date) == 7:
        y, m = int(date[:4]), int(date[5:7])
        return datetime(y + (m == 12), m % 12 + 1, 1, tzinfo=timezone.utc)
    return datetime.strptime(date[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc) + timedelta(days=1)


def load_regions(path: str) -> dict[tuple[str, str], dict]:
    out = {}
    for r in csv.DictReader(open(path, newline="")):
        if r.get("included", "yes") != "yes":
            continue  # a region whose GA date or grid zone was not found: out of the candidate sets
        r["latlon"] = (float(r["lat"]), float(r["lon"]))
        r["ga_end"] = ga_end(r["ga_date"], r["ga_precision"])
        out[(r["provider"], r["region"])] = r
    return out


def load_carbon(path: str) -> dict[str, set[str]]:
    hours: dict[str, set[str]] = {}
    for r in csv.DictReader(open(path, newline="")):
        hours.setdefault(r["zone"], set()).add(r["utc_start"])
    return hours


def candidates(home: dict, regions: dict, when: datetime, bound: float = BOUND_MS) -> list[dict]:
    return sorted((r for (p, _), r in regions.items()
                   if p == home["provider"] and r["region"] != home["region"] and r["geo"] == home["geo"]
                   and r["ga_end"] is not None and when >= r["ga_end"]
                   and added_rtt_ms(home["latlon"], r["latlon"]) <= bound), key=lambda r: r["region"])


def hours_needed(start: datetime, end: datetime) -> list[str]:
    h = start.replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)
    out = []
    while h < end:
        out.append(ts(h))
        h += timedelta(hours=1)
    return out


def rule(inst: dict, regions: dict, carbon: dict[str, set[str]], draws: dict) -> tuple[int | str, dict]:
    """The first rule the instance fails, or 'kept', with derived fields."""
    info: dict = {}
    if inst["scope"] not in ("regional", "multi_region"):
        return 2, info
    s, e = t(inst["start_utc"]), t(inst["end_utc"])
    prec = inst["start_precision"]
    if s and not e and inst["duration_min"]:
        e = s + timedelta(minutes=int(float(inst["duration_min"])))
    if not (s and e) or (e - s) < timedelta(minutes=MIN_DUR):
        return 3, info
    if prec not in ("minute", "hour"):
        if prec == "day" and inst["duration_min"]:
            key = (inst["event_id"], inst["home"])
            s = s.replace(hour=int(draws[key]), minute=0)
            e = s + timedelta(minutes=int(float(inst["duration_min"])))
            info["start_drawn"] = "yes"
        else:
            return 4, info
    info.update(start=ts(s), end=ts(e))
    home = regions.get((inst["provider"], inst["home"]))
    if home is None:
        return 5, info
    cands = candidates(home, regions, s)
    info["candidates"] = ";".join(c["region"] for c in cands)
    if len(cands) < 2:
        return 6, info
    need = hours_needed(s, e)
    missing = [c["region"] for c in cands if not set(need) <= carbon.get(c["zone"], set())]
    if missing:
        info["missing_carbon"] = ";".join(missing)
        return 7, info
    return "kept", info


def main(argv: list[str] | None = None) -> int:
    corpus, build, region_table, carbon_csv = (argv or sys.argv[1:])[:4]
    order = {r["corpus_no"]: i for i, r in enumerate(csv.DictReader(open(corpus, newline="")))}
    events = list(csv.DictReader(open(os.path.join(build, "events.csv"), newline="")))
    ev_order = {e["event_id"]: min(order[n] for n in e["corpus_nos"].split(";")) for e in events}
    insts = list(csv.DictReader(open(os.path.join(build, "instances.csv"), newline="")))
    regions, carbon = load_regions(region_table), load_carbon(carbon_csv)
    # "start-hour" draws: once per flagged instance, events in corpus row order, then home region code
    flagged = sorted((i for i in insts if i["start_precision"] == "day" and i["duration_min"]),
                     key=lambda i: (ev_order[i["event_id"]], i["home"]))
    rng = stream("start-hour")
    draws = {(i["event_id"], i["home"]): int(rng.integers(0, 24)) for i in flagged}
    out = []
    for i in insts:
        r, info = rule(i, regions, carbon, draws)
        out.append({**i, "outcome": r, **{k: info.get(k, "") for k in
                    ("start", "end", "start_drawn", "candidates", "missing_carbon")}})
    with open(os.path.join(build, "instances_ruled.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    # counts: an event with no named region fails rule 1 as a whole; otherwise each instance counts
    ev_rule: dict[str, int | str] = {}
    for e in events:
        if not e["regions"]:
            ev_rule[e["event_id"]] = 1
    for i in out:
        best = ev_rule.get(i["event_id"])
        o = i["outcome"]
        if o == "kept" or best == "kept":
            ev_rule[i["event_id"]] = "kept"
        elif best is None or (isinstance(best, int) and o > best):
            ev_rule[i["event_id"]] = o  # the event's furthest-reaching instance
    rows = []
    for k in range(1, 8):
        rows.append({"rule": k, "text": RULES[k],
                     "instances_excluded": sum(1 for i in out if i["outcome"] == k),
                     "events_excluded": sum(1 for v in ev_rule.values() if v == k)})
    rows.append({"rule": "kept", "text": "meets all seven rules",
                 "instances_excluded": sum(1 for i in out if i["outcome"] == "kept"),
                 "events_excluded": sum(1 for v in ev_rule.values() if v == "kept")})
    with open(os.path.join(build, "exclusions.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["rule", "text", "instances_excluded", "events_excluded"])
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(r)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
