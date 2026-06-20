from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user
from app.schemas.schemas import ExpressionAnalysisRequest, FullAnalysisRequest
from app.services.parsing import strip_fasta
from app.services import (
    sequence_service, mutation_service, protein_service,
    restriction_service, codon_service, expression_service, readiness_service,
)
from app.ml import predict as ml_predict

router = APIRouter(tags=["Module 6/9 - Expression & Readiness"])


@router.post("/pipeline/full-analysis-async")
def full_analysis_async(payload: FullAnalysisRequest, user=Depends(get_current_user)):
    """
    Submits the full pipeline as a background Celery task and returns a
    task_id. Connect to /api/v1/ws/jobs/{task_id} for live status/result.
    """
    from app.worker import run_full_analysis_task
    try:
        task = run_full_analysis_task.delay(
            strip_fasta(payload.original_sequence),
            strip_fasta(payload.mutated_sequence) if payload.mutated_sequence else None,
            payload.organism,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    return {"task_id": task.id, "status": "submitted"}


@router.post("/ml/predict-viability")
def predict_viability(payload: ExpressionAnalysisRequest, user=Depends(get_current_user)):
    seq = strip_fasta(payload.sequence)
    return ml_predict.predict_construct_viability(seq, payload.organism)


@router.post("/expression/analyze")
def expression_analyze(payload: ExpressionAnalysisRequest, user=Depends(get_current_user)):
    seq = strip_fasta(payload.sequence)
    try:
        return expression_service.assess_expression_feasibility(seq, payload.organism)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/pipeline/full-analysis")
def full_analysis(payload: FullAnalysisRequest, user=Depends(get_current_user)):
    """
    Runs the complete GARUDA analysis pipeline (Modules 1, 2, 3, 4, 5, 6, 9)
    on a single construct in one call.
    """
    original = strip_fasta(payload.original_sequence)

    try:
        seq_analysis = sequence_service.analyze_sequence(original, "DNA")
    except sequence_service.SequenceValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))

    restriction = restriction_service.analyze_restriction_sites(original, payload.enzymes)
    optimization = codon_service.optimize_sequence(original, payload.organism)
    expression = expression_service.assess_expression_feasibility(original, payload.organism)

    mutation_report = None
    protein_impact = None
    if payload.mutated_sequence:
        mutated = strip_fasta(payload.mutated_sequence)
        mutation_report = mutation_service.detect_mutations(original, mutated)
        protein_impact = protein_service.analyze_protein_impact(original, mutated)

    readiness = readiness_service.compute_readiness_score(
        expression_result=expression,
        mutation_summary=mutation_report["summary"] if mutation_report else None,
        protein_impact=protein_impact,
        restriction_result=restriction,
        codon_optimization=optimization,
    )

    ml_prediction = ml_predict.predict_construct_viability(original, payload.organism)

    return {
        "sequence_analysis": seq_analysis,
        "restriction_analysis": restriction,
        "codon_optimization": optimization,
        "expression_feasibility": expression,
        "mutation_report": mutation_report,
        "protein_impact": protein_impact,
        "ml_prediction": ml_prediction,
        "readiness_score": readiness,
    }
