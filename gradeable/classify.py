from __future__ import annotations

from dataclasses import dataclass, field

from .item import BenchmarkItem
from .rules import REGISTRY, Rule, RuleResult
from .verdict import Verdict

# How restrictive each verdict is. The classifier reports the strongest verdict
# any rule fires (ill-posed beats judge-dependent beats the exact-checkable default).
_SEVERITY = {
    Verdict.EXACT_CHECKABLE: 0,
    Verdict.JUDGE_DEPENDENT: 1,
    Verdict.ILL_POSED: 2,
}


@dataclass(frozen=True)
class ClassifiedItem:
    item: BenchmarkItem
    verdict: Verdict
    fired: list[RuleResult] = field(default_factory=list)

    @property
    def soundly_gradeable(self) -> bool:
        return self.verdict.soundly_gradeable


def classify(item: BenchmarkItem, rules: list[Rule] = REGISTRY) -> ClassifiedItem:
    """Run every rule. Default verdict is EXACT_CHECKABLE; rules can only
    downgrade. The reported verdict is the most restrictive one that fired."""
    fired: list[RuleResult] = []
    for rule in rules:
        result = rule(item)
        if result is not None:
            fired.append(result)

    verdict = Verdict.EXACT_CHECKABLE
    for result in fired:
        if _SEVERITY[result.verdict] > _SEVERITY[verdict]:
            verdict = result.verdict

    # Report the fired results ordered by severity (strongest first) for readable output.
    fired.sort(key=lambda r: _SEVERITY[r.verdict], reverse=True)
    return ClassifiedItem(item=item, verdict=verdict, fired=fired)
