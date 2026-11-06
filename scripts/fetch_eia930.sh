#!/usr/bin/env bash
# Downloads EIA-930 six-month balance files (public domain, U.S. EIA) into $1 (default data/eia).
set -euo pipefail
out="${1:-data/eia}"; mkdir -p "$out"
for y in 2018 2019 2020 2021 2022 2023 2024 2025 2026; do
  for h in Jan_Jun Jul_Dec; do
    f="EIA930_BALANCE_${y}_${h}.csv"
    [ -s "$out/$f" ] || curl -sSf --retry 2 -o "$out/$f" "https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/$f"
  done
done
