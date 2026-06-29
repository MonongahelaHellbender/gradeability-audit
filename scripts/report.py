#!/usr/bin/env python3
"""Real-data audit across benchmarks: the trust denominator as a comparable stat.

Run after the fetch scripts. Reads:
  data/gsm8k_test.jsonl        (full GSM8K test split, 1319) -> numeric profile
  data/gsm8k_platinum.jsonl    (300, gold-labeled)           -> validation
  data/hotpotqa_platinum.jsonl (250, gold-labeled)           -> exact-match profile
  data/drop_platinum.jsonl     (250, gold-labeled)           -> exact-match profile (mixed)

GSM8K is graded by numeric equality (sound for every item). HotpotQA/DROP are
graded by exact-match/F1 (sound only for numbers + yes/no). The trust denominator
should fall as the share of free-text answers rises -- and DROP, with a real mix
of numeric and span answers, should split *within* one benchmark.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gradeable.audit import AuditReport, audit                    # noqa: E402
from gradeable.item import load_gsm8k, load_jsonl                 # noqa: E402
from gradeable.rules import EXACT_MATCH_PROFILE, NUMERIC_PROFILE  # noqa: E402
from gradeable.validate import validate                          # noqa: E402
from gradeable.verdict import Verdict                            # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

EXACT_MATCH_BENCHMARKS = [("HotpotQA", "hotpotqa_platinum.jsonl"), ("DROP", "drop_platinum.jsonl")]


def section(title: str) -> None:
    print("\n" + "=" * 66 + f"\n{title}\n" + "=" * 66)


def gold_defect_rate(items) -> float:
    n = sum(1 for it in items if it.gold_label == "problematic")
    return n / len(items) if items else 0.0


def split(rep: AuditReport) -> str:
    return (f"exact={rep.counts[Verdict.EXACT_CHECKABLE]} "
            f"judge={rep.counts[Verdict.JUDGE_DEPENDENT]} "
            f"ill-posed={rep.counts[Verdict.ILL_POSED]}")


def main() -> None:
    spectrum = []  # (name, grader, denominator)

    # ---- GSM8K: numeric grader (sound) ----
    section("GSM8K (full test split) — numeric grader")
    gsm = load_gsm8k(DATA / "gsm8k_test.jsonl")
    gsm_rep = audit(gsm, NUMERIC_PROFILE)
    print(gsm_rep.summary())
    spectrum.append(("GSM8K", "numeric equality", gsm_rep.soundly_gradeable_fraction))

    section("GSM8K-Platinum (300) — validation of the ill-posed axis")
    gsm_plat = load_jsonl(DATA / "gsm8k_platinum.jsonl")
    print(f"gold key-defect rate: {gold_defect_rate(gsm_plat):.1%} (rejected+revised)")
    print(validate(gsm_plat, NUMERIC_PROFILE).summary())

    # ---- exact-match benchmarks ----
    for name, fname in EXACT_MATCH_BENCHMARKS:
        items = load_jsonl(DATA / fname)
        rep = audit(items, EXACT_MATCH_PROFILE)
        spectrum.append((name, "exact-match / F1", rep.soundly_gradeable_fraction))
        section(f"{name}-Platinum ({len(items)}) — exact-match grader")
        print(rep.summary())
        print(f"  verdict split: {split(rep)}")
        print(f"  gold key-defect rate (orthogonal axis): {gold_defect_rate(items):.1%}")

    print("\n  (JUDGE_DEPENDENT is NOT scored against the gold labels: cleaning_status "
          "golds\n   well-posedness, which is orthogonal to exact-checkability. "
          "Scoring one against\n   the other is a category error.)")

    # ---- headline: the denominator is a comparable cross-benchmark statistic ----
    section("TRUST DENOMINATOR — spectrum (the deliverable)")
    for name, grader, frac in sorted(spectrum, key=lambda x: -x[2]):
        bar = "#" * round(frac * 40)
        print(f"  {name:9} {frac:6.1%}  {bar:<40}  ({grader})")
    print("\n  100% = every item soundly gradeable by the benchmark's own grader.")
    print("  Lower = more of the score rests on an unsound grader (a judge / EM over free text).")


if __name__ == "__main__":
    main()
