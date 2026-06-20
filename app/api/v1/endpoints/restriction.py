from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user
from app.schemas.schemas import RestrictionAnalysisRequest
from app.services.parsing import strip_fasta
from app.services import restriction_service

router = APIRouter(prefix="/restriction", tags=["Module 4 - Restriction Enzyme Analysis"])


@router.post("/analyze")
def analyze(payload: RestrictionAnalysisRequest, user=Depends(get_current_user)):
    seq = strip_fasta(payload.sequence)
    return restriction_service.analyze_restriction_sites(seq, payload.enzymes)


@router.get("/{enzyme}/remove-suggestions")
def remove_suggestions(enzyme: str, sequence: str, user=Depends(get_current_user)):
    try:
        return restriction_service.suggest_site_removal(strip_fasta(sequence), enzyme)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{enzyme}/add-suggestions")
def add_suggestions(enzyme: str, sequence: str, near_position: int = 0, user=Depends(get_current_user)):
    try:
        return restriction_service.suggest_site_addition(strip_fasta(sequence), enzyme, near_position)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
