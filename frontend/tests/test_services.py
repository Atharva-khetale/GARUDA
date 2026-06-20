from app.services import sequence_service, mutation_service, codon_service, expression_service, restriction_service, protein_service, readiness_service

DNA = "ATGGCCATTGTAATGGGCCGCTGAAA"  # ATG GCC ATT GTA ATG GGC CGC TGA AA


def test_sequence_analysis():
    result = sequence_service.analyze_sequence(DNA, "DNA")
    assert result["seq_type"] == "DNA"
    assert result["length"] == len(DNA)
    assert 0 <= result["gc_content"] <= 100
    assert result["protein_sequence"] == "MAIVMGR"


def test_reverse_complement_and_transcribe():
    rc = sequence_service.reverse_complement("ATGC")
    assert rc == "GCAT"
    assert sequence_service.transcribe("ATGC") == "AUGC"


def test_mutation_silent_and_missense():
    original = "ATGGCCATT"  # M A I
    mutated_silent = "ATGGCGATT"  # GCC -> GCG, still A
    mutated_missense = "ATGACCATT"  # GCC -> ACC, A -> T

    silent = mutation_service.detect_mutations(original, mutated_silent)
    assert silent["summary"]["overall_severity"] == "Low"

    missense = mutation_service.detect_mutations(original, mutated_missense)
    assert any("Missense" in m["mutation_type"] for m in missense["mutations"])


def test_mutation_nonsense():
    original = "ATGGAAATT"  # M E I
    mutated = "ATGTAAATT"   # GAA -> TAA = stop
    report = mutation_service.detect_mutations(original, mutated)
    assert report["summary"]["overall_severity"] == "High"
    assert any("Nonsense" in m["mutation_type"] for m in report["mutations"])


def test_codon_optimization_preserves_protein():
    seq = "ATGGCCATTGTAATGGGCCGCTGA"
    result = codon_service.optimize_sequence(seq, "ecoli")
    orig_protein = sequence_service.translate(seq, to_stop=True)
    opt_protein = sequence_service.translate(result["optimized_sequence"], to_stop=True)
    assert orig_protein == opt_protein
    assert result["after"]["cai"] >= result["before"]["cai"] - 1e-6


def test_expression_feasibility_range():
    seq = "ATGGCCATTGTAATGGGCCGCTGA"
    result = expression_service.assess_expression_feasibility(seq, "human")
    assert 0 <= result["expression_score"] <= 100
    assert result["category"] in ["Very Low", "Low", "Moderate", "High", "Very High"]


def test_restriction_analysis_runs():
    seq = "GAATTCGGATCCAAGCTT" * 3  # contains EcoRI, BamHI, HindIII sites
    result = restriction_service.analyze_restriction_sites(seq)
    assert result["total_cut_sites"] > 0
    assert "EcoRI" in result["enzymes"]


def test_protein_impact():
    original = "ATGGCCATTGTAATGGGCCGCTGA"
    mutated = "ATGTAAATTGTAATGGGCCGCTGA"  # premature stop near start
    impact = protein_service.analyze_protein_impact(original, mutated)
    assert impact["truncated"] is True
    assert impact["functional_impact_score"] < 100


def test_readiness_score():
    seq = "ATGGCCATTGTAATGGGCCGCTGA"
    expr = expression_service.assess_expression_feasibility(seq, "human")
    score = readiness_service.compute_readiness_score(expression_result=expr)
    assert 0 <= score["construct_score"] <= 100
    assert score["recommendation"]
