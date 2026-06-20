"""
MODULE 5: CODON OPTIMIZATION ENGINE

Computes Codon Adaptation Index (CAI), identifies rare codons, and
generates an optimized DNA sequence for a target organism by replacing
codons with the most frequently used synonymous codon for that organism,
while preserving the encoded protein.
"""
from __future__ import annotations

import math

from app.services.codon_tables import (
    CODON_TABLE, ORGANISM_CODON_USAGE, SYNONYMOUS_CODONS, SUPPORTED_ORGANISMS,
)
from app.services.sequence_service import gc_content, codon_frequency_table

RARE_CODON_THRESHOLD = 10.0  # usage per 1000 below this is considered "rare"


def _relative_adaptiveness(organism: str) -> dict[str, float]:
    """w_ij = usage(codon) / max(usage(synonyms of same aa))"""
    usage = ORGANISM_CODON_USAGE[organism]
    weights = {}
    for aa, codons in SYNONYMOUS_CODONS.items():
        if aa == "*":
            continue
        max_usage = max(usage.get(c, 0.0) for c in codons) or 1e-9
        for c in codons:
            weights[c] = usage.get(c, 0.0) / max_usage
    return weights


def calculate_cai(dna: str, organism: str) -> float:
    """Codon Adaptation Index: geometric mean of relative adaptiveness
    values (w) for each codon in the sequence."""
    if organism not in ORGANISM_CODON_USAGE:
        raise ValueError(f"Unsupported organism '{organism}'. Supported: {SUPPORTED_ORGANISMS}")

    weights = _relative_adaptiveness(organism)
    codons = [dna[i:i + 3] for i in range(0, len(dna) - len(dna) % 3, 3)]
    log_sum, n = 0.0, 0
    for codon in codons:
        aa = CODON_TABLE.get(codon)
        if not aa or aa == "*" or len(SYNONYMOUS_CODONS.get(aa, [])) <= 1:
            continue  # skip Met/Trp (no synonyms) and stops
        w = weights.get(codon, 1e-9)
        log_sum += math.log(max(w, 1e-9))
        n += 1
    if n == 0:
        return 1.0
    return round(math.exp(log_sum / n), 4)


def find_rare_codons(dna: str, organism: str) -> list[dict]:
    usage = ORGANISM_CODON_USAGE[organism]
    codons = [dna[i:i + 3] for i in range(0, len(dna) - len(dna) % 3, 3)]
    rare = []
    for i, codon in enumerate(codons):
        freq = usage.get(codon, 0.0)
        if freq < RARE_CODON_THRESHOLD:
            rare.append({
                "position_nt": i * 3,
                "codon": codon,
                "amino_acid": CODON_TABLE.get(codon, "?"),
                "usage_per_1000": freq,
            })
    return rare


def optimize_sequence(dna: str, organism: str) -> dict:
    """
    Replace every codon with the most-used synonymous codon for the
    target organism (one-best codon optimization). Preserves the
    protein sequence exactly (stop codon kept as-is).
    """
    if organism not in ORGANISM_CODON_USAGE:
        raise ValueError(f"Unsupported organism '{organism}'. Supported: {SUPPORTED_ORGANISMS}")

    usage = ORGANISM_CODON_USAGE[organism]
    best_codon_for_aa = {}
    for aa, codons in SYNONYMOUS_CODONS.items():
        best_codon_for_aa[aa] = max(codons, key=lambda c: usage.get(c, 0.0))

    dna = dna.upper()
    codons = [dna[i:i + 3] for i in range(0, len(dna) - len(dna) % 3, 3)]
    remainder = dna[len(codons) * 3:]

    optimized_codons = []
    changed = 0
    for codon in codons:
        aa = CODON_TABLE.get(codon)
        if not aa:
            optimized_codons.append(codon)
            continue
        if aa == "*":
            # keep original stop codon choice
            optimized_codons.append(codon)
            continue
        new_codon = best_codon_for_aa[aa]
        if new_codon != codon:
            changed += 1
        optimized_codons.append(new_codon)

    optimized_dna = "".join(optimized_codons) + remainder

    before_cai = calculate_cai(dna, organism)
    after_cai = calculate_cai(optimized_dna, organism)
    before_rare = find_rare_codons(dna, organism)
    after_rare = find_rare_codons(optimized_dna, organism)

    return {
        "organism": organism,
        "original_sequence": dna,
        "optimized_sequence": optimized_dna,
        "codons_changed": changed,
        "total_codons": len(codons),
        "before": {
            "cai": before_cai,
            "gc_content": gc_content(dna),
            "rare_codon_count": len(before_rare),
        },
        "after": {
            "cai": after_cai,
            "gc_content": gc_content(optimized_dna),
            "rare_codon_count": len(after_rare),
        },
        "expected_improvement": {
            "cai_delta": round(after_cai - before_cai, 4),
            "rare_codon_reduction": len(before_rare) - len(after_rare),
        },
        "rare_codons_before": before_rare,
        "rare_codons_after": after_rare,
    }


def codon_usage_comparison(dna: str, organism: str) -> dict:
    seq_usage = codon_frequency_table(dna)
    organism_usage = ORGANISM_CODON_USAGE[organism]
    return {
        "sequence_codon_frequencies": seq_usage["frequencies"],
        "organism_reference_usage_per_1000": organism_usage,
        "cai": calculate_cai(dna, organism),
        "gc_content": gc_content(dna),
    }
