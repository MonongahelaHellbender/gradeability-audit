# gradeable — the trust denominator of a benchmark

A deterministic, **annotation-free** auditor that answers one question per
benchmark item, with no model calls and no human in the loop:

> Can this item's reference answer be verified by an exact checker?

From that it reports a benchmark's **trust denominator**: of the *N* items a
benchmark advertises as gradeable, how many are *soundly* gradeable. The rest
either need a semantic judge or are ill-posed.

```
$ python -m gradeable --demo
=== gradeability audit ===
items advertised:        12
soundly gradeable:       10  (83.3%  <- trust denominator)
judge-dependent:         0
ill-posed:               2
...
=== validation ===
  precision=1.000  recall=0.500  f1=0.667
```

## What this is — and what it is NOT

It decides **gradeability**, not correctness. It does **not** judge whether an
answer is right, whether a model cheated, or whether an item was contaminated.
Those are separate, largely *heuristic* questions; this tool is the *sound* core
that those heuristic overlays attach to later.

**Banned overclaim:** never call a benchmark "soundly verified" or "clean"
because of this tool. It verifies that an item is *exact-checkable* — nothing
about the answer key's truth.

## Honest prior-art statement

The component measurements here are **reproductions of named prior work**, not
discoveries:

- label-error / ambiguity rates — MMLU-Redux, "Are We Done with MMLU?",
  GSM8K-Platinum / PlatinumBench (MIT CSAIL)
- contamination detection — see the contamination-detection survey (arXiv 2404.00699)
- gameability — length-controlled AlpacaEval; "One Token to Fool LLM-as-a-Judge"
- whole-benchmark meta-audit — BetterBench (arXiv 2411.12990)

**And the trust denominator itself is not new — it is standard practice in five other fields,
where reporting it is mandatory rather than optional:**

- **AAPOR Standard Definitions** (1998–) — response rates computed over *defined dispositions*,
  with every non-response classified by mechanism before any rate is reported. RR1 is a trust
  denominator.
- **NHS Diabetic Eye Screening Programme** — the *ungradable* rate is reported alongside screening
  results as a first-class quality measure.
- **ISO 26262** — *diagnostic coverage*: the fraction of faults a safety mechanism can actually
  detect, stated explicitly rather than assumed complete.
- **ETS e-rater advisory flags** — essays the automated scorer declines to score, surfaced rather
  than silently scored.
- **STARD** (diagnostic accuracy reporting) — *indeterminate* results reported separately from
  positives and negatives.
- **Chow (1970)** — the reject option and the error-versus-coverage tradeoff.
- **bpref** (Buckley & Voorhees) — IR evaluation designed to be robust to incomplete judgments.

The ML-specific novelty is therefore narrow: applying an established reporting discipline to LLM
benchmarks, where it is currently absent.

**The contribution is two things those don't provide:**

1. A **deterministic, annotation-free** gradeability classifier. Existing audits
   need a human or an LLM in the loop, so the audit inherits the soundness
   problem it measures. A purely static classifier breaks that regress for the
   fraction it can decide and **honestly abstains** on the rest.
2. A single per-benchmark **trust denominator** that aggregates the scattered
   audit axes with the **sound part strictly separated** from the heuristic ones.

The classifier is **validated against** the human-annotated cleaned sets
(GSM8K-Platinum, MMLU-Redux): we report precision/recall of our flags vs. their
gold labels (see `gradeable/validate.py`). The tool is only as good as that
number, and we publish it.

## The rules are the product

`gradeable/rules.py` holds the gradeability rules — deterministic, conservative,
benchmark-aware functions that each *downgrade* an item with a stated reason.
They are meant to be **named, cited, and forkable**: disagree with a flag? change
a rule and re-run. Bias is toward **not** flagging — precision must stay high;
recall is the number you grow.

Two **sound** rules are live — `answer_not_clean_number` and
`internal_contradiction` — both narrow, high-precision, zero false positives on
1,619 real items. A third, `underspecified_non_derivable`, was **retracted**
after scoring 0% precision on real GSM8K (kept in the file as a documented
warning). Two remain as stubs (`multiple_candidate_answers`,
`unit_or_rounding_ambiguity`). The retraction is the point: a rule that fails on
real data gets disabled, not relaxed.

## Run

```
python -m gradeable --demo                 # bundled offline fixture
python -m gradeable --input path/to.jsonl  # your benchmark (id, question, reference_answer)
python -m unittest discover -s tests       # tests (also pytest-compatible)
```

No dependencies beyond the Python standard library (3.10+).

## Status

v0.2 — sound core + validation harness + per-grader rule profiles, run on real
data across three benchmarks. **Write-up: [`WRITEUP.md`](WRITEUP.md)** (the
deliverable); raw findings log in [`FINDINGS.md`](FINDINGS.md):

- **Finding 01 (GSM8K):** trust denominator 100% (fully exact-checkable) yet 11%
  of PlatinumBench's subset is semantically defective and deterministic rules
  recover 0/33 — exact-checkability ⟂ well-posedness. One rule retracted after
  failing on real data.
- **Finding 02 (HotpotQA):** the denominator **discriminates** — exact-match over
  free text isn't paraphrase/alias-invariant, so most items are judge-dependent.
- **Finding 03 (spectrum):** one comparable number across benchmarks —
  **GSM8K 100% → DROP 72.4% → HotpotQA 11.6%** exact-checkable. DROP splits
  *within* one benchmark (181 numeric exact-checkable / 69 span judge-dependent).
  The number is about the *grader*, not the questions.

```
TRUST DENOMINATOR — spectrum
  GSM8K     100.0%  ########################################  (numeric equality)
  DROP       72.4%  #############################             (exact-match / F1)
  HotpotQA   11.6%  #####                                     (exact-match / F1)
```

Reproduce: `python scripts/fetch_platinum.py gsm8k && python scripts/fetch_platinum.py hotpotqa && python scripts/fetch_platinum.py drop && python scripts/report.py`.

Next: **write up the spectrum** (it's the deliverable) — not another benchmark.

---

*Part of a portfolio of refusal-first AI-assurance & verification tools — [github.com/MonongahelaHellbender](https://github.com/MonongahelaHellbender). Related: [rag-triad](https://github.com/MonongahelaHellbender/rag-triad) · [honesty-atlas](https://github.com/MonongahelaHellbender/honesty-atlas) · [assurance-compiler](https://github.com/MonongahelaHellbender/assurance-compiler) · [gradeability-audit](https://github.com/MonongahelaHellbender/gradeability-audit) · [oracle-shield](https://github.com/MonongahelaHellbender/oracle-shield) · [rag-assurance](https://github.com/MonongahelaHellbender/rag-assurance).*
