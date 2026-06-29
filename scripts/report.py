#!/usr/bin/env python3
"""Real-data audit: GSM8K trust denominator + validation vs GSM8K-Platinum gold.

Run after scripts/fetch_gsm8k_platinum.py. Reads:
  data/gsm8k_test.jsonl      (full GSM8K test split, 1319) -> trust denominator
  data/gsm8k_platinum.jsonl  (300, gold-labeled)           -> validation
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gradeable.audit import audit          # noqa: E402
from gradeable.item import load_gsm8k, load_jsonl  # noqa: E402
from gradeable.validate import validate     # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def section(title: str) -> None:
    print("\n" + "=" * 64 + f"\n{title}\n" + "=" * 64)


def main() -> None:
    section("GSM8K (full test split) — trust denominator")
    gsm = load_gsm8k(DATA / "gsm8k_test.jsonl")
    rep = audit(gsm)
    print(rep.summary())
    if rep.flagged:
        print(f"\n{len(rep.flagged)} item(s) flagged not-soundly-gradeable (showing up to 10):")
        for c in rep.flagged[:10]:
            print(f"  [{c.verdict.value}] {c.item.id}: {c.fired[0].reason if c.fired else ''}")

    section("GSM8K-Platinum (300, human gold labels) — validation")
    plat = load_jsonl(DATA / "gsm8k_platinum.jsonl")
    prep = audit(plat)
    n_bad = sum(1 for it in plat if it.gold_label == "problematic")
    print(f"gold: {n_bad} problematic / {len(plat)} items "
          f"({n_bad / len(plat):.1%}) — PlatinumBench rejected+revised")
    print("\naudit of the 300 (our deterministic rules):")
    print(prep.summary())
    print("\nclassifier vs human gold:")
    print(validate(plat).summary())


if __name__ == "__main__":
    main()
