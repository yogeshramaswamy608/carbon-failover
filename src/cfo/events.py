"""Coded rows, events and event-home instances (preregistration 3.1, event codebook 2 to 7).

Usage: python -m cfo.events CORPUS_CSV SCRIPT_FIELDS_CSV MODEL_DIR OUT_DIR

Reads the script's fields (cfo.script_run) and the model's outputs (logs/coding/bNN.json),
writes OUT_DIR/coded.csv (one row per kept report, no report text), OUT_DIR/script_model_diffs.csv,
OUT_DIR/events.csv, OUT_DIR/merges.csv and OUT_DIR/instances.csv.
"""
from __future__ import annotations

import csv
import glob
import json
import os
import sys
from datetime import datetime, timedelta, timezone

from .reports import KEPT, kept_rows, review_url

CODED = ["corpus_no", "provider", "link", "published_utc", "scope", "regions", "zones", "start_utc",
         "start_precision", "end_utc", "end_basis", "duration_min", "region_starts", "services_n",
         "evidence", "coded_by", "notes"]
SCRIPT_FIELDS = ["start_utc", "start_precision", "end_utc", "scope", "regions"]
WIDTH = {"unclear": 0, "zonal": 1, "regional": 2, "multi_region": 3, "global": 4}
FMT = "%Y-%m-%dT%H:%MZ"


def t(s: str) -> datetime | None:
    return datetime.strptime(s, FMT).replace(tzinfo=timezone.utc) if s else None


def ts(d: datetime) -> str:
    return d.strftime(FMT)


def _flat(v) -> str:
    if isinstance(v, dict):
        return "; ".join(f"{k}: {x}" for k, x in v.items())
    if isinstance(v, list):
        return ";".join(str(x) for x in v)
    return "" if v is None else str(v)


def _regions(s: str) -> list[str]:
    return sorted({x.strip() for x in s.split(";") if x.strip()})


def coded_rows(corpus: str, script_csv: str, model_dir: str) -> tuple[list[dict], list[dict]]:
    script = {r["corpus_no"]: r for r in csv.DictReader(open(script_csv, newline=""))}
    model = {}
    for p in sorted(glob.glob(os.path.join(model_dir, "b*.json"))):
        for o in json.load(open(p)):
            model[str(o["corpus_no"])] = o
    rows, diffs = [], []
    for c in kept_rows(corpus):
        n = c["corpus_no"]
        m = model.get(n)
        row = {k: "" for k in CODED}
        row.update(corpus_no=n, provider=KEPT[c["source"]], link=review_url(c))
        notes = []
        if m is None:
            notes.append("report page not retrievable on Mon Nov 16, 2026 (Azure keeps reviews 5 years); not coded")
        else:
            for k in CODED:
                if k in m and k not in ("corpus_no", "provider"):
                    row[k] = _flat(m[k])
            row["regions"] = ";".join(_regions(row["regions"]))
            row["zones"] = ";".join(_regions(row["zones"]))
        s = {k: script[n][k] for k in SCRIPT_FIELDS if script.get(n, {}).get(k)}
        for k, v in s.items():
            mv = row[k]
            same = (_regions(mv) == _regions(v)) if k == "regions" else (mv == v)
            if mv and not same:
                diffs.append({"corpus_no": n, "field": k, "script": v, "model": mv})
            row[k] = v
        times_by = "script" if "start_utc" in s else ("model" if m else "")
        region_by = "script" if "regions" in s or "scope" in s else ("model" if m else "")
        row["coded_by"] = ";".join(dict.fromkeys(x for x in (times_by, region_by) if x))
        if m is not None and not row["published_utc"] and row["end_utc"]:
            row["published_utc"] = (t(row["end_utc"]) + timedelta(days=14)).strftime("%Y-%m-%d")
            notes.append("no publication date shown; set to the end plus 14 days (codebook)")
        if m is not None and m.get("notes"):
            notes.append(str(m["notes"]))
        row["notes"] = " | ".join(notes)
        rows.append(row)
    return rows, diffs


def window(r: dict) -> tuple[datetime | None, datetime | None]:
    s, e = t(r["start_utc"]), t(r["end_utc"])
    if s and not e and r["duration_min"]:
        e = s + timedelta(minutes=int(float(r["duration_min"])))
    return s, e


def build_events(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """Merge reports of one provider whose windows overlap and whose region sets share a region,
    or that are both global (codebook section 6), transitively, in corpus row order."""
    order = {r["corpus_no"]: i for i, r in enumerate(rows)}
    groups: list[list[dict]] = []
    for r in rows:
        if not r["scope"]:
            groups.append([r])
            continue
        s, e = window(r)
        hit = None
        for g in groups:
            if g[0]["provider"] != r["provider"] or not g[0]["scope"]:
                continue
            for q in g:
                qs, qe = window(q)
                if not (s and e and qs and qe) or not (s < qe and qs < e):
                    continue
                share = set(_regions(r["regions"])) & set(_regions(q["regions"]))
                if share or (r["scope"] == "global" and q["scope"] == "global"):
                    hit = g
                    break
            if hit:
                break
        if hit:
            hit.append(r)
        else:
            groups.append([r])
    events, merges = [], []
    for k, g in enumerate(sorted(groups, key=lambda g: min(order[x["corpus_no"]] for x in g)), 1):
        g = sorted(g, key=lambda x: order[x["corpus_no"]])
        regs = sorted(set().union(*[_regions(x["regions"]) for x in g]))
        scopes = [x["scope"] for x in g if x["scope"]]
        scope = max(scopes, key=lambda x: WIDTH[x]) if scopes else ""
        if len(g) > 1 and len(regs) >= 2 and "global" not in scopes:
            scope = "multi_region"
        wins = [window(x) for x in g]
        starts = [w[0] for w in wins if w[0]]
        ends = [w[1] for w in wins if w[1]]
        precs = [x["start_precision"] for x in g if x["start_utc"] and window(x)[0] == min(starts)] if starts else []
        rs = {}
        for x in g:
            for pair in _regions(x["region_starts"]):
                if "=" in pair:
                    reg, when = pair.split("=", 1)
                    rs[reg] = min(rs.get(reg, when), when)
        ev = {"event_id": f"E{k:03d}", "provider": g[0]["provider"],
              "corpus_nos": ";".join(x["corpus_no"] for x in g), "scope": scope, "regions": ";".join(regs),
              "start_utc": ts(min(starts)) if starts else "", "start_precision": precs[0] if precs else "",
              "end_utc": ts(max(ends)) if ends else "",
              "duration_min": g[0]["duration_min"] if len(g) == 1 else "",
              "region_starts": ";".join(f"{a}={b}" for a, b in sorted(rs.items())),
              "services_n": max([int(x["services_n"]) for x in g if str(x["services_n"]).isdigit()] or [0]) or "",
              "published_utc": min(x["published_utc"] for x in g if x["published_utc"]) if any(x["published_utc"] for x in g) else ""}
        events.append(ev)
        if len(g) > 1:
            merges.append({"event_id": ev["event_id"], "corpus_nos": ev["corpus_nos"], "regions": ev["regions"],
                           "start_utc": ev["start_utc"], "end_utc": ev["end_utc"]})
    return events, merges


def instances(events: list[dict]) -> list[dict]:
    """One event-home instance per impaired region of a regional or multi-region event."""
    out = []
    for ev in events:
        rs = dict(p.split("=", 1) for p in ev["region_starts"].split(";") if "=" in p)
        regs = _regions(ev["regions"])
        for h in regs:
            out.append({"event_id": ev["event_id"], "provider": ev["provider"], "home": h,
                        "impaired": ";".join(x for x in regs if x != h),
                        "start_utc": rs.get(h, ev["start_utc"]), "end_utc": ev["end_utc"],
                        "start_precision": ev["start_precision"] if h not in rs else "minute",
                        "duration_min": ev["duration_min"], "scope": ev["scope"]})
    return out


def _write(path: str, rows: list[dict], fields: list[str] | None = None) -> None:
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields or (list(rows[0]) if rows else ["empty"]))
        w.writeheader()
        w.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    corpus, script_csv, model_dir, out = (argv or sys.argv[1:])[:4]
    os.makedirs(out, exist_ok=True)
    rows, diffs = coded_rows(corpus, script_csv, model_dir)
    events, merges = build_events(rows)
    inst = instances(events)
    _write(os.path.join(out, "coded.csv"), rows, CODED)
    _write(os.path.join(out, "script_model_diffs.csv"), diffs, ["corpus_no", "field", "script", "model"])
    _write(os.path.join(out, "events.csv"), events)
    _write(os.path.join(out, "merges.csv"), merges, ["event_id", "corpus_nos", "regions", "start_utc", "end_utc"])
    _write(os.path.join(out, "instances.csv"), inst)
    print(f"coded rows {len(rows)}; script-model differences {len(diffs)}; events {len(events)}; "
          f"merges {len(merges)}; instances {len(inst)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
