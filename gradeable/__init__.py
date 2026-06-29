"""gradeable — a deterministic, annotation-free auditor of benchmark *gradeability*.

It answers ONE question per benchmark item, with no model calls and no human in
the loop:

    Can this item's reference answer be verified by an exact checker?

From that it reports a per-benchmark **trust denominator**: of the N items a
benchmark advertises as gradeable, how many are *soundly* gradeable. The
remainder either need a semantic judge or are ill-posed.

It does NOT decide whether an answer is correct, whether a model cheated, or
whether the item was contaminated. Those are separate (and largely heuristic)
questions. Keeping them separate is the point.
"""

from .verdict import Verdict
from .item import BenchmarkItem, load_jsonl, load_fixture
from .classify import classify, ClassifiedItem
from .audit import audit, AuditReport
from .validate import validate, ValidationReport

__all__ = [
    "Verdict",
    "BenchmarkItem",
    "load_jsonl",
    "load_fixture",
    "classify",
    "ClassifiedItem",
    "audit",
    "AuditReport",
    "validate",
    "ValidationReport",
]

__version__ = "0.1.0"
