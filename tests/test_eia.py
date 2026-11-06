import csv
from cfo import eia


def _file(tmp_path, header, rows):
    p = tmp_path / "x.csv"
    with open(p, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)
    return str(p)


def test_intensity_weighted_and_storage_excluded(tmp_path):
    h = ["Balancing Authority", "UTC Time at End of Hour",
         "Net Generation (MW) from Coal", "Net Generation (MW) from Wind",
         "Net Generation (MW) from Battery Storage", "Net Generation (MW) from Coal (Imputed)"]
    p = _file(tmp_path, h, [["CISO", "01/01/2025 1:00:00 AM", "100", "100", "50", "0"]])
    (ba, t, ci, gen), = list(eia.rows(p))
    assert ba == "CISO" and gen == 200 and abs(ci - (820 + 11) / 2) < 1e-9


def test_adjusted_columns_preferred(tmp_path):
    h = ["Balancing Authority", "UTC Time at End of Hour",
         "Net Generation (MW) from Coal", "Net Generation (MW) from Coal (Adjusted)",
         "Net Generation (MW) from Nuclear", "Net Generation (MW) from Nuclear (Adjusted)"]
    p = _file(tmp_path, h, [["X", "t", "0", "10", "0", "10"]])
    (_, _, ci, gen), = list(eia.rows(p))
    assert gen == 20 and abs(ci - (820 + 12) / 2) < 1e-9


def test_negative_and_blank_ignored(tmp_path):
    h = ["Balancing Authority", "UTC Time at End of Hour", "Net Generation (MW) from Natural Gas",
         "Net Generation (MW) from Solar", "Net Generation (MW) from Unknown Fuel Sources"]
    p = _file(tmp_path, h, [["X", "t", "1,000", "-5", ""]])
    (_, _, ci, gen), = list(eia.rows(p))
    assert gen == 1000 and ci == 490


def test_double_space_header(tmp_path):
    h = ["Balancing Authority", "UTC Time at End of Hour", "Net Generation (MW) from Pumped Storage  (Adjusted)",
         "Net Generation (MW) from Nuclear (Adjusted)"]
    p = _file(tmp_path, h, [["X", "t", "50", "10"]])
    (_, _, ci, gen), = list(eia.rows(p))
    assert gen == 10 and ci == 12
