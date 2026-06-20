"""
MODULE 2: MUTATION ANALYSIS ENGINE

Compares an original DNA sequence against a mutated DNA sequence and
classifies each difference as a SNP, insertion, deletion, frameshift,
silent, missense, or nonsense mutation.
"""
from __future__ import annotations

from app.services.codon_tables import CODON_TABLE


def _translate_codon(codon: str) -> str:
    codon = codon.upper()
    if len(codon) != 3 or any(b not in "ACGT" for b in codon):
        return "?"
    return CODON_TABLE.get(codon, "?")


def _classify_point_mutation(orig_codon: str, mut_codon: str) -> tuple[str, str, str, float]:
    """Returns (mutation_type, impact, severity, severity_score 0-1)."""
    orig_aa = _translate_codon(orig_codon)
    mut_aa = _translate_codon(mut_codon)

    if orig_aa == mut_aa:
        return "Silent (Synonymous)", "No amino acid change", "Low", 0.05

    if mut_aa == "*" and orig_aa != "*":
        return "Nonsense", "Premature Stop Codon", "High", 0.95

    if orig_aa == "*" and mut_aa != "*":
        return "Stop-Loss", "Loss of stop codon, read-through translation", "High", 0.85

    return "Missense", f"{orig_aa} -> {mut_aa} amino acid substitution", "Medium", 0.45


def detect_mutations(original: str, mutated: str) -> dict:
    """
    Full Module 2 pipeline. Returns a structured mutation report.

    Detects:
      - Length difference -> insertion/deletion/frameshift
      - Per-codon SNP/silent/missense/nonsense/stop-loss classification
    """
    original = original.upper().strip()
    mutated = mutated.upper().strip()

    report: dict = {"mutations": [], "summary": {}}

    len_diff = len(mutated) - len(original)

    if len_diff != 0:
        if len_diff % 3 != 0:
            indel_type = "Insertion" if len_diff > 0 else "Deletion"
            report["mutations"].append({
                "position": min(len(original), len(mutated)),
                "original_codon": None,
                "mutated_codon": None,
                "mutation_type": f"Frameshift ({indel_type})",
                "impact": f"Frameshift mutation: {abs(len_diff)} nt {'inserted' if len_diff > 0 else 'deleted'}, "
                          f"shifts downstream reading frame",
                "severity": "High",
                "severity_score": 0.98,
            })
        else:
            indel_type = "In-frame Insertion" if len_diff > 0 else "In-frame Deletion"
            report["mutations"].append({
                "position": min(len(original), len(mutated)),
                "original_codon": None,
                "mutated_codon": None,
                "mutation_type": indel_type,
                "impact": f"{abs(len_diff)} nt {'inserted' if len_diff > 0 else 'deleted'} "
                          f"({abs(len_diff) // 3} codon(s)), reading frame preserved",
                "severity": "Medium",
                "severity_score": 0.5,
            })

    # Codon-by-codon comparison over the overlapping region
    compare_len = min(len(original), len(mutated))
    compare_len -= compare_len % 3

    for i in range(0, compare_len, 3):
        orig_codon = original[i:i + 3]
        mut_codon = mutated[i:i + 3]
        if orig_codon == mut_codon:
            continue

        mutation_type, impact, severity, score = _classify_point_mutation(orig_codon, mut_codon)

        # If only one base differs, label as SNP explicitly
        diffs = sum(1 for a, b in zip(orig_codon, mut_codon) if a != b)
        prefix = "SNP - " if diffs == 1 else "Multi-base substitution - "

        report["mutations"].append({
            "position": i,
            "original_codon": orig_codon,
            "mutated_codon": mut_codon,
            "mutation_type": prefix + mutation_type,
            "impact": impact,
            "severity": severity,
            "severity_score": score,
        })

    severities = [m["severity"] for m in report["mutations"]]
    report["summary"] = {
        "total_mutations": len(report["mutations"]),
        "high_severity": severities.count("High"),
        "medium_severity": severities.count("Medium"),
        "low_severity": severities.count("Low"),
        "length_change": len_diff,
        "overall_severity": (
            "High" if "High" in severities else
            "Medium" if "Medium" in severities else
            "Low" if severities else "None"
        ),
    }
    return report
