"""
MODULE 3: PROTEIN IMPACT ANALYSIS

Compares original vs mutated protein sequences (derived from translated
DNA) to assess amino acid changes, truncation, and length change, and
produces a 0-100 Functional Impact Score.
"""
from __future__ import annotations

from app.services.sequence_service import translate


def _count_aa_changes(orig_protein: str, mut_protein: str) -> int:
    n = min(len(orig_protein), len(mut_protein))
    return sum(1 for i in range(n) if orig_protein[i] != mut_protein[i])


def analyze_protein_impact(original_dna: str, mutated_dna: str) -> dict:
    orig_protein = translate(original_dna, to_stop=True)
    mut_protein = translate(mutated_dna, to_stop=True)

    aa_changes = _count_aa_changes(orig_protein, mut_protein)
    length_change = len(mut_protein) - len(orig_protein)
    truncated = length_change < 0
    extended = length_change > 0

    # Functional impact score: starts at 100, deducted for changes
    score = 100.0
    if orig_protein:
        change_ratio = aa_changes / len(orig_protein)
        score -= change_ratio * 40

    if truncated:
        truncation_ratio = abs(length_change) / max(len(orig_protein), 1)
        score -= min(50, truncation_ratio * 100)
    elif extended:
        score -= min(15, (length_change / max(len(orig_protein), 1)) * 50)

    score = max(0.0, min(100.0, round(score, 1)))

    if score >= 85:
        verdict = "Minimal functional disruption expected"
    elif score >= 60:
        verdict = "Moderate functional disruption possible"
    elif score >= 30:
        verdict = "Significant functional disruption likely"
    else:
        verdict = "Severe functional disruption / likely loss of function"

    return {
        "original_protein_length": len(orig_protein),
        "mutated_protein_length": len(mut_protein),
        "amino_acid_changes": aa_changes,
        "protein_length_change": length_change,
        "truncated": truncated,
        "extended": extended,
        "functional_impact_score": score,
        "verdict": verdict,
        "original_protein": orig_protein,
        "mutated_protein": mut_protein,
    }
