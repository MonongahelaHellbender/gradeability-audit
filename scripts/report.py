#!/usr/bin/env python3
"""Real-data audit across benchmarks: the trust denominator as a comparable stat.

Run after the fetch scripts. Reads:
  data/gsm8k_test.jsonl        (full GSM8K test split, 1319) -> numeric profile
  data/gsm8k_platinum.jsonl    (300, gold-labeled)           -> validation
  data/hotpotqa_platinum.jsonl (250, gold-labeled)           -> exact-match profile

GSM8K is graded by numeric equality (sound); HotpotQA by exact-match/F1 over
free text (sound only for numbers + yes/no). The trust denominator should drop
hard between them -- that is the whole point: it discriminates.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gradeable.audit import audit                                  # noqa: E402
from gradeable.item import load_gsm8k, load_jsonl                  # noqa: E402
from gradeable.rules import EXACT_MATCH_PROFILE, NUMERIC_PROFILE   # noqa: E402
from gradeable.validate import validate                           # noqa: E402
from gradeable.verdict import Verdict                             # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def section(title: str) -> None:
    print("\n" + "=" * 66 + f"\n{title}\n" + "=" * 66)


def gold_problematic_rate(items) -> float:
    n = sum(1 for it in items if it.gold_label == "problematic")
    return n / len(items) if items else 0.0


def main() -> None:
    # ---- GSM8K: numeric grader (sound) ----
    section("GSM8K (full test split) — numeric grader")
    gsm = load_gsm8k(DATA / "gsm8k_test.jsonl")
    gsm_rep = audit(gsm, NUMERIC_PROFILE)
    print(gsm_rep.summary())

    section("GSM8K-Platinum (300, gold labels) — validation of the ill-posed axis")
    gsm_plat = load_jsonl(DATA / "gsm8k_platinum.jsonl")
    print(f"gold key-defect rate: {gold_problematic_rate(gsm_plat):.1%} (rejected+revised)")
    print(validate(gsm_plat, NUMERIC_PROFILE).summary())

    # ---- HotpotQA: exact-match grader (unsound for free text) ----
    section("HotpotQA-Platinum (250) — exact-match grader")
    hpqa = load_jsonl(DATA / "hotpotqa_platinum.jsonl")
    hpqa_rep = audit(hpqa, EXACT_MATCH_PROFILE)
    print(hpqa_rep.summary())
    print("\nNOTE: the JUDGE_DEPENDENT count is NOT validated against the gold "
          "labels.\ncleaning_status golds WELL-POSEDNESS (the ill-posed axis); "
          "exact-checkability is\na different, orthogonal axis -- a HotpotQA item "
          "can be perfectly well-posed\nAND judge-dependent. Validating one against "
          "the other would be a category error.")
    print(f"\nfor context, gold key-defect rate here: {gold_problematic_rate(hpqa):.1%} "
          "(rejected+revised) — orthogonal to the denominator above")

    # ---- the headline: the denominator discriminates ----
    section("TRUST DENOMINATOR — cross-benchmark")
    print(f"  GSM8K     (numeric eq grader) : {gsm_rep.soundly_gradeable_fraction:6.1%} exact-checkable")
    print(f"  HotpotQA  (exact-match grader): {hpqa_rep.soundly_gradeable_fraction:6.1%} exact-checkable")
    print(f"\n  HotpotQA verdict split: "
          f"exact={hpqa_rep.counts[Verdict.EXACT_CHECKABLE]} "
          f"judge={hpqa_rep.counts[Verdict.JUDGE_DEPENDENT]} "
          f"ill-posed={hpqa_rep.counts[Verdict.ILL_POSED]}")


if __name__ == "__main__":
    main()
