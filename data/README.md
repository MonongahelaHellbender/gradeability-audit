# Data

`fixture.jsonl` is a tiny, hand-labeled demo set bundled with the repo. It runs
fully offline and backs the tests and `python -m gradeable --demo`. It is
synthetic — do not cite its numbers as a real benchmark audit.

## Fetching real benchmarks (for the v0.1 result)

Everything below is downloaded locally and read by the loaders in
`gradeable/item.py`. No network at runtime.

### GSM8K (the target)
- Canonical source: HuggingFace `openai/gsm8k`, config `main`, `test` split
  (1,319 items). Export to JSONL with keys `question`, `answer` (the `answer`
  field ends with `#### <final number>`; `load_gsm8k` strips it).

### GSM8K-Platinum (the gold signal)
- From the PlatinumBench release (MIT CSAIL): http://platinum-bench.csail.mit.edu/
- It is a *cleaned / filtered* version of GSM8K. The gold signal you want is the
  set of original GSM8K item ids that Platinum **removed or revised** — those are
  the human-annotated "problematic" items. Build that id set and pass it to
  `attach_platinum_gold(items, problematic_ids)`.

> ⚠️ TODO before trusting validation numbers: confirm the exact field names and
> the id alignment between the GSM8K and Platinum files. The precision/recall is
> only as honest as that mapping. If ids don't align directly, align on
> normalized question text and record the match rate.

### MMLU / MMLU-Redux (natural second target, v0.2)
- MMLU-Redux is the human-reannotated subset; same pattern — its corrections are
  the gold "problematic" labels.
