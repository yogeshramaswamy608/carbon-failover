from cfo import script_code as sc
from cfo.reports import azure_section, review_url


def test_gcp_line_pacific_daylight_and_locations():
    text = ("Incident began at 2026-10-19 23:00 and ended at 2026-10-20 05:08 (all times are US/Pacific ).\n"
            "Previously affected location(s)\nLondon (europe-west2)\nMulti-region: eu (eu)\nDate Time Description\n")
    out = sc.code("gcp", text)
    assert out["start_utc"] == "2026-10-20T06:00Z" and out["end_utc"] == "2026-10-20T12:08Z"
    assert out["regions"] == "europe-west2" and out["locations_not_regions"] == "eu"


def test_gcp_standard_time_and_global():
    text = "Incident began at 2025-01-08 10:00 and ended at 2025-01-08 11:30 (all times are US/Pacific).\nAffected location(s)\nGlobal\n"
    out = sc.code("gcp", text)
    assert out["start_utc"] == "2025-01-08T18:00Z" and out["scope"] == "global" and "regions" not in out


def test_azure_forms():
    a = sc.code("azure", "Between 20:30 UTC on 30 September 2026 and 02:15 UTC on 1 October 2026, customers")
    assert a == {"start_utc": "2026-09-30T20:30Z", "start_precision": "minute", "end_utc": "2026-10-01T02:15Z"}
    b = sc.code("azure", "Between 08:05 UTC and 18:30 UTC on 22 December 2025, the service")
    assert b["start_utc"] == "2025-12-22T08:05Z" and b["end_utc"] == "2025-12-22T18:30Z"
    c = sc.code("azure", "Between 22:31 UTC on 8 January and 00:44 UTC on 11 January 2025, a change")
    assert c["start_utc"] == "2025-01-08T22:31Z" and c["end_utc"] == "2025-01-11T00:44Z"
    assert sc.code("azure", "Between 23:00 UTC and 01:00 UTC on 2 May 2024") == {}  # crosses midnight
    assert sc.code("aws", "Between 11:48 PM PDT on October 19 and 2:40 AM PDT") == {}


def test_azure_review_url_and_section():
    row = {"source": "Microsoft Azure PIR", "url": "https://aka.ms/AzPIR/ML7_-DWG", "report_id": "ML7_-DWG"}
    assert review_url(row).endswith("trackingId=ML7_-DWG")
    page = "Header\n09/30/2026\nPIR title\nTracking ID: AB12-CD3\nWhat happened?\nBody\nSorry for the inconvenience, x\nFooter"
    assert azure_section(page, "AB12-CD3") == "09/30/2026\nPIR title\nTracking ID: AB12-CD3\nWhat happened?\nBody"
    assert azure_section(page, "ZZZZ-999") == ""
