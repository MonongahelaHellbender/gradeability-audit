#!/usr/bin/env python3
"""Fetch the GSM8K config of madrylab/platinum-bench via the HuggingFace
datasets-server REST API (no auth, no `datasets` dependency) and write it in
gradeable's JSONL schema.

Gold label: PlatinumBench manually reviewed each item and set `cleaning_status`
to one of {consensus, verified, rejected, revised}. We treat as gold
"problematic" any item whose ORIGINAL GSM8K scoring is indefensible:
  * "rejected" = removed as defective (ambiguous / mislabeled / ill-posed)
  * "revised"  = the original answer key was wrong and got corrected
Items kept unchanged ("consensus" / "verified") are "clean".

`original_target` is the ORIGINAL GSM8K answer key — i.e. exactly what a GSM8K
run grades against — so it is the right reference_answer for an audit of GSM8K
as it is actually scored.

Output: data/gsm8k_platinum.jsonl  ({id, question, reference_answer, gold_label, meta})
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

DATASET = "madrylab/platinum-bench"
CONFIG = "gsm8k"
SPLIT = "test"
BASE = "https://datasets-server.huggingface.co/rows"
OUT = Path(__file__).resolve().parent.parent / "data" / "gsm8k_platinum.jsonl"


def fetch_page(offset: int, length: int = 100) -> dict:
    query = urllib.parse.urlencode(
        {"dataset": DATASET, "config": CONFIG, "split": SPLIT, "offset": offset, "length": length}
    )
    with urllib.request.urlopen(f"{BASE}?{query}", timeout=60) as resp:
        return json.load(resp)


def norm_answer(original_target) -> str:
    if isinstance(original_target, list):
        return str(original_target[0]).strip() if original_target else ""
    return str(original_target).strip()


def main() -> None:
    first = fetch_page(0)
    total = first["num_rows_total"]
    rows = list(first["rows"])
    while len(rows) < total:
        page = fetch_page(len(rows))
        if not page["rows"]:
            break
        rows.extend(page["rows"])
        time.sleep(0.2)

    counts: dict[str, int] = {}
    with OUT.open("w") as fh:
        for entry in rows:
            row = entry["row"]
            status = row.get("cleaning_status")
            counts[status] = counts.get(status, 0) + 1
            fh.write(json.dumps({
                "id": f"plat_{entry['row_idx']}",
                "question": row["question"],
                "reference_answer": norm_answer(row.get("original_target")),
                "gold_label": "problematic" if status in ("rejected", "revised") else "clean",
                "meta": {"cleaning_status": status},
            }) + "\n")

    print(f"wrote {len(rows)} items -> {OUT}")
    print("cleaning_status counts:", counts)


if __name__ == "__main__":
    main()
