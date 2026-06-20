"""
MODULE 1: SEQUENCE ANALYSIS ENGINE

Implements DNA/RNA/Protein validation, GC content, ORF detection,
codon statistics, transcription/translation, and length metrics
using Biopython.
"""
from __future__ import annotations

from collections import Counter
from typing import Literal

from Bio.Seq import Seq
from Bio.SeqUtils import gc_fraction

from app.services.codon_tables import CODON_TABLE, STOP_CODONS

VALID_DNA = set("ACGTN")
VALID_RNA = set("ACGUN")
VALID_PROTEIN = set("ACDEFGHIKLMNPQRSTVWYX*")

SeqType = Literal["DNA", "RNA", "PROTEIN"]


class SequenceValidationError(ValueError):
    pass


def detect_sequence_type(raw: str) -> SeqType:
    """Best-effort auto-detection of sequence type."""
    s = raw.upper().strip().replace("\n", "").replace(" ", "")
    chars = set(s)
    if chars <= VALID_DNA:
        return "DNA"
    if chars <= VALID_RNA and "U" in chars:
        return "RNA"
    if chars <= VALID_PROTEIN:
        return "PROTEIN"
    raise SequenceValidationError(f"Unrecognized characters in sequence: {chars - VALID_PROTEIN}")


def validate_sequence(raw: str, seq_type: SeqType) -> str:
    s = raw.upper().strip().replace("\n", "").replace(" ", "")
    if not s:
        raise SequenceValidationError("Empty sequence")

    valid_set = {"DNA": VALID_DNA, "RNA": VALID_RNA, "PROTEIN": VALID_PROTEIN}[seq_type]
    invalid = set(s) - valid_set
    if invalid:
        raise SequenceValidationError(
            f"Invalid characters for {seq_type} sequence: {sorted(invalid)}"
        )
    return s


def gc_content(dna: str) -> float:
    return round(gc_fraction(Seq(dna)) * 100, 2)


def reverse_complement(dna: str) -> str:
    return str(Seq(dna).reverse_complement())


def transcribe(dna: str) -> str:
    """Coding-strand DNA -> mRNA."""
    return str(Seq(dna).transcribe())


def translate(dna_or_rna: str, to_stop: bool = False) -> str:
    return str(Seq(dna_or_rna).translate(to_stop=to_stop))


def codon_frequency_table(dna: str) -> dict:
    """Return raw counts and relative frequencies of each codon found
    in-frame (frame 0) within the given DNA sequence."""
    codons = [dna[i:i + 3] for i in range(0, len(dna) - len(dna) % 3, 3)]
    codons = [c for c in codons if len(c) == 3]
    counts = Counter(codons)
    total = sum(counts.values()) or 1
    return {
        "counts": dict(counts),
        "frequencies": {c: round(n / total, 4) for c, n in counts.items()},
        "total_codons": total,
    }


def find_orfs(dna: str, min_protein_length: int = 30) -> list[dict]:
    """
    Find Open Reading Frames on both strands across all 3 reading frames.

    Returns list of dicts: {start, end, strand, frame, length_nt,
    protein_length, protein_sequence}
    Coordinates are 0-based, end-exclusive, relative to the input strand.
    """
    orfs = []
    seq_len = len(dna)
    seq_obj = Seq(dna)
    strands = [(+1, seq_obj), (-1, seq_obj.reverse_complement())]

    for strand, nuc in strands:
        for frame in range(3):
            trans = str(nuc[frame:].translate())
            trans_len = len(trans)
            aa_start = 0
            while aa_start < trans_len:
                aa_start_codon = trans.find("M", aa_start)
                if aa_start_codon == -1:
                    break
                aa_end = trans.find("*", aa_start_codon)
                if aa_end == -1:
                    # ORF runs to the end without a stop codon - skip
                    aa_start = aa_start_codon + 1
                    continue
                protein_len = aa_end - aa_start_codon
                if protein_len >= min_protein_length:
                    nt_start = frame + aa_start_codon * 3
                    nt_end = frame + (aa_end + 1) * 3  # include stop codon
                    if strand == 1:
                        start, end = nt_start, min(nt_end, seq_len)
                    else:
                        # convert reverse-strand coordinates back to original sequence
                        start = seq_len - min(nt_end, seq_len)
                        end = seq_len - nt_start
                    orfs.append({
                        "start": start,
                        "end": end,
                        "strand": strand,
                        "frame": frame,
                        "length_nt": (aa_end + 1 - aa_start_codon) * 3,
                        "protein_length": protein_len,
                        "protein_sequence": trans[aa_start_codon:aa_end],
                    })
                aa_start = aa_end + 1

    orfs.sort(key=lambda o: o["length_nt"], reverse=True)
    return orfs


def molecular_weight(protein: str) -> float:
    from Bio.SeqUtils.ProtParam import ProteinAnalysis
    clean = protein.replace("*", "").replace("X", "")
    if not clean:
        return 0.0
    return round(ProteinAnalysis(clean).molecular_weight(), 2)


def analyze_sequence(raw: str, seq_type: SeqType | None = None) -> dict:
    """
    Full Module 1 pipeline.

    If seq_type is None, it is auto-detected.
    """
    if seq_type is None:
        seq_type = detect_sequence_type(raw)

    seq = validate_sequence(raw, seq_type)
    result: dict = {
        "seq_type": seq_type,
        "length": len(seq),
        "sequence": seq,
    }

    if seq_type == "DNA":
        result["gc_content"] = gc_content(seq)
        result["reverse_complement"] = reverse_complement(seq)
        result["mrna_sequence"] = transcribe(seq)
        result["protein_sequence"] = translate(seq, to_stop=True)
        result["codon_usage"] = codon_frequency_table(seq)
        result["orfs"] = find_orfs(seq)
    elif seq_type == "RNA":
        dna_equiv = seq.replace("U", "T")
        result["gc_content"] = gc_content(dna_equiv)
        result["protein_sequence"] = translate(seq, to_stop=True)
        result["codon_usage"] = codon_frequency_table(dna_equiv)
        result["orfs"] = find_orfs(dna_equiv)
    else:  # PROTEIN
        result["molecular_weight"] = molecular_weight(seq)

    return result
