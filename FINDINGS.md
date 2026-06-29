# Finding 01 — GSM8K: exact-checkability and well-posedness are nearly orthogonal

*2026-06-28. Reproduce: `python scripts/fetch_platinum.py gsm8k && python scripts/report.py`.*

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

---

# Finding 02 — the trust denominator discriminates: GSM8K 100% vs HotpotQA 11.6%

*2026-06-29. Reproduce: `python scripts/fetch_platinum.py hotpotqa && python scripts/report.py`.*

Finding 01 left GSM8K at a trivial 100% (its grader, numeric equality, is sound
for every item). The open question was whether the denominator *moves* on a
benchmark with a different grader. It does.

## Numbers

| Benchmark | Grader | **Trust denominator** (exact-checkable) | Gold key-defect rate |
|---|---|---|---|
| GSM8K (1,319) | numeric equality | **100.0%** | 11% (curated 300) |
| HotpotQA (250) | exact-match / token-F1 | **11.6%** | 63% (curated 250) |

HotpotQA's 11.6% = 16 numeric + 13 yes/no answers; the other **221/250 are
judge-dependent**, because exact-match over free-text answers (entities, phrases,
even single tokens like `albany` / `u2`) is not invariant to case, articles,
morphology, or aliasing. The `JUDGE_DEPENDENT` bucket — empty for GSM8K — is now
the majority verdict.

## Forecast vs result (forecast-first, logged before the run)

Predicted 15–40% exact-checkable, "carried by yes/no + numeric." Actual **11.6%**,
just below the predicted floor: I underweighted that the 20% single-token entity
answers are *also* EM-brittle and conservatively classify as judge-dependent.
Direction correct, floor too high. Logged as a miss.

## The honest scope line (the orthogonality, again)

The `JUDGE_DEPENDENT` count is **not** validated against the gold labels, and the
report refuses to compute a precision/recall for it. `cleaning_status` golds
*well-posedness* (the ill-posed axis); exact-checkability is a different axis — a
HotpotQA item can be perfectly well-posed **and** judge-dependent. Scoring one
against the other is a category error. So the three verdict buckets measure three
orthogonal things, and the human gold only golds one of them. (Finding 01 showed
exact ⟂ ill-posed; this shows judge ⟂ ill-posed too.)

Separately and orthogonally: HotpotQA's original answer keys are **63% defective**
on this curated subset (mostly `revised` = the original key was wrong) — a known
HotpotQA label-noise issue (**prior art, not a finding here**). Under its standard
exact-match grading HotpotQA is thus doubly compromised: most items aren't soundly
EM-gradeable *and* most keys were wrong. GSM8K is the clean contrast on both axes.

## Prior-art gate

EM/F1 brittleness on free-text QA is textbook (SQuAD EM-vs-F1; answer-equivalence
work). **Not a finding.** The contribution is unchanged from v0.1: a deterministic
per-item gradeability classifier producing a **comparable cross-benchmark trust
denominator**, with the grader-soundness boundary made explicit. Reproduction +
tool.

## Caveats

- The 250 is PlatinumBench's **curated** HotpotQA subset (model-disagreement-
  enriched), not uniform HotpotQA; the 63% is that subset's rate.
- The denominator is scoped to the benchmark's *actual* grader (EM/F1). A
  benchmark that shipped an alias set or a judge would score differently — which
  is exactly the point: the number is about the grader, not the questions.

## Next experiment

→ done: DROP, Finding 03.

---

# Finding 03 — the denominator is a comparable cross-benchmark statistic (+ intra-benchmark split)

*2026-06-29. Reproduce: `python scripts/fetch_platinum.py drop && python scripts/report.py`.*

DROP grades by exact-match/F1 like HotpotQA, but its answers are a real **mix** of
numbers and free-text spans — so it tests whether the denominator splits *within*
one benchmark, not just across two.

## The spectrum (the deliverable)

| Benchmark | Grader | **Trust denominator** | Verdict split |
|---|---|---|---|
| GSM8K | numeric equality | **100.0%** | exact 1319 / judge 0 |
| DROP | exact-match / F1 | **72.4%** | exact 181 / judge 69 |
| HotpotQA | exact-match / F1 | **11.6%** | exact 29 / judge 221 |

DROP splits **within one benchmark**: 181 numeric answers are exact-checkable, 69
span / single-token answers are judge-dependent. The denominator lands between the
all-numeric (GSM8K) and all-free-text (HotpotQA) ends because DROP's answer *mix*
is between them. That is the whole claim: **one comparable number, computed the
same way for any benchmark, that says what fraction of its score rests on a sound
grader.**

## Forecast vs result (forecast-first)

Predicted 40–65% exact-checkable; actual **72.4%** — above my ceiling (DROP's
curated subset is 72% numeric, more than I assumed). Combined with Finding 02
(predicted 15–40%, got 11.6%, below floor), I have now missed the *magnitude* in
both directions while getting the *direction* right both times. Honest takeaway:
my qualitative ordering forecasts hold; my point-range estimates of answer-type
mix are not reliable — I should stop quoting tight ranges I can't ground.

## Caveats

- Same as Findings 01–02: PlatinumBench **curated** subsets (model-disagreement-
  enriched), scoped to the benchmark's actual grader.
- DROP **date** answers are a known soft spot of the simple rule: a bare-year date
  (`1944`) reads as a number → exact-checkable, while `March 1944` reads as
  multi-token → judge-dependent. Defensible (raw EM *is* brittle on the latter),
  but it means "exact-checkable" for DROP partly tracks date *formatting*. Noted,
  not hidden.
- Gold key-defect rate climbs across the three (GSM8K 11% → HotpotQA 63% → DROP
  88%), orthogonal to the denominator and **prior art** (known label noise in
  HotpotQA/DROP), not a finding here.

## Where this stops (ship discipline)

Three benchmarks is enough to make the deliverable: a comparable trust-denominator
**spectrum** + the two orthogonality lessons (exact ⟂ ill-posed, judge ⟂ ill-posed).
A fourth benchmark is procrastination from writing it up. **Next is the short
artifact, not another fetch.**
