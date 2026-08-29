"""Run the phase-01 raw-data audit without altering the source CSV files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from nwc.data.baseline import audit_raw_data, load_raw_data


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument(
        "--report-path",
        type=Path,
        default=Path("reports/metrics/phase_01_raw_data_audit.json"),
    )
    args = parser.parse_args()
    raw = load_raw_data(args.raw_dir)
    _, report = audit_raw_data(raw)
    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    args.report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
