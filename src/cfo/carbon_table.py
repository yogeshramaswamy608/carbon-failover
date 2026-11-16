"""Join the hourly intensity files into one table keyed by the region table's grid zones.

Usage: python -m cfo.carbon_table REGION_TABLE EIA_CI_CSV EUROPE_DIR OUT_CSV

A zone written "A>B@T" takes zone A's hours before T and zone B's from T (a balancing authority
retired and replaced in EIA-930). Every hour keeps its start in UTC; no hour is filled.
"""
from __future__ import annotations

import csv
import glob
import os
import sys


def main(argv: list[str] | None = None) -> int:
    regions, eia_csv, eu_dir, out = (argv or sys.argv[1:])[:4]
    zones = {r["zone"] for r in csv.DictReader(open(regions, newline="")) if r["zone"] and r["included"] == "yes"}
    want: dict[str, list[tuple[str, str, str]]] = {}  # source zone -> [(table zone, from, to)]
    for z in zones:
        if ">" in z:
            a, rest = z.split(">")
            b, at = rest.split("@")
            want.setdefault(a, []).append((z, "", at))
            want.setdefault(b, []).append((z, at, "9999"))
        else:
            want.setdefault(z, []).append((z, "", "9999"))
    rows: dict[tuple[str, str], str] = {}

    def take(src: str, hour: str, ci: str) -> None:
        for z, lo, hi in want.get(src, []):
            if lo <= hour < hi:
                rows[(z, hour)] = ci

    with open(eia_csv, newline="") as fh:
        for r in csv.DictReader(fh):
            if r["ba"] in want:
                take(r["ba"], r["utc_start"], r["ci_g_per_kwh"])
    for p in sorted(glob.glob(os.path.join(eu_dir, "*_*.csv"))):
        with open(p, newline="") as fh:
            for r in csv.DictReader(fh):
                if r["zone"] in want:
                    take(r["zone"], r["utc_start"], r["ci_g_per_kwh"])
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["zone", "utc_start", "ci_g_per_kwh"])
        for (z, h), ci in sorted(rows.items()):
            w.writerow([z, h, ci])
    per = {}
    for z, _ in rows:
        per[z] = per.get(z, 0) + 1
    print(f"zones {len(per)} of {len(zones)}; hours {len(rows)}; missing zones {sorted(zones - set(per))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
