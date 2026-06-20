"""
MODULE 9: EXPERIMENT READINESS SCORE

Aggregates outputs from mutation analysis, expression feasibility,
protein impact, restriction analysis, and codon optimization into a
single 0-100 construct readiness score with a recommendation.
"""
from __future__ import annotations


SEVERITY_PENALTY = {"None": 0, "Low": 5, "Medium": 20, "High": 40}


def compute_readiness_score(
    expression_result: dict,
    mutation_summary: dict | None = None,
    protein_impact: dict | None = None,
    restriction_result: dict | None = None,
    codon_optimization: dict | None = None,
) -> dict:
    expression_score = expression_result["expression_score"]

    mutation_severity = (mutation_summary or {}).get("overall_severity", "None")
    mutation_penalty = SEVERITY_PENALTY.get(mutation_severity, 0)

    protein_score = (protein_impact or {}).get("functional_impact_score", 100.0)

    restriction_penalty = 0
    if restriction_result:
        # more than 4 total cut sites starts to be a cloning concern
        excess = max(0, restriction_result.get("total_cut_sites", 0) - 4)
        restriction_penalty = min(15, excess * 3)

    optimization_bonus = 0
    optimization_needed = "Minimal"
    if codon_optimization:
        cai_delta = codon_optimization["expected_improvement"]["cai_delta"]
        if cai_delta > 0.15:
            optimization_needed = "Significant"
            optimization_bonus = -10
        elif cai_delta > 0.05:
            optimization_needed = "Moderate"
            optimization_bonus = -5
        else:
            optimization_needed = "Minimal"

    construct_score = (
        0.45 * expression_score
        + 0.35 * protein_score
        + 0.20 * 100  # base codon/restriction baseline, adjusted below
    )
    construct_score -= mutation_penalty
    construct_score -= restriction_penalty
    construct_score += optimization_bonus
    construct_score = max(0.0, min(100.0, round(construct_score, 1)))

    if construct_score >= 80:
        recommendation = "Ready for Experimental Validation"
    elif construct_score >= 60:
        recommendation = "Minor optimization recommended before validation"
    elif construct_score >= 40:
        recommendation = "Significant revisions recommended before proceeding"
    else:
        recommendation = "Not recommended for wet-lab validation without redesign"

    return {
        "construct_score": construct_score,
        "expression_score": expression_score,
        "expression_category": expression_result["category"],
        "mutation_severity": mutation_severity,
        "protein_functional_score": protein_score,
        "restriction_penalty": restriction_penalty,
        "optimization_needed": optimization_needed,
        "recommendation": recommendation,
    }
