# Finding 01 — GSM8K: exact-checkability and well-posedness are nearly orthogonal

*2026-06-28. Reproduce: `python scripts/fetch_gsm8k_platinum.py && python scripts/report.py`.*

## Numbers (real data, not the fixture)

| Measurement | Value |
|---|---|
| GSM8K test split audited | 1,319 items |
| **Trust denominator** (soundly exact-checkable) | **1,319 / 1,319 = 100.0%** |
| Structural defects found by deterministic rules | 0 |
| PlatinumBench GSM8K subset | 300 items |
| Human-identified defects (rejected + revised) | **33 / 300 = 11.0%** |
| Deterministic rules' **recall** on those 33 defects | **0 / 33 = 0.0%** |
| Deterministic rules' false positives on the 300 | 0 |

## What it means

GSM8K is **100% exact-checkable**: every answer key is a single clean number, so a
deterministic checker can grade it with no judge and no human. That is a real,
useful fact — it is the *high-soundness endpoint* of the spectrum this tool
measures (a free-text / LLM-judged benchmark would score far below 100%).

But exact-checkability says **nothing** about whether the questions are *well-posed*.
PlatinumBench's human review removed or corrected 11% of its GSM8K subset, and
**every one of those defects has a clean numeric answer** — they are semantic
(ambiguous quantities, missing constraints, "each"/scope confusion, a wrong key),
invisible to any check that only asks "is the answer key exact-checkable?".

Deterministic static rules recovered **0 of 33** of those defects. The one rule
that reached for semantics — flagging "`<subject> has some <noun>`" as an
underspecified start — scored **0% precision on real GSM8K** (3 flags, 3 false
positives: "has some savings … how much does she have?" is a *solve-for-the-unknown*
problem, not a defect) and was **retracted**.

## The honest conclusion

> **Structural gradeability is soundly automatable and near-total for a numeric
> benchmark. Semantic well-posedness is NOT soundly automatable by surface rules
> and must remain a clearly-labeled heuristic / human overlay.**

This is the sound-vs-heuristic separation the tool is built on, now *demonstrated
on real data* instead of asserted. The tool's value is making that boundary
explicit and refusing to paper over it with heuristics that fail silently — the
retraction above is the discipline working as intended.

## Caveats (do not overclaim)

- The 300 is PlatinumBench's **curated subset**, not a uniform random sample of
  the 1,319. The 11% is that subset's defect rate, **not** a GSM8K-wide rate.
- "Defect" = PlatinumBench's human judgment (rejected/revised). A different
  reviewer might draw the line differently.
- `recall 0/33` is a property of *these* rules, not a proof that no deterministic
  rule could help — but the observed defect types (semantic ambiguity) strongly
  suggest surface cues won't.

## Next experiment

Run the same audit on a benchmark whose items are **partly judge-dependent**
(free-text / LLM-graded). There the trust denominator should drop well below
100% — that is where a structural auditor earns its keep, and where this GSM8K
result serves as the all-sound calibration point.
