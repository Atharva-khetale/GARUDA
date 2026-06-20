def strip_fasta(raw: str) -> str:
    """Remove FASTA header lines and whitespace, return concatenated sequence."""
    lines = [ln.strip() for ln in raw.strip().splitlines()]
    seq_lines = [ln for ln in lines if ln and not ln.startswith(">")]
    return "".join(seq_lines).upper()
