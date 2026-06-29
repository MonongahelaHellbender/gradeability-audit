from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_FIXTURE = _DATA_DIR / "fixture.jsonl"


@dataclass(frozen=True)
class BenchmarkItem:
    """One benchmark item, normalized.

    reference_answer is the benchmark's official answer key, as a string. For a
    numeric benchmark (e.g. GSM8K) this should already be reduced to the final
    answer (the loader strips GSM8K's "#### 42" wrapping).

    gold_label is an OPTIONAL human-annotated quality label from a cleaned
    counterpart set (e.g. GSM8K-Platinum / MMLU-Redux): "clean" or "problematic".
    It is used only to *validate* the classifier — never as an input to it.
    """

    id: str
    question: str
    reference_answer: str
    gold_label: Optional[str] = None  # "clean" | "problematic" | None
    meta: dict = field(default_factory=dict)


def _row_to_item(row: dict) -> BenchmarkItem:
    return BenchmarkItem(
        id=str(row["id"]),
        question=row["question"],
        reference_answer=str(row["reference_answer"]),
        gold_label=row.get("gold_label"),
        meta=row.get("meta", {}),
    )


def load_jsonl(path) -> list[BenchmarkItem]:
    """Load items from a JSONL file with keys: id, question, reference_answer,
    [gold_label], [meta]."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. See data/README.md for how to fetch a real "
            f"benchmark, or use load_fixture() for the bundled offline demo."
        )
    items: list[BenchmarkItem] = []
    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if line:
                items.append(_row_to_item(json.loads(line)))
    return items


def load_fixture() -> list[BenchmarkItem]:
    """The bundled, hand-labeled demo set. Runs fully offline; used by the tests
    and by `python -m gradeable --demo`."""
    return load_jsonl(_FIXTURE)


# --------------------------------------------------------------------------- #
# Real-benchmark loaders. These expect locally-downloaded files (see
# data/README.md). They are kept thin and deterministic on purpose.
# --------------------------------------------------------------------------- #

def load_gsm8k(path) -> list[BenchmarkItem]:
    """Load GSM8K (the canonical jsonl: keys `question`, `answer`, where `answer`
    ends with `#### <final>`). Reduces each answer to its final value."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. See data/README.md.")
    items: list[BenchmarkItem] = []
    with path.open() as fh:
        for i, line in enumerate(fh):
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            answer = str(row["answer"])
            final = answer.split("####")[-1].strip() if "####" in answer else answer.strip()
            items.append(
                BenchmarkItem(
                    id=str(row.get("id", i)),
                    question=row["question"],
                    reference_answer=final,
                    meta={"raw_answer": answer},
                )
            )
    return items


def attach_platinum_gold(items: list[BenchmarkItem], problematic_ids: set[str]) -> list[BenchmarkItem]:
    """Attach gold labels from a cleaned counterpart set.

    `problematic_ids` is the set of original-item ids that the cleaned set
    removed or revised (i.e. flagged as defective). Everything else is labeled
    "clean". Build this set from the PlatinumBench / GSM8K-Platinum release.

    TODO (you): confirm the exact field names in the downloaded Platinum file
    and the id alignment with GSM8K before trusting these labels — the precision/
    recall numbers are only as honest as this mapping.
    """
    return [
        BenchmarkItem(
            id=it.id,
            question=it.question,
            reference_answer=it.reference_answer,
            gold_label="problematic" if it.id in problematic_ids else "clean",
            meta=it.meta,
        )
        for it in items
    ]
