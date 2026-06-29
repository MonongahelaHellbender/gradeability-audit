#!/usr/bin/env python3
"""Fetch any config of madrylab/platinum-bench via the HuggingFace
datasets-server REST API (no auth, no `datasets` dependency) and write it in
gradeable's JSONL schema.

    python scripts/fetch_platinum.py gsm8k       # numeric benchmark
    python scripts/fetch_platinum.py hotpotqa    # free-text benchmark
    python scripts/fetch_platinum.py drop        # mixed (numbers + spans)

platinum-bench shares one schema across configs:
  * question            -- the original benchmark question
  * original_target     -- the ORIGINAL benchmark answer key (what the benchmark
                           actually grades against); the right reference_answer
  * cleaning_status     -- PlatinumBench's manual review verdict, one of
                           {consensus, verified, revised, rejected}

Gold label (well-posedness axis only): "problematic" iff cleaning_status is
"rejected" (removed as defective) or "revised" (original key was wrong). Items
kept unchanged (consensus / verified) are "clean".

Output: data/<config>_platinum.jsonl  ({id, question, reference_answer, gold_label, meta})
"""
from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

DATASET = "madrylab/platinum-bench"
SPLIT = "test"
BASE = "https://datasets-server.huggingface.co/rows"
DATA = Path(__file__).resolve().parent.parent / "data"


def fetch_page(config: str, offset: int, length: int = 100) -> dict:
    query = urllib.parse.urlencode(
        {"dataset": DATASET, "config": config, "split": SPLIT, "offset": offset, "length": length}
    )
    with urllib.request.urlopen(f"{BASE}?{query}", timeout=60) as resp:
        return json.load(resp)


def norm_answer(original_target) -> str:
    if isinstance(original_target, list):
        return str(original_target[0]).strip() if original_target else ""
    return str(original_target).strip()


def main(config: str) -> None:
    out = DATA / f"{config}_platinum.jsonl"
    first = fetch_page(config, 0)
    total = first["num_rows_total"]
    rows = list(first["rows"])
    while len(rows) < total:
        page = fetch_page(config, len(rows))
        if not page["rows"]:
            break
        rows.extend(page["rows"])
        time.sleep(0.2)

    counts: dict[str, int] = {}
    with out.open("w") as fh:
        for entry in rows:
            row = entry["row"]
            status = row.get("cleaning_status")
            counts[status] = counts.get(status, 0) + 1
            fh.write(json.dumps({
                "id": f"{config}_{entry['row_idx']}",
                "question": row["question"],
                "reference_answer": norm_answer(row.get("original_target")),
                "gold_label": "problematic" if status in ("rejected", "revised") else "clean",
                "meta": {"cleaning_status": status},
            }) + "\n")

    print(f"wrote {len(rows)} items -> {out}")
    print("cleaning_status counts:", counts)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "gsm8k")
