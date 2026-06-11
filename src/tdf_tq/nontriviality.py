"""Nontrivial vs trivial stability classification (Stage 4B)."""

from dataclasses import dataclass

from tdf_tq.candidates import CandidateEvaluation

CLASS_TRIVIAL_STABLE_CONTROL = "TRIVIAL_STABLE_CONTROL"
CLASS_NONTRIVIAL_STABLE_TOY_CANDIDATE = "NONTRIVIAL_STABLE_TOY_CANDIDATE"
CLASS_INCONCLUSIVE = "INCONCLUSIVE"
CLASS_FAIL = "FAIL"

_ALLOWED_CLASSIFICATIONS = frozenset(
    {
        CLASS_TRIVIAL_STABLE_CONTROL,
        CLASS_NONTRIVIAL_STABLE_TOY_CANDIDATE,
        CLASS_INCONCLUSIVE,
        CLASS_FAIL,
    }
)

_LIMITATION = "Toy stability label only; not a particle, not an electron, not validated physics."


@dataclass(frozen=True)
class NontrivialStabilityAssessment:
    """Toy nontrivial-stability classification for one evaluated history."""

    seed_label: str
    update_rule_label: str
    classification: str
    passed_nontrivial: bool
    metrics: dict[str, object]
    limitations: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.classification not in _ALLOWED_CLASSIFICATIONS:
            raise ValueError(f"invalid classification: {self.classification!r}")
        if not isinstance(self.passed_nontrivial, bool):
            raise TypeError("passed_nontrivial must be a bool")
        if not self.limitations:
            raise ValueError("limitations must be non-empty")
        if _LIMITATION not in self.limitations:
            raise ValueError("limitations must include the standard Stage 4B disclaimer")


def classify_nontrivial_stability(
    evaluation: CandidateEvaluation,
    update_rule_label: str,
    changed_across_history: bool,
    perturbation_robust: bool,
) -> NontrivialStabilityAssessment:
    """Classify toy stability as trivial control, nontrivial candidate, or other."""
    if update_rule_label == "identity" or not changed_across_history:
        classification = CLASS_TRIVIAL_STABLE_CONTROL
        passed_nontrivial = False
    elif evaluation.passed and perturbation_robust:
        classification = CLASS_NONTRIVIAL_STABLE_TOY_CANDIDATE
        passed_nontrivial = True
    elif evaluation.verdict == "INCONCLUSIVE":
        classification = CLASS_INCONCLUSIVE
        passed_nontrivial = False
    else:
        classification = CLASS_FAIL
        passed_nontrivial = False

    metrics = {
        "evaluation_passed": evaluation.passed,
        "evaluation_verdict": evaluation.verdict,
        "changed_across_history": changed_across_history,
        "perturbation_robust": perturbation_robust,
        **evaluation.metrics,
    }

    return NontrivialStabilityAssessment(
        seed_label=evaluation.seed_label,
        update_rule_label=update_rule_label,
        classification=classification,
        passed_nontrivial=passed_nontrivial,
        metrics=metrics,
        limitations=(_LIMITATION,),
    )
