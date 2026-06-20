"""
MODULE 6: EXPRESSION FEASIBILITY ENGINE

Combines GC content, CAI, rare codon density, mRNA secondary-structure
proxy (5' UTR/start-codon folding via GC of first 30 nt), and sequence
complexity into a single 0-100 expression score with category and
detailed reasoning.
"""
from __future__ import annotations

from app.services.sequence_service import gc_content, codon_frequency_table
from app.services.codon_service import calculate_cai, find_rare_codons

IDEAL_GC_RANGE = (40.0, 60.0)


def _gc_score(gc: float) -> float:
    lo, hi = IDEAL_GC_RANGE
    if lo <= gc <= hi:
        return 100.0
    distance = min(abs(gc - lo), abs(gc - hi))
    return max(0.0, 100.0 - distance * 4)


def _cai_score(cai: float) -> float:
    return max(0.0, min(100.0, cai * 100))


def _rare_codon_score(rare_count: int, total_codons: int) -> float:
    if total_codons == 0:
        return 0.0
    density = rare_count / total_codons
    return max(0.0, 100.0 - density * 200)


def _five_prime_structure_score(dna: str) -> float:
    """Proxy for mRNA secondary structure near the start codon: very high
    GC content in the first 30 nt suggests strong secondary structure
    that can impede ribosome binding/scanning."""
    window = dna[:30]
    if not window:
        return 100.0
    gc = gc_content(window)
    if gc <= 60:
        return 100.0
    return max(0.0, 100.0 - (gc - 60) * 2.5)


def _complexity_score(dna: str) -> float:
    """Penalize long homopolymer runs and low sequence diversity."""
    if not dna:
        return 0.0
    max_run = 1
    current_run = 1
    for i in range(1, len(dna)):
        if dna[i] == dna[i - 1]:
            current_run += 1
            max_run = max(max_run, current_run)
        else:
            current_run = 1
    penalty = max(0, max_run - 4) * 8
    return max(0.0, 100.0 - penalty)


def _categorize(score: float) -> str:
    if score >= 85:
        return "Very High"
    if score >= 70:
        return "High"
    if score >= 50:
        return "Moderate"
    if score >= 30:
        return "Low"
    return "Very Low"


def assess_expression_feasibility(dna: str, organism: str) -> dict:
    dna = dna.upper()
    gc = gc_content(dna)
    cai = calculate_cai(dna, organism)
    codon_table = codon_frequency_table(dna)
    rare = find_rare_codons(dna, organism)

    gc_s = _gc_score(gc)
    cai_s = _cai_score(cai)
    rare_s = _rare_codon_score(len(rare), codon_table["total_codons"])
    structure_s = _five_prime_structure_score(dna)
    complexity_s = _complexity_score(dna)

    weights = {
        "gc_content": 0.20,
        "cai": 0.30,
        "rare_codon_density": 0.20,
        "mrna_structure": 0.15,
        "sequence_complexity": 0.15,
    }
    component_scores = {
        "gc_content": gc_s,
        "cai": cai_s,
        "rare_codon_density": rare_s,
        "mrna_structure": structure_s,
        "sequence_complexity": complexity_s,
    }
    overall = sum(component_scores[k] * w for k, w in weights.items())

    reasoning = []
    reasoning.append(
        f"GC content is {gc:.1f}% (ideal range {IDEAL_GC_RANGE[0]}-{IDEAL_GC_RANGE[1]}%), "
        f"contributing a sub-score of {gc_s:.1f}/100."
    )
    reasoning.append(
        f"Codon Adaptation Index for {organism} is {cai:.3f}, "
        f"contributing a sub-score of {cai_s:.1f}/100."
    )
    reasoning.append(
        f"{len(rare)} of {codon_table['total_codons']} codons are rare for {organism} "
        f"(usage < 10/1000), contributing a sub-score of {rare_s:.1f}/100."
    )
    reasoning.append(
        f"5' region GC composition gives an mRNA structure sub-score of {structure_s:.1f}/100 "
        f"(high GC near the start codon can impede ribosome scanning)."
    )
    reasoning.append(
        f"Sequence complexity (homopolymer run analysis) sub-score: {complexity_s:.1f}/100."
    )

    return {
        "expression_score": round(overall, 1),
        "category": _categorize(overall),
        "component_scores": {k: round(v, 1) for k, v in component_scores.items()},
        "weights": weights,
        "metrics": {
            "gc_content": gc,
            "cai": cai,
            "rare_codon_count": len(rare),
            "total_codons": codon_table["total_codons"],
        },
        "reasoning": reasoning,
    }
