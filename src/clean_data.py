import argparse
import os
import pathlib
import typing


def _resolve_data_dir(data_dir: typing.Optional[str]) -> pathlib.Path:
    if data_dir is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.abspath(os.path.join(base_dir, "..", "data"))
    return pathlib.Path(data_dir)


def run_clean(data_dir: typing.Optional[str] = None) -> int:
    data_path = _resolve_data_dir(data_dir)
    if not data_path.exists():
        return 0

    removed = 0
    for path in data_path.rglob("*"):
        if path.is_file():
            path.unlink()
            removed += 1

    return removed


def main() -> None:
    parser = argparse.ArgumentParser(description="Delete all files under /data.")
    parser.add_argument("--data-dir", default=None)
    args = parser.parse_args()

    removed = run_clean(data_dir=args.data_dir)
    print(f"Deleted {removed} file(s).")


if __name__ == "__main__":
    main()
