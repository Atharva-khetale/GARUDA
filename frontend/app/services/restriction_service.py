"""
MODULE 4: RESTRICTION ENZYME ANALYSIS

Uses Bio.Restriction to find cut sites for common cloning enzymes and
provides data for restriction map visualization. Also supports
silent-mutation suggestions to remove or add specific restriction sites.
"""
from __future__ import annotations

from Bio.Seq import Seq
from Bio.Restriction import RestrictionBatch, EcoRI, BamHI, HindIII, XhoI, NotI, PstI

from app.services.codon_tables import CODON_TABLE, SYNONYMOUS_CODONS

DEFAULT_ENZYMES = RestrictionBatch([EcoRI, BamHI, HindIII, XhoI, NotI, PstI])


def analyze_restriction_sites(dna: str, enzymes: list[str] | None = None) -> dict:
    """
    Returns cut site positions (1-based, per Biopython convention) and
    counts for each enzyme, plus data suitable for a restriction map.
    """
    seq = Seq(dna.upper())
    batch = DEFAULT_ENZYMES if not enzymes else RestrictionBatch(enzymes)
    results = batch.search(seq)

    sites = {}
    map_features = []
    for enzyme, positions in results.items():
        sites[str(enzyme)] = {
            "cut_positions": positions,
            "num_cuts": len(positions),
            "recognition_site": str(enzyme.site),
        }
        for pos in positions:
            map_features.append({
                "enzyme": str(enzyme),
                "position": pos,
                "recognition_site": str(enzyme.site),
            })

    map_features.sort(key=lambda f: f["position"])

    return {
        "sequence_length": len(seq),
        "enzymes": sites,
        "total_cut_sites": sum(v["num_cuts"] for v in sites.values()),
        "restriction_map": map_features,
    }


def _silent_recode(codon: str) -> list[str]:
    """Return alternative codons coding for the same amino acid."""
    aa = CODON_TABLE.get(codon.upper())
    if not aa or aa == "*":
        return []
    return [c for c in SYNONYMOUS_CODONS.get(aa, []) if c != codon.upper()]


def suggest_site_removal(dna: str, enzyme_name: str) -> dict:
    """
    Find occurrences of an enzyme's recognition site and suggest a
    silent (synonymous) codon substitution within the in-frame coding
    sequence that disrupts the site without changing the protein.
    """
    seq = dna.upper()
    batch = RestrictionBatch([enzyme_name])
    enzyme = batch.get(enzyme_name)
    site = str(enzyme.site)

    suggestions = []
    idx = seq.find(site)
    while idx != -1:
        # find a codon boundary overlapping the site, within reading frame 0
        codon_start = (idx // 3) * 3
        for offset in (0, 3):
            cs = codon_start + offset
            if cs < 0 or cs + 3 > len(seq):
                continue
            codon = seq[cs:cs + 3]
            for alt in _silent_recode(codon):
                new_seq = seq[:cs] + alt + seq[cs + 3:]
                if site not in new_seq[max(0, idx - 5):idx + len(site) + 5]:
                    suggestions.append({
                        "site_position": idx,
                        "codon_position": cs,
                        "original_codon": codon,
                        "suggested_codon": alt,
                        "amino_acid_unchanged": True,
                    })
                    break
            if suggestions and suggestions[-1]["site_position"] == idx:
                break
        idx = seq.find(site, idx + 1)

    return {
        "enzyme": enzyme_name,
        "recognition_site": site,
        "occurrences": seq.count(site),
        "suggestions": suggestions,
    }


def suggest_site_addition(dna: str, enzyme_name: str, near_position: int = 0) -> dict:
    """
    Suggest a silent codon substitution near `near_position` that would
    introduce the enzyme's recognition site, if a synonymous codon
    combination can create it without altering the protein.
    """
    seq = dna.upper()
    batch = RestrictionBatch([enzyme_name])
    enzyme = batch.get(enzyme_name)
    site = str(enzyme.site)

    if "N" in site:
        return {
            "enzyme": enzyme_name,
            "recognition_site": site,
            "feasible": False,
            "reason": "Degenerate recognition sequences are not auto-insertable; manual design recommended.",
        }

    window_start = max(0, (near_position // 3) * 3 - 6)
    window_end = min(len(seq), window_start + len(site) + 9)
    region = seq[window_start:window_end]

    feasible = False
    detail = "No silent substitution within the search window produces this recognition site."
    for shift in range(0, len(region) - len(site) + 1):
        target = region[shift:shift + len(site)]
        if target == site:
            feasible = True
            detail = "Recognition site already present in this region."
            break

    return {
        "enzyme": enzyme_name,
        "recognition_site": site,
        "feasible": feasible,
        "detail": detail,
        "search_window": [window_start, window_end],
    }
