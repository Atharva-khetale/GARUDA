from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.schemas.schemas import MutationAnalysisRequest
from app.services.parsing import strip_fasta
from app.services.mutation_service import detect_mutations
from app.services.protein_service import analyze_protein_impact

router = APIRouter(prefix="/mutation", tags=["Module 2/3 - Mutation & Protein Impact"])


@router.post("/analyze")
def analyze(payload: MutationAnalysisRequest, user=Depends(get_current_user)):
    original = strip_fasta(payload.original_sequence)
    mutated = strip_fasta(payload.mutated_sequence)

    mutation_report = detect_mutations(original, mutated)
    protein_impact = analyze_protein_impact(original, mutated)

    return {
        "mutation_report": mutation_report,
        "protein_impact": protein_impact,
    }
