# The Trust Denominator

### What fraction of a benchmark score actually rests on a sound grader?

A leaderboard number like "82% on HotpotQA" quietly assumes the grader was right
about which answers to count. For some benchmarks that assumption is free; for
others it carries most of the score. This is a small, deterministic tool that
measures the difference, and reports one comparable number per benchmark.

It does **not** decide whether answers are correct, whether a model cheated, or
whether the data was contaminated. It asks one narrow, checkable question per
item and aggregates the result.

---

## A definition first

Call an item **soundly gradeable** under a given grader if that grader marks a
response correct **iff the response actually is correct** — no false positives,
no false negatives. Soundness is a property of the *(item, grader)* pair, not of
the question alone.

The **trust denominator** of a benchmark is the fraction of its items that are
soundly gradeable by *its own grader*. 100% means every point on the leaderboard
is backed by a grader that can't be wrong about it. Lower means some of the score
rides on a grader that can be.

This is deliberately not a claim about difficulty, contamination, or answer-key
correctness. It is the narrowest thing you can say and still say something sound.

## The tool

For each item, a deterministic classifier (no model calls, no annotators, no
network) assigns one of three verdicts, mirroring a simple trust spine:

- **exact-checkable** — the gold answer has a canonical form (a number, or a
  closed label like yes/no) and the grader's check is sound for it.
- **judge-dependent** — grading the item correctly needs semantic judgment,
  because the grader (string equality / token overlap) is *not* sound for this
  answer type.
- **ill-posed** — the item is internally contradictory or underspecified;
  not soundly gradeable by anyone.

The rule set is chosen per benchmark *grader*: a numeric-equality profile for
GSM8K, an exact-match/F1 profile for free-text QA. The denominator is just the
exact-checkable fraction.

## The result: a spectrum

Run across three benchmarks (PlatinumBench's curated subsets, plus the full GSM8K
test split), the denominator moves the way it should — it tracks how much of each
benchmark's answers have a canonical form its grader can soundly check:

```
TRUST DENOMINATOR
  GSM8K     100.0%  ########################################  (numeric equality)
  DROP       72.4%  #############################             (exact-match / F1)
  HotpotQA   11.6%  #####                                     (exact-match / F1)
```

- **GSM8K**: every answer is a number; numeric equality is sound; denominator 100%.
- **DROP**: a real mix — of 250 items, 181 numeric answers are exact-checkable and
  69 free-text spans are judge-dependent. The denominator splits *within one
  benchmark*, landing between the all-numeric and all-free-text ends because its
  answer mix is between them.
- **HotpotQA**: 221 of 250 answers are free-text entities/phrases; only 29
  (numbers + yes/no) are soundly checkable.

The same number, computed the same way, for any benchmark.

## "But nobody grades HotpotQA with naive exact-match"

This is the objection that matters, so here it is head-on. Real harnesses use
token-**F1** and answer **normalization** (lowercasing, stripping articles and
punctuation), not bare string equality. Doesn't that recover most of the 88%?

No — because **F1 and normalization fail the soundness definition too**, in *both*
directions, on free-text answers:

- **False negatives.** Gold `JFK`, response `John F. Kennedy`: correct, but the
  two strings share no tokens at all — EM is 0 **and** token-F1 is 0. Marked wrong.
- **False positives.** Gold `George Washington Carver`, response `George
  Washington`: wrong person, but high token-F1 overlap. Marked (partly) right.
- **Normalization** fixes case, articles, and punctuation. It does **nothing** for
  aliasing (`U.S.` / `United States` / `America`), paraphrase, or partial-overlap
  collisions.

So for a free-text answer, *no* deterministic string metric is sound — getting it
right requires semantic judgment. That is exactly what "judge-dependent" means.
The free-text side of the denominator is therefore **robust to the choice of
string metric**: it doesn't move when you swap EM for F1. If anything the reported
denominator is a *generous* upper bound on soundness, since it credits every bare
number as cleanly checkable.

## Three axes, not one

The three verdict buckets measure three *different* things, and it's a mistake to
collapse them:

1. **exact-checkable vs judge-dependent** — is the *grader* sound for this item?
2. **well-posed vs ill-posed** — is the *question* answerable as written?
3. **right vs wrong key** — is the *answer key* itself correct?

These are orthogonal. PlatinumBench's human "rejected/revised" labels gold only
axis 2–3 (well-posedness and key correctness). They say nothing about axis 1. So
this tool **refuses** to score its judge-dependent predictions against those
labels — doing so would be a category error. On GSM8K the deterministic rules
recover 0 of 33 human-flagged defects, precisely because those defects live on a
different axis (every one has a clean numeric answer). A benchmark can be perfectly
well-posed *and* not soundly gradeable; the point is to stop conflating the two.

## What's new here, and what isn't

Almost nothing here is a new observation:

- That exact-match is brittle for free-text QA is textbook (SQuAD's EM-vs-F1 gap;
  the answer-equivalence literature).
- That popular benchmarks carry label noise is well documented (MMLU-Redux,
  GSM8K-Platinum / PlatinumBench, and the high revised/rejected rates seen here
  for HotpotQA and DROP are known issues).

The contribution is **not a finding**. It is (a) a single deterministic,
annotation-free, model-free number that is computed the same way for any
benchmark, so denominators are comparable; and (b) the discipline of separating
what is soundly automatable (numeric/closed-label grading) from what is not
(everything else), and refusing to let a heuristic masquerade as a sound check.
This is a reproduction plus a tool, not a discovery.

## Honest limits

- **Curated subsets.** The PlatinumBench slices are manually-reviewed subsets of a
  few hundred items each, not the full benchmarks. The denominators are computed
  over those slices (and the full GSM8K test split); they are not population
  estimates of each benchmark.
- **Dates.** DROP's "exact-checkable" fraction partly tracks date *formatting*: a
  bare year (`1944`) reads as a number and counts as checkable, while `March 1944`
  reads as multi-token and counts as judge-dependent. Defensible (raw matching is
  brittle on the latter) but worth seeing.
- **It checks gradeability, not truth.** A benchmark scoring 100% here is not
  "verified" or "clean" — only that its grader is sound *given* a correct key.
  Never read the denominator as a quality seal.
- **Contamination and gameability are out of scope** by design. Those are
  irreducibly heuristic (you can't prove a model never saw an item without its
  training data); folding them in would contaminate a sound number with guesses.

## Use it

```bash
python scripts/fetch_platinum.py gsm8k
python scripts/fetch_platinum.py hotpotqa
python scripts/fetch_platinum.py drop
python scripts/report.py          # prints the spectrum above
```

Before trusting a leaderboard, compute its trust denominator. If most of the
score sits on judge-dependent items, the number you're comparing is a measurement
of a grader as much as of a model — and you should know which.
