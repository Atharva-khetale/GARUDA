from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str

    class Config:
        from_attributes = True


class SequenceAnalysisRequest(BaseModel):
    sequence: str = Field(..., description="Raw DNA/RNA/Protein sequence (FASTA header lines ignored)")
    seq_type: Optional[Literal["DNA", "RNA", "PROTEIN"]] = Field(
        None, description="If omitted, type is auto-detected"
    )


class MutationAnalysisRequest(BaseModel):
    original_sequence: str
    mutated_sequence: str


class RestrictionAnalysisRequest(BaseModel):
    sequence: str
    enzymes: Optional[list[str]] = None


class CodonOptimizationRequest(BaseModel):
    sequence: str
    organism: Literal["human", "mouse", "ecoli", "yeast", "cho"]


class ExpressionAnalysisRequest(BaseModel):
    sequence: str
    organism: Literal["human", "mouse", "ecoli", "yeast", "cho"]


class FullAnalysisRequest(BaseModel):
    original_sequence: str
    mutated_sequence: Optional[str] = None
    organism: Literal["human", "mouse", "ecoli", "yeast", "cho"] = "human"
    enzymes: Optional[list[str]] = None
