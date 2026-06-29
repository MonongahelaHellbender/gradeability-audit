from __future__ import annotations

from dataclasses import dataclass

from .classify import ClassifiedItem, classify
from .item import BenchmarkItem
from .rules import REGISTRY, Rule

# The classifier's "positive" prediction = item is NOT soundly gradeable
# (verdict != EXACT_CHECKABLE). Gold positive = an annotated cleaned set flagged
# the item as "problematic". We score the classifier against that gold signal,
# considering only items that carry a gold label.


@dataclass
class ValidationReport:
    n_labeled: int
    tp: int
    fp: int
    fn: int
    tn: int

    @property
    def precision(self) -> float:
        denom = self.tp + self.fp
        return self.tp / denom if denom else float("nan")

    @property
    def recall(self) -> float:
        denom = self.tp + self.fn
        return self.tp / denom if denom else float("nan")

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        if not (p == p) or not (r == r) or (p + r) == 0:  # nan-safe
            return float("nan")
        return 2 * p * r / (p + r)

    def summary(self) -> str:
        return (
            f"validated against gold labels on {self.n_labeled} items\n"
            f"  TP={self.tp}  FP={self.fp}  FN={self.fn}  TN={self.tn}\n"
            f"  precision={self.precision:.3f}  recall={self.recall:.3f}  f1={self.f1:.3f}\n"
            f"  (precision = of items we flagged, how many the gold set agrees are bad;\n"
            f"   recall    = of gold-bad items, how many we caught. Grow recall, guard precision.)"
        )


def validate(items: list[BenchmarkItem], rules: list[Rule] = REGISTRY) -> ValidationReport:
    tp = fp = fn = tn = 0
    n_labeled = 0
    for it in items:
        if it.gold_label is None:
            continue
        n_labeled += 1
        gold_bad = it.gold_label == "problematic"
        pred_bad = not classify(it, rules).soundly_gradeable
        if pred_bad and gold_bad:
            tp += 1
        elif pred_bad and not gold_bad:
            fp += 1
        elif not pred_bad and gold_bad:
            fn += 1
        else:
            tn += 1
    return ValidationReport(n_labeled=n_labeled, tp=tp, fp=fp, fn=fn, tn=tn)
