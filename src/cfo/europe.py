"""Hourly production-based carbon intensity for Great Britain (NESO) and other European countries
(Energy-Charts), with the frozen factors of factors.py (preregistration section 3.2).

Every hourly value is labelled by the start of its hour in UTC. A missing hour is not filled.

Usage:
  python -m cfo.europe neso YEAR > gb.csv
  python -m cfo.europe energy_charts COUNTRY YEAR > xx.csv
"""
from __future__ import annotations

import csv
import json
import sys
import time
import urllib.request
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from .factors import FACTORS, STORAGE, key_for

NESO_URL = "https://api.carbonintensity.org.uk/generation/{}/{}"
EC_URL = "https://api.energy-charts.info/public_power?country={}&start={}&end={}"


def _get(url: str) -> dict:
    for i in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "carbon-failover"}), timeout=120) as r:
                return json.load(r)
        except Exception:
            if i == 3:
                raise
            time.sleep(10 * (i + 1))
    raise RuntimeError


def _hour(dt: datetime) -> str:
    return dt.replace(minute=0, second=0, microsecond=0).strftime("%Y-%m-%dT%H:%MZ")


def neso_halfhour_intensity(mix: list[dict]) -> float | None:
    """Intensity of one half-hour: imports removed, remaining shares rescaled to 100 percent."""
    shares = {}
    for m in mix:
        k = key_for("neso", m["fuel"])
        if k is None or k in STORAGE:
            continue
        if m["perc"] > 0:
            shares[k] = shares.get(k, 0.0) + m["perc"]
    total = sum(shares.values())
    if total <= 0:
        return None
    return sum(p * FACTORS[k] for k, p in shares.items()) / total


def neso_hours(records: list[dict]) -> dict[str, float]:
    """Hour start to intensity; both half-hours of an hour, equal weight. An hour lacking one is dropped."""
    halves: dict[str, list[float]] = defaultdict(list)
    for r in records:
        start = datetime.strptime(r["from"], "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc)
        ci = neso_halfhour_intensity(r["generationmix"])
        if ci is not None:
            halves[_hour(start)].append(ci)
    return {h: sum(v) / 2 for h, v in halves.items() if len(v) == 2}


def neso_year(year: int) -> dict[str, float]:
    out: dict[str, float] = {}
    start = datetime(year, 1, 1, tzinfo=timezone.utc)
    end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
    end = min(end, datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0))
    t = start
    while t < end:
        u = min(t + timedelta(days=14), end)
        # the API also returns the half-hour that ends at "from"; overlaps between requests repeat values
        recs = _get(NESO_URL.format(t.strftime("%Y-%m-%dT%H:%MZ"), u.strftime("%Y-%m-%dT%H:%MZ")))["data"]
        out.update({h: v for h, v in neso_hours(recs).items() if h[:4] == str(year)})
        t = u
        time.sleep(1)
    return out


def ec_hours(d: dict) -> dict[str, tuple[float, float]]:
    """Hour start to (intensity, mean generation MW), weighted by generation within the hour."""
    em: dict[str, float] = defaultdict(float)
    gen: dict[str, float] = defaultdict(float)
    n: dict[str, int] = defaultdict(int)
    series = []
    for p in d["production_types"]:
        k = key_for("energy_charts", p["name"])
        if k is None or k in STORAGE:
            continue
        series.append((k, p["data"]))
    for i, ts in enumerate(d["unix_seconds"]):
        h = _hour(datetime.fromtimestamp(ts, tz=timezone.utc))
        g_any = False
        for k, data in series:
            v = data[i]
            if v is not None and v > 0:
                gen[h] += v
                em[h] += v * FACTORS[k]
                g_any = True
        if g_any:
            n[h] += 1
    return {h: (em[h] / gen[h], gen[h] / n[h]) for h in gen if gen[h] > 0}


def ec_year(country: str, year: int) -> dict[str, tuple[float, float]]:
    out: dict[str, tuple[float, float]] = {}
    now = datetime.now(timezone.utc)
    for m in range(1, 13):
        if datetime(year, m, 1, tzinfo=timezone.utc) > now:
            break  # a month that has not begun
        a = f"{year}-{m:02d}-01T00:00Z"
        b = f"{year + (m == 12)}-{(m % 12) + 1:02d}-01T00:00Z"
        if datetime.strptime(b, "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc) > now:
            b = (now - timedelta(hours=2)).strftime("%Y-%m-%dT%H:00Z")  # the month in progress, to two hours ago
        d = _get(EC_URL.format(country, a, b))
        out.update({h: v for h, v in ec_hours(d).items() if h[:7] == a[:7]})
        time.sleep(1)
    return out


def main(argv: list[str] | None = None) -> int:
    a = argv or sys.argv[1:]
    w = csv.writer(sys.stdout)
    w.writerow(["zone", "utc_start", "ci_g_per_kwh", "gen_mw"])
    if a[0] == "neso":
        for h, ci in sorted(neso_year(int(a[1])).items()):
            w.writerow(["GB", h, f"{ci:.1f}", ""])
    elif a[0] == "energy_charts":
        for h, (ci, g) in sorted(ec_year(a[1], int(a[2])).items()):
            w.writerow([a[1].upper(), h, f"{ci:.1f}", f"{g:.0f}"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
