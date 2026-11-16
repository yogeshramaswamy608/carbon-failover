"""Hourly production-based carbon intensity per balancing authority from EIA-930 balance files.

Intensity = sum over fuels of (generation x factor) / sum of generation, over non-storage
fuels with positive generation. Imports are not traced (production-based signal). Each hour is
labelled by its start in UTC; the EIA file gives the end of the hour.
"""
from __future__ import annotations

import csv
import sys
from datetime import datetime, timedelta
from typing import Iterator

from .factors import FACTORS, STORAGE, key_for

PREFIX = "Net Generation (MW) from "


def hour_start(utc_end: str) -> str:
    """The start of the hour in UTC, ISO 8601, from the file's "UTC Time at End of Hour"."""
    end = datetime.strptime(utc_end.strip(), "%m/%d/%Y %I:%M:%S %p")
    return (end - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%MZ")


def fuel_columns(header: list[str]) -> dict[int, str]:
    """Column index to fuel, using the Adjusted column when present, else the reported one."""
    base, adj = {}, {}
    for i, h in enumerate(header):
        if not h.startswith(PREFIX):
            continue
        name = " ".join(h[len(PREFIX):].split())  # EIA headers sometimes carry double spaces
        target = adj if name.endswith(" (Adjusted)") else base if not name.endswith(")") else None
        if target is None:
            continue
        fuel = key_for("eia930", name.removesuffix(" (Adjusted)"))  # raises on a label factors.py lacks
        target.setdefault(fuel, []).append(i)
    chosen = adj if adj else base
    return {i: f for f, idx in chosen.items() for i in idx}


def _num(s: str) -> float:
    s = s.replace(",", "").strip()
    return float(s) if s else 0.0


def rows(path: str, factors: dict = FACTORS) -> Iterator[tuple[str, str, float, float]]:
    """Yield (balancing authority, UTC start of hour, intensity gCO2eq/kWh, generation MW)."""
    with open(path, newline="", encoding="utf-8-sig") as fh:
        r = csv.reader(fh)
        header = next(r)
        ba, utc = header.index("Balancing Authority"), header.index("UTC Time at End of Hour")
        cols = fuel_columns(header)
        for row in r:
            gen = em = 0.0
            for i, fuel in cols.items():
                if fuel in STORAGE:
                    continue
                mw = _num(row[i])
                if mw > 0:
                    gen += mw
                    em += mw * factors[fuel]
            if gen > 0:
                yield row[ba], hour_start(row[utc]), em / gen, gen


def main(argv: list[str] | None = None) -> int:
    w = csv.writer(sys.stdout)
    w.writerow(["ba", "utc_start", "ci_g_per_kwh", "gen_mw"])
    for p in argv or sys.argv[1:]:
        for ba, t, ci, g in rows(p):
            w.writerow([ba, t, f"{ci:.1f}", f"{g:.0f}"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
