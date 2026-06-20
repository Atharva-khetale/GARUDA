"""
Codon usage frequency tables (per 1000 codons), simplified reference values
for supported target organisms. Used for CAI calculation and codon
optimization. Values are representative averages compiled from public
codon usage databases (Kazusa-style tables).
"""

# Standard genetic code: codon -> amino acid (single letter)
CODON_TABLE = {
    "TTT": "F", "TTC": "F", "TTA": "L", "TTG": "L",
    "CTT": "L", "CTC": "L", "CTA": "L", "CTG": "L",
    "ATT": "I", "ATC": "I", "ATA": "I", "ATG": "M",
    "GTT": "V", "GTC": "V", "GTA": "V", "GTG": "V",
    "TCT": "S", "TCC": "S", "TCA": "S", "TCG": "S",
    "CCT": "P", "CCC": "P", "CCA": "P", "CCG": "P",
    "ACT": "T", "ACC": "T", "ACA": "T", "ACG": "T",
    "GCT": "A", "GCC": "A", "GCA": "A", "GCG": "A",
    "TAT": "Y", "TAC": "Y", "TAA": "*", "TAG": "*",
    "CAT": "H", "CAC": "H", "CAA": "Q", "CAG": "Q",
    "AAT": "N", "AAC": "N", "AAA": "K", "AAG": "K",
    "GAT": "D", "GAC": "D", "GAA": "E", "GAG": "E",
    "TGT": "C", "TGC": "C", "TGA": "*", "TGG": "W",
    "CGT": "R", "CGC": "R", "CGA": "R", "CGG": "R",
    "AGT": "S", "AGC": "S", "AGA": "R", "AGG": "R",
    "GGT": "G", "GGC": "G", "GGA": "G", "GGG": "G",
}

STOP_CODONS = {"TAA", "TAG", "TGA"}

# Relative synonymous codon usage frequencies per organism
# (codon -> usage frequency per 1000, approximate)
ORGANISM_CODON_USAGE = {
    "human": {
        "TTT": 17.6, "TTC": 20.3, "TTA": 7.7, "TTG": 12.9, "CTT": 13.2, "CTC": 19.6,
        "CTA": 7.2, "CTG": 39.6, "ATT": 16.0, "ATC": 20.8, "ATA": 7.5, "ATG": 22.0,
        "GTT": 11.0, "GTC": 14.5, "GTA": 7.1, "GTG": 28.1, "TCT": 15.2, "TCC": 17.7,
        "TCA": 12.2, "TCG": 4.4, "CCT": 17.5, "CCC": 19.8, "CCA": 16.9, "CCG": 6.9,
        "ACT": 13.1, "ACC": 18.9, "ACA": 15.1, "ACG": 6.1, "GCT": 18.4, "GCC": 27.7,
        "GCA": 15.8, "GCG": 7.4, "TAT": 12.2, "TAC": 15.3, "TAA": 1.0, "TAG": 0.8,
        "CAT": 10.9, "CAC": 15.1, "CAA": 12.3, "CAG": 34.2, "AAT": 17.0, "AAC": 19.1,
        "AAA": 24.4, "AAG": 31.9, "GAT": 21.8, "GAC": 25.1, "GAA": 29.0, "GAG": 39.6,
        "TGT": 10.6, "TGC": 12.6, "TGA": 1.6, "TGG": 13.2, "CGT": 4.5, "CGC": 10.4,
        "CGA": 6.2, "CGG": 11.4, "AGT": 12.1, "AGC": 19.5, "AGA": 12.2, "AGG": 12.0,
        "GGT": 10.8, "GGC": 22.2, "GGA": 16.5, "GGG": 16.5,
    },
    "mouse": {
        "TTT": 17.2, "TTC": 21.0, "TTA": 6.5, "TTG": 12.6, "CTT": 12.5, "CTC": 19.4,
        "CTA": 6.7, "CTG": 39.5, "ATT": 15.4, "ATC": 21.0, "ATA": 6.8, "ATG": 22.6,
        "GTT": 10.5, "GTC": 14.7, "GTA": 6.6, "GTG": 26.8, "TCT": 14.8, "TCC": 18.0,
        "TCA": 11.7, "TCG": 4.5, "CCT": 18.0, "CCC": 18.6, "CCA": 17.1, "CCG": 6.5,
        "ACT": 12.5, "ACC": 19.3, "ACA": 14.6, "ACG": 5.9, "GCT": 18.7, "GCC": 26.3,
        "GCA": 15.4, "GCG": 6.5, "TAT": 11.6, "TAC": 15.7, "TAA": 0.9, "TAG": 0.7,
        "CAT": 10.2, "CAC": 15.4, "CAA": 11.6, "CAG": 34.6, "AAT": 16.4, "AAC": 19.8,
        "AAA": 22.8, "AAG": 33.9, "GAT": 21.1, "GAC": 25.7, "GAA": 28.4, "GAG": 41.0,
        "TGT": 9.8, "TGC": 12.4, "TGA": 1.5, "TGG": 12.4, "CGT": 4.7, "CGC": 9.6,
        "CGA": 6.3, "CGG": 10.2, "AGT": 11.6, "AGC": 19.4, "AGA": 13.0, "AGG": 11.4,
        "GGT": 10.6, "GGC": 23.2, "GGA": 14.6, "GGG": 14.9,
    },
    "ecoli": {
        "TTT": 22.1, "TTC": 16.6, "TTA": 13.9, "TTG": 13.7, "CTT": 11.9, "CTC": 11.0,
        "CTA": 4.2, "CTG": 52.6, "ATT": 30.3, "ATC": 25.1, "ATA": 4.4, "ATG": 27.9,
        "GTT": 18.3, "GTC": 15.3, "GTA": 10.9, "GTG": 26.4, "TCT": 8.5, "TCC": 8.6,
        "TCA": 7.2, "TCG": 8.9, "CCT": 7.0, "CCC": 5.5, "CCA": 8.6, "CCG": 23.2,
        "ACT": 9.0, "ACC": 23.4, "ACA": 7.1, "ACG": 14.4, "GCT": 15.3, "GCC": 25.5,
        "GCA": 20.5, "GCG": 33.6, "TAT": 16.8, "TAC": 12.2, "TAA": 2.0, "TAG": 0.2,
        "CAT": 12.9, "CAC": 9.7, "CAA": 15.3, "CAG": 28.8, "AAT": 17.6, "AAC": 21.6,
        "AAA": 33.6, "AAG": 10.3, "GAT": 32.1, "GAC": 19.1, "GAA": 39.0, "GAG": 18.4,
        "TGT": 5.2, "TGC": 6.4, "TGA": 0.9, "TGG": 15.2, "CGT": 20.9, "CGC": 21.4,
        "CGA": 3.6, "CGG": 5.4, "AGT": 8.8, "AGC": 15.9, "AGA": 2.1, "AGG": 1.2,
        "GGT": 24.7, "GGC": 29.6, "GGA": 8.0, "GGG": 11.1,
    },
    "yeast": {
        "TTT": 26.1, "TTC": 18.4, "TTA": 26.2, "TTG": 27.2, "CTT": 12.3, "CTC": 5.4,
        "CTA": 13.4, "CTG": 10.5, "ATT": 30.1, "ATC": 17.2, "ATA": 17.8, "ATG": 20.9,
        "GTT": 22.1, "GTC": 11.8, "GTA": 11.8, "GTG": 10.8, "TCT": 23.5, "TCC": 14.2,
        "TCA": 18.7, "TCG": 8.6, "CCT": 13.5, "CCC": 6.8, "CCA": 18.3, "CCG": 5.3,
        "ACT": 20.3, "ACC": 12.7, "ACA": 17.8, "ACG": 7.2, "GCT": 21.2, "GCC": 12.6,
        "GCA": 16.2, "GCG": 6.2, "TAT": 18.8, "TAC": 14.8, "TAA": 1.1, "TAG": 0.5,
        "CAT": 13.6, "CAC": 7.5, "CAA": 27.3, "CAG": 12.1, "AAT": 35.7, "AAC": 24.8,
        "AAA": 41.9, "AAG": 30.8, "GAT": 37.6, "GAC": 20.2, "GAA": 45.6, "GAG": 19.2,
        "TGT": 8.1, "TGC": 4.8, "TGA": 0.7, "TGG": 10.4, "CGT": 6.4, "CGC": 2.6,
        "CGA": 3.0, "CGG": 1.7, "AGT": 14.2, "AGC": 9.8, "AGA": 21.3, "AGG": 9.3,
        "GGT": 23.9, "GGC": 9.8, "GGA": 10.9, "GGG": 6.0,
    },
    "cho": {
        "TTT": 16.9, "TTC": 21.4, "TTA": 6.6, "TTG": 12.1, "CTT": 12.5, "CTC": 19.0,
        "CTA": 6.6, "CTG": 40.3, "ATT": 15.5, "ATC": 21.5, "ATA": 6.5, "ATG": 22.7,
        "GTT": 10.4, "GTC": 14.9, "GTA": 6.4, "GTG": 27.5, "TCT": 14.6, "TCC": 17.9,
        "TCA": 11.4, "TCG": 4.3, "CCT": 17.4, "CCC": 18.9, "CCA": 17.0, "CCG": 6.4,
        "ACT": 12.6, "ACC": 19.6, "ACA": 14.5, "ACG": 5.9, "GCT": 18.6, "GCC": 27.6,
        "GCA": 15.3, "GCG": 7.1, "TAT": 11.8, "TAC": 15.8, "TAA": 0.9, "TAG": 0.7,
        "CAT": 10.4, "CAC": 15.3, "CAA": 11.7, "CAG": 35.0, "AAT": 16.2, "AAC": 19.9,
        "AAA": 23.4, "AAG": 33.0, "GAT": 21.4, "GAC": 26.0, "GAA": 28.6, "GAG": 40.5,
        "TGT": 9.8, "TGC": 12.6, "TGA": 1.4, "TGG": 13.0, "CGT": 4.6, "CGC": 10.0,
        "CGA": 6.1, "CGG": 10.6, "AGT": 11.8, "AGC": 19.5, "AGA": 12.5, "AGG": 11.7,
        "GGT": 10.7, "GGC": 22.8, "GGA": 15.2, "GGG": 15.4,
    },
}

SUPPORTED_ORGANISMS = list(ORGANISM_CODON_USAGE.keys())


def get_synonymous_groups():
    """Return mapping amino_acid -> list of codons coding for it."""
    groups: dict[str, list[str]] = {}
    for codon, aa in CODON_TABLE.items():
        groups.setdefault(aa, []).append(codon)
    return groups


SYNONYMOUS_CODONS = get_synonymous_groups()
