import argparse
import datetime as dt
import os
import sys
from typing import List

from fetch_aemo import (
    DEFAULT_END,
    DEFAULT_START,
    DEFAULT_TABLE,
    run_fetch,
)
from clean_data import run_clean


def _parse_dt(value: str) -> dt.datetime:
    return dt.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")


def _run_ingest(args: argparse.Namespace) -> None:
    run_fetch(
        start_time=args.start,
        end_time=args.end,
        table=args.table,
        data_dir=args.data_dir,
    )


def _run_clean(args: argparse.Namespace) -> None:
    removed = run_clean(data_dir=args.data_dir)
    print(f"Deleted {removed} file(s).")


def _collect_missing_stages() -> List[str]:
    candidates = [
        ("feature_engineering", "src/features/feature_engineering.py"),
        ("train_model", "src/models/train_model.py"),
        ("evaluate_model", "src/models/evaluate_model.py"),
        ("optimizer", "src/optimizer/run_optimizer.py"),
        ("api", "src/api/main.py"),
        ("dashboard", "src/dashboard/app.py"),
    ]
    missing = []
    for label, path in candidates:
        if not os.path.exists(path):
            missing.append(f"{label} ({path})")
    return missing


def _run_all(args: argparse.Namespace) -> None:
    _run_ingest(args)

    missing = _collect_missing_stages()
    if missing:
        missing_text = "\n".join(f"- {item}" for item in missing)
        sys.stderr.write(
            "Note: Skipping stages that are not present in this repo:\n"
            f"{missing_text}\n"
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run individual pipeline stages or the full pipeline."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest = subparsers.add_parser("ingest", help="Run data ingestion only.")
    ingest.add_argument("--start", type=_parse_dt, default=DEFAULT_START)
    ingest.add_argument("--end", type=_parse_dt, default=DEFAULT_END)
    ingest.add_argument("--table", default=DEFAULT_TABLE)
    ingest.add_argument("--data-dir", default=None)
    ingest.set_defaults(func=_run_ingest)

    all_cmd = subparsers.add_parser("all", help="Run all available stages.")
    all_cmd.add_argument("--start", type=_parse_dt, default=DEFAULT_START)
    all_cmd.add_argument("--end", type=_parse_dt, default=DEFAULT_END)
    all_cmd.add_argument("--table", default=DEFAULT_TABLE)
    all_cmd.add_argument("--data-dir", default=None)
    all_cmd.set_defaults(func=_run_all)

    clean = subparsers.add_parser("clean", help="Delete all files under /data.")
    clean.add_argument("--data-dir", default=None)
    clean.set_defaults(func=_run_clean)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
