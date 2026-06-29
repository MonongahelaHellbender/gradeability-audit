"""The gradeability rules — THIS FILE IS THE CONTESTABLE PRODUCT.

A rule is a pure function `(item) -> Optional[RuleResult]`:
  * It only ever DOWNGRADES an item from the default EXACT_CHECKABLE to
    JUDGE_DEPENDENT or ILL_POSED. It never upgrades.
  * It must return a human-readable `reason`.
  * It is deterministic: no model calls, no network, no randomness, no clock.

Design stance (this is the whole honesty argument of the tool):
  Be CONSERVATIVE. When in doubt, return None (do not flag). That keeps
  precision high — every item you flag as ill-posed should be defensibly
  ill-posed to a skeptical reader. Recall is the number you grow over time by
  adding rules; precision is the number you must not sacrifice. The trust
  denominator is only trustworthy if false flags are near zero.

Rules are benchmark-aware. The ones below assume a NUMERIC-answer benchmark
(GSM8K-style): the official answer key is supposed to be a single number.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, Optional

from .item import BenchmarkItem
from .verdict import Verdict


@dataclass(frozen=True)
class RuleResult:
    verdict: Verdict  # ILL_POSED or JUDGE_DEPENDENT — rules only downgrade
    reason: str
    rule: str


Rule = Callable[[BenchmarkItem], Optional[RuleResult]]


# Matches a single "clean" number: optional sign, optional $, thousands
# separators, optional decimal, optional trailing %. e.g. 42  -7  $1,200  0.5  30%
_CLEAN_NUMBER = re.compile(
    r"^[-+]?\$?\d{1,3}(?:,\d{3})+(?:\.\d+)?%?$"   # with thousands separators
    r"|^[-+]?\$?\d+(?:\.\d+)?%?$"                 # plain integer / decimal
)

# Age-contradiction detection (narrow): "<subject> is [also] <n> years old".
_AGE = re.compile(
    r"\b(\w+)\s+is\s+(?:also\s+|now\s+|actually\s+)?(\d+)\s+years\s+old",
    re.IGNORECASE,
)
# Any temporal cue means two stated ages may refer to different times -> abstain.
_TEMPORAL = re.compile(
    r"\b(?:ago|later|was|were|will\s+be|then|before|after|previously|since)\b",
    re.IGNORECASE,
)


def _final_answer(item: BenchmarkItem) -> str:
    ans = item.reference_answer.strip()
    if "####" in ans:
        ans = ans.split("####")[-1].strip()
    return ans


# --------------------------------------------------------------------------- #
# IMPLEMENTED EXAMPLE RULE — kept deliberately simple so the pipeline runs and
# you have a working template to copy.
# --------------------------------------------------------------------------- #

def answer_not_clean_number(item: BenchmarkItem) -> Optional[RuleResult]:
    """For a numeric benchmark, the answer key must be a single clean number.
    If it isn't (e.g. "12 or 15", "many", "about 7"), an exact numeric checker
    cannot soundly grade it, so the item is ill-posed *as a numeric item*.
    """
    ans = _final_answer(item)
    if _CLEAN_NUMBER.match(ans):
        return None
    return RuleResult(
        verdict=Verdict.ILL_POSED,
        reason=f"reference answer {ans!r} is not a single clean number",
        rule="answer_not_clean_number",
    )


# --------------------------------------------------------------------------- #
# RULES FOR YOU TO WRITE.
#
# Each stub below is a real, registered rule that currently returns None (no
# effect). Fill in the body and the trust denominator + validation numbers move
# immediately. These are the judgment calls that make the tool yours — there is
# more than one defensible way to write each, and the choice is the product.
# Keep them conservative (see the module docstring).
# --------------------------------------------------------------------------- #

def multiple_candidate_answers(item: BenchmarkItem) -> Optional[RuleResult]:
    """ILL_POSED when the stem admits more than one valid answer.

    Why it matters: an item with two correct answers silently penalizes any
    model that picks the "wrong" right answer — the benchmark is measuring luck,
    not capability, and no exact checker can fix that.

    Approaches to weigh (pick and defend one):
      * Surface heuristics on the QUESTION: disjunctive targets ("how many cats
        or dogs"), ranges asked for as a point value, "at least/at most" framings.
      * Heuristics on the ANSWER key that already leaked ambiguity ("12 or 15"),
        though answer_not_clean_number may already catch the leaked ones.
    Trade-off: aggressive surface matching raises recall but risks false flags
    on perfectly well-posed items that merely *mention* "or". Bias toward None.

    TODO(you): implement. Return a RuleResult(Verdict.ILL_POSED, reason, rule)
    or None.
    """
    return None


def underspecified_non_derivable(item: BenchmarkItem) -> Optional[RuleResult]:
    """RETRACTED 2026-06-28 — disabled after failing on real data.

    The first cut flagged "<subject> has/have/had some <noun>" as an indefinite,
    non-derivable starting quantity. On the synthetic fixture it looked perfect
    (precision 1.0). On the real GSM8K test split it fired on 3 items and ALL 3
    were FALSE POSITIVES:
      * 837 "She already has some savings ... how much money does she have?"
        -- the "some" IS the unknown you solve for (well-posed; answer 120).
      * 856 "expects to have some extra glue sticks left over" -- flavor text.
      * 863 "Gretchen has some coins ... how many in total?" -- solved from the
        stated constraints (answer 110).
    "has some X" is the *normal* shape of a solve-for-the-unknown GSM8K problem,
    not a defect, so the cue carries no sound signal. Shipping it would mean 0%
    real precision; precision-first says disable, not relax.

    A sound version must verify the queried quantity is genuinely unconstrained
    -- which is most of the work of solving the problem. Left as an honest open
    problem; the dead heuristic is kept here as a documented warning.
    """
    return None


def internal_contradiction(item: BenchmarkItem) -> Optional[RuleResult]:
    """ILL_POSED when the same subject is assigned two different ages with no
    temporal qualifier — a direct contradiction.

    Narrow by design: only the "<subject> is <n> years old" attribute, and it
    abstains the instant any temporal cue (ago / was / later / before ...)
    appears, since "Ben is 10; two years ago Ben was 8" is consistent, not
    contradictory. Extend to other attributes the same way: detect conflicting
    assignments, abstain on anything that could be a different time or entity.
    """
    if _TEMPORAL.search(item.question):
        return None
    by_subject: dict[str, set[int]] = {}
    for subject, num in _AGE.findall(item.question):
        by_subject.setdefault(subject.lower(), set()).add(int(num))
    for subject, ages in by_subject.items():
        if len(ages) > 1:
            return RuleResult(
                verdict=Verdict.ILL_POSED,
                reason=f"'{subject}' is assigned conflicting ages {sorted(ages)} with no temporal qualifier",
                rule="internal_contradiction",
            )
    return None


def unit_or_rounding_ambiguity(item: BenchmarkItem) -> Optional[RuleResult]:
    """JUDGE_DEPENDENT (not ill-posed) when the correct answer depends on an
    unspecified unit or rounding convention — gradeable, but only once a human
    fixes the convention, so it does not count as soundly exact-checkable.

    TODO(you): implement, or delete if you decide GSM8K does not need it.
    """
    return None


# Order matters only for which reason is reported first; the verdict is the
# strongest (most restrictive) one that fires. Register every rule here.
REGISTRY: list[Rule] = [
    answer_not_clean_number,
    multiple_candidate_answers,
    underspecified_non_derivable,
    internal_contradiction,
    unit_or_rounding_ambiguity,
]
