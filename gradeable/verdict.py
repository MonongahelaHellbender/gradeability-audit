from __future__ import annotations

from enum import Enum


class Verdict(str, Enum):
    """Gradeability verdict for a single benchmark item.

    Mirrors the trust-lane spine (supported / needs-query / refused) applied to
    *whether an item can be soundly graded* — NOT whether its answer is correct.
    Only EXACT_CHECKABLE items count toward the trust denominator.
    """

    # supported: an exact checker (numeric / string / symbolic / unit-test) can
    # verify the reference answer with no semantic judgment.
    EXACT_CHECKABLE = "exact-checkable"

    # needs-query: grading the item requires a semantic judge (an LLM or a human).
    # Sound only relative to that judge; does NOT count toward the denominator.
    JUDGE_DEPENDENT = "judge-dependent"

    # refused: the item is internally contradictory, admits multiple valid
    # answers, is underspecified, or its answer key is indefensible. Not soundly
    # gradeable by anyone.
    ILL_POSED = "ill-posed"

    @property
    def soundly_gradeable(self) -> bool:
        return self is Verdict.EXACT_CHECKABLE
