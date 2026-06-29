from __future__ import annotations

import argparse

from .audit import audit
from .item import load_fixture, load_jsonl
from .validate import validate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="gradeable",
        description="Audit a benchmark's soundly-gradeable fraction (the trust denominator).",
    )
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--demo", action="store_true", help="run on the bundled offline fixture")
    src.add_argument("--input", metavar="JSONL", help="path to a benchmark JSONL")
    args = parser.parse_args(argv)

    items = load_fixture() if args.demo else load_jsonl(args.input)

    report = audit(items)
    print("=== gradeability audit ===")
    print(report.summary())

    if report.flagged:
        print("\nflagged items:")
        for c in report.flagged:
            reason = c.fired[0].reason if c.fired else ""
            print(f"  [{c.verdict.value}] {c.item.id}: {reason}")

    if any(it.gold_label is not None for it in items):
        print("\n=== validation ===")
        print(validate(items).summary())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
