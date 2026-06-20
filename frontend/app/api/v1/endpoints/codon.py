from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user
from app.schemas.schemas import CodonOptimizationRequest
from app.services.parsing import strip_fasta
from app.services import codon_service

router = APIRouter(prefix="/codon", tags=["Module 5 - Codon Optimization"])


@router.post("/optimize")
def optimize(payload: CodonOptimizationRequest, user=Depends(get_current_user)):
    seq = strip_fasta(payload.sequence)
    try:
        return codon_service.optimize_sequence(seq, payload.organism)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/usage")
def usage(payload: CodonOptimizationRequest, user=Depends(get_current_user)):
    seq = strip_fasta(payload.sequence)
    return codon_service.codon_usage_comparison(seq, payload.organism)
