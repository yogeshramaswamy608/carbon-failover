"""Script coding of the fields a report states in a fixed form (event codebook, section 7).

Google Cloud: the line "Incident began at YYYY-MM-DD HH:MM and ended at YYYY-MM-DD HH:MM
(all times are US/Pacific)" and the list of affected locations under it.
Azure: the impact window "Between HH:MM UTC on D Month YYYY and HH:MM UTC on D Month YYYY".
AWS reports have no fixed form, so the script sets nothing for them.

Each result holds coded fields only, never report text.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

PACIFIC = ZoneInfo("America/Los_Angeles")
GCP_REGION = re.compile(r"^[a-z]+-[a-z]+\d+$")
GCP_LINE = re.compile(
    r"Incident began at (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) and ended at (\d{4}-\d{2}-\d{2} \d{2}:\d{2})"
    r"\s*\(all times are US/Pacific\s*\)"
)
AZ_TIME = r"(\d{1,2}:\d{2}) UTC on (\d{1,2}) ([A-Z][a-z]+),? (\d{4})"
AZ_LINE = re.compile(r"Between " + AZ_TIME + r" and " + AZ_TIME)
AZ_NO_FIRST_YEAR = re.compile(
    r"Between (\d{1,2}:\d{2}) UTC on (\d{1,2}) ([A-Z][a-z]+) and " + AZ_TIME)
AZ_SAME_DAY = re.compile(r"Between (\d{1,2}:\d{2})(?: UTC)? and (\d{1,2}:\d{2}) UTC on (\d{1,2}) ([A-Z][a-z]+),? (\d{4})")


def _utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def pacific_to_utc(s: str) -> str:
    """'2026-10-19 23:00' in US/Pacific, with the daylight-saving rule of its date, to ISO UTC."""
    return _utc(datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=PACIFIC))


def _az(hm: str, d: str, month: str, y: str) -> str:
    for fmt in ("%Y %B %d %H:%M", "%Y %b %d %H:%M"):
        try:
            return _utc(datetime.strptime(f"{y} {month} {d} {hm}", fmt).replace(tzinfo=timezone.utc))
        except ValueError:
            continue
    raise ValueError(f"unreadable Azure date: {d} {month} {y} {hm}")


def gcp_locations(text: str) -> list[str]:
    """Location labels listed under the began/ended line, as 'Name (code)' entries."""
    lines = text.split("\n")
    out: list[str] = []
    for k, line in enumerate(lines):
        if re.match(r"^(Previously |Currently )?[Aa]ffected location\(s\)", line):
            for x in lines[k + 1:]:
                if x.startswith("Date Time Description") or re.match(r"^(Previously |Currently )?[Aa]ffected", x):
                    break
                out.extend(re.findall(r"\(([^()]+)\)", x) or ([x] if x == "Global" else []))
    return out


def code(provider: str, text: str) -> dict:
    """The script's fields for one report; {} when the fixed form is absent."""
    if provider == "gcp":
        m = GCP_LINE.search(text)
        if not m:
            return {}
        out = {"start_utc": pacific_to_utc(m.group(1)), "start_precision": "minute",
               "end_utc": pacific_to_utc(m.group(2))}
        locs = gcp_locations(text)
        regions = sorted({x for x in locs if GCP_REGION.match(x)})
        other = sorted({x for x in locs if not GCP_REGION.match(x)})
        if any(x.lower() == "global" for x in other):
            out["scope"] = "global"
        if regions:
            out["regions"] = ";".join(regions)
        if other:
            out["locations_not_regions"] = ";".join(other)
        return out
    if provider == "azure":
        m = AZ_LINE.search(text)
        if m:
            g = m.groups()
            return {"start_utc": _az(*g[:4]), "start_precision": "minute", "end_utc": _az(*g[4:])}
        m = AZ_NO_FIRST_YEAR.search(text)
        if m:
            t1, d1, m1, t2, d2, m2, y = m.groups()
            start, end = _az(t1, d1, m1, y), _az(t2, d2, m2, y)
            if end > start:  # the year is the end's; a window across New Year is left to the model
                return {"start_utc": start, "start_precision": "minute", "end_utc": end}
        m = AZ_SAME_DAY.search(text)
        if m:
            t1, t2, d, mon, y = m.groups()
            start, end = _az(t1, d, mon, y), _az(t2, d, mon, y)
            if end > start:  # a same-day window that crosses midnight is left to the model
                return {"start_utc": start, "start_precision": "minute", "end_utc": end}
        return {}
    return {}


# Version 2 of the event codebook (sections 5 and 7), Thu Nov 19, 2026: the Google Cloud end is the
# incident report's own "Incident End" line, not the dashboard header's "ended at" time.
REPORT_HEAD = re.compile(r"^\d{1,2} [A-Z][a-z]{2} \d{4} \d{2}:\d{2} P[DS]T .*(Incident Report|Mini-IR)")
UPDATE_HEAD = re.compile(r"^\d{1,2} [A-Z][a-z]{2} \d{4} \d{2}:\d{2} P[DS]T\b")
IR_END = re.compile(r"^Incident End\s*:?\s*(\d{1,2})(?:st|nd|rd|th)? ([A-Z][a-z]+)\.?,? (\d{4}),?(?: at)? (\d{1,2}:\d{2})(?::\d{2})?(?: (?:US/Pacific|PDT|PST)\b.*)?\s*$")


def _pacific(d: str, month: str, y: str, hm: str) -> str | None:
    month = {"Sept": "Sep"}.get(month, month)
    for fmt in ("%Y %B %d %H:%M", "%Y %b %d %H:%M"):
        try:
            return _utc(datetime.strptime(f"{y} {month} {d} {hm}", fmt).replace(tzinfo=PACIFIC))
        except ValueError:
            continue
    return None


def gcp_ir_end(text: str, began_utc: str) -> str:
    """The end under codebook version 2: the latest plain "Incident End:" line of the newest incident
    report on the page that has one; "" when there is none, when a line cannot be read, or when the
    end falls before the header's begin time (a date the model reads from the dated updates)."""
    lines = text.split("\n")
    heads = [k for k, x in enumerate(lines) if REPORT_HEAD.match(x)]
    blocks = []
    for k in heads:
        j = next((m for m in range(k + 1, len(lines)) if UPDATE_HEAD.match(lines[m])), len(lines))
        blocks.append(lines[k + 1:j])
    if not heads:
        blocks = [lines]
    for b in blocks:
        hits = [IR_END.match(x) for x in b if x.startswith("Incident End")]
        if not hits:
            continue
        if not all(hits):
            return ""
        ends = [_pacific(*m.groups()) for m in hits]
        if None in ends:
            return ""
        end = max(ends)
        return end if end > began_utc else ""
    return ""


def code_v2(provider: str, text: str) -> dict:
    """The script's fields under codebook version 2: as code(), with the Google Cloud end replaced."""
    out = code(provider, text)
    if provider == "gcp" and out:
        out["end_utc"] = gcp_ir_end(text, out["start_utc"])
        if not out["end_utc"]:
            del out["end_utc"]
    return out
