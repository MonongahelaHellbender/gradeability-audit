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

One example rule (`answer_not_clean_number`) is implemented; the rest are stubs
with design notes for you to fill in.

## Run

```
python -m gradeable --demo                 # bundled offline fixture
python -m gradeable --input path/to.jsonl  # your benchmark (id, question, reference_answer)
python -m unittest discover -s tests       # tests (also pytest-compatible)
```

No dependencies beyond the Python standard library (3.10+).

## Status

v0.1 — sound core + offline fixture + validation harness. Next: wire in real
GSM8K + GSM8K-Platinum (see `data/README.md`), write the stub rules, report the
real trust denominator and validation numbers, write it up.
