"""Fetch the kept post-incident reports of the companion corpus and turn each page into plain text.

The text is used only to code (preregistration section 3.1). It is never written into this
repository, printed to a log or saved as an artifact; callers keep it in memory or in a
directory outside the repository.
"""
from __future__ import annotations

import csv
import html
import re
import time
import urllib.request

KEPT = {"AWS PES": "aws", "Microsoft Azure PIR": "azure", "Google Cloud incident report": "gcp"}
AZURE_REVIEW = "https://azure.status.microsoft/en-us/status/history/?trackingId={}"
UA = "carbon-failover research fetcher (https://github.com/yogeshramaswamy608/carbon-failover)"


def review_url(row: dict) -> str:
    """The page the coding reads. For Azure, aka.ms/AzPIR/ID opens a feedback form and the history
    page's anchor opens only the recent reviews, so the coding reads the history page filtered by the
    report's tracking ID."""
    if KEPT[row["source"]] == "azure":
        return AZURE_REVIEW.format(row["report_id"])
    return row["url"]


def kept_rows(corpus_csv: str) -> list[dict]:
    """The 271 kept rows (AWS, Azure, Google Cloud) in the corpus row order."""
    with open(corpus_csv, newline="", encoding="utf-8") as fh:
        return [r for r in csv.DictReader(fh) if r["source"] in KEPT]


def fetch(url: str, tries: int = 3) -> str:
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8", errors="replace")
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(5 * (i + 1))
    raise RuntimeError("unreachable")


def to_text(page: str) -> str:
    """Visible text of an HTML page, block elements on their own lines."""
    s = re.sub(r"(?is)<(script|style|noscript|svg|head)[^>]*>.*?</\1>", " ", page)
    s = re.sub(r"(?i)<br\s*/?>|</(p|div|li|tr|h[1-6]|section|article|table|ul|ol)>", "\n", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s).replace("\xa0", " ")
    lines = [" ".join(x.split()) for x in s.split("\n")]
    return "\n".join(x for x in lines if x)


def azure_section(text: str, tracking_id: str) -> str:
    """The one review of the history page that carries this tracking ID, or "" when it is absent."""
    lines = text.split("\n")
    at = [k for k, x in enumerate(lines) if x == f"Tracking ID: {tracking_id}"]
    if not at:
        return ""
    k = at[0]
    first = k - 1  # the review's title line
    if first > 0 and re.fullmatch(r"\d{2}/\d{2}/\d{4}", lines[first - 1]):
        first -= 1  # its date line
    last = len(lines)
    for j in range(k + 1, len(lines)):
        if lines[j].startswith("Tracking ID:") or lines[j].startswith("Sorry for the inconvenience"):
            last = j - 2 if lines[j].startswith("Tracking ID:") else j
            break
    return "\n".join(lines[first:last]).strip()


def report_text(row: dict) -> str:
    """Plain text of one kept report, trimmed to the report itself."""
    text = to_text(fetch(review_url(row)))
    if KEPT[row["source"]] == "azure":
        return azure_section(text, row["report_id"])
    return text
