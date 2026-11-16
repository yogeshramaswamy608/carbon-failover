from datetime import datetime, timezone

from cfo import eligibility as el
from cfo import events as ev


def _r(n, scope, regions, s, e, prov="gcp"):
    return {"corpus_no": n, "provider": prov, "scope": scope, "regions": regions, "start_utc": s, "end_utc": e,
            "duration_min": "", "region_starts": "", "start_precision": "minute", "services_n": "1", "published_utc": ""}


def test_merge_shared_region_and_overlap_only():
    rows = [_r("1", "regional", "us-east1", "2024-01-01T00:00Z", "2024-01-01T02:00Z"),
            _r("2", "regional", "us-east1;us-east4", "2024-01-01T01:00Z", "2024-01-01T03:00Z"),
            _r("3", "regional", "us-east1", "2024-01-02T01:00Z", "2024-01-02T03:00Z"),
            _r("4", "regional", "us-east4", "2024-01-01T01:00Z", "2024-01-01T03:00Z", prov="azure")]
    events, merges = ev.build_events(rows)
    assert len(events) == 3 and merges[0]["corpus_nos"] == "1;2"
    assert events[0]["scope"] == "multi_region" and events[0]["end_utc"] == "2024-01-01T03:00Z"


def test_latency_model_and_ga_end():
    assert abs(el.added_rtt_ms((0, 0), (0, 0)) - 2.0) < 1e-9
    assert 15.0 < el.added_rtt_ms((48.86, 2.35), (52.52, 13.40)) < 15.3  # Paris to Berlin, 877 km: 13.2 + 2 ms
    assert el.ga_end("2016", "year") == datetime(2017, 1, 1, tzinfo=timezone.utc)
    assert el.ga_end("2022-06", "month") == datetime(2022, 7, 1, tzinfo=timezone.utc)
    assert el.ga_end("2022-06-15", "day") == datetime(2022, 6, 16, tzinfo=timezone.utc)


def test_hours_include_the_hour_before():
    s = datetime(2024, 1, 1, 10, 20, tzinfo=timezone.utc)
    e = datetime(2024, 1, 1, 11, 5, tzinfo=timezone.utc)
    assert el.hours_needed(s, e) == ["2024-01-01T09:00Z", "2024-01-01T10:00Z", "2024-01-01T11:00Z"]
