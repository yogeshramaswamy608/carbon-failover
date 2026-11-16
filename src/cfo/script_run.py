"""Run the script coder over the 271 kept reports (preregistration section 3.1).

Usage: python -m cfo.script_run corpus.csv out.csv

Each page is fetched into memory, coded and dropped. The output holds the corpus number, the
link the coding read and the script's fields; it never holds report text, and nothing from a
page is printed.
"""
from __future__ import annotations

import csv
import sys
import time

from .reports import KEPT, kept_rows, report_text, review_url
from .script_code import code

FIELDS = ["corpus_no", "provider", "review_url", "fetched", "start_utc", "start_precision",
          "end_utc", "scope", "regions", "locations_not_regions"]


def main(argv: list[str] | None = None) -> int:
    corpus, out = (argv or sys.argv[1:])[:2]
    n_ok = n_coded = 0
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for row in kept_rows(corpus):
            prov = KEPT[row["source"]]
            rec = {"corpus_no": row["corpus_no"], "provider": prov, "review_url": review_url(row)}
            try:
                text = report_text(row)
                rec["fetched"] = "yes" if text else "empty"
            except Exception as e:  # the error class only, never page content
                text, rec["fetched"] = "", f"error:{type(e).__name__}"
            fields = code(prov, text) if text else {}
            del text
            rec.update(fields)
            n_ok += rec["fetched"] == "yes"
            n_coded += bool(fields)
            w.writerow(rec)
            time.sleep(1)
    print(f"reports fetched: {n_ok}; reports with script fields: {n_coded}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
