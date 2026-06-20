from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user
from app.schemas.schemas import SequenceAnalysisRequest
from app.services.parsing import strip_fasta
from app.services.sequence_service import analyze_sequence, SequenceValidationError

router = APIRouter(prefix="/sequence", tags=["Module 1 - Sequence Analysis"])


@router.post("/analyze")
def analyze(payload: SequenceAnalysisRequest, user=Depends(get_current_user)):
    seq = strip_fasta(payload.sequence)
    try:
        return analyze_sequence(seq, payload.seq_type)
    except SequenceValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
