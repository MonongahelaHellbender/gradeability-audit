from __future__ import annotations

from dataclasses import dataclass, field

from .classify import ClassifiedItem, classify
from .item import BenchmarkItem
from .rules import REGISTRY, Rule
from .verdict import Verdict


@dataclass
class AuditReport:
    n_total: int
    counts: dict[Verdict, int]
    classified: list[ClassifiedItem] = field(default_factory=list)

    @property
    def soundly_gradeable_fraction(self) -> float:
        """THE trust denominator: fraction of advertised items that are soundly
        (exact-) gradeable with no judge and no defects."""
        if self.n_total == 0:
            return 0.0
        return self.counts.get(Verdict.EXACT_CHECKABLE, 0) / self.n_total

    @property
    def flagged(self) -> list[ClassifiedItem]:
        return [c for c in self.classified if not c.soundly_gradeable]

    def summary(self) -> str:
        lines = [
            f"items advertised:        {self.n_total}",
            f"soundly gradeable:       {self.counts.get(Verdict.EXACT_CHECKABLE, 0)}"
            f"  ({self.soundly_gradeable_fraction:.1%}  <- trust denominator)",
            f"judge-dependent:         {self.counts.get(Verdict.JUDGE_DEPENDENT, 0)}",
            f"ill-posed:               {self.counts.get(Verdict.ILL_POSED, 0)}",
        ]
        return "\n".join(lines)


def audit(items: list[BenchmarkItem], rules: list[Rule] = REGISTRY) -> AuditReport:
    classified = [classify(it, rules) for it in items]
    counts: dict[Verdict, int] = {v: 0 for v in Verdict}
    for c in classified:
        counts[c.verdict] += 1
    return AuditReport(n_total=len(items), counts=counts, classified=classified)
