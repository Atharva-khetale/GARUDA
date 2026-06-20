import uuid
import enum
from datetime import datetime

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON, Enum
)
from sqlalchemy import String as UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


def gen_uuid():
    return str(uuid.uuid4())


class RoleEnum(str, enum.Enum):
    admin = "admin"
    researcher = "researcher"
    viewer = "viewer"


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(36), primary_key=True, default=gen_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(Enum(RoleEnum), default=RoleEnum.researcher, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    projects = relationship("Project", back_populates="owner")


class Organism(Base):
    __tablename__ = "organisms"
    id = Column(UUID(36), primary_key=True, default=gen_uuid)
    name = Column(String, unique=True, nullable=False)
    taxonomy_id = Column(String, nullable=True)
    codon_usage_table = Column(JSON, nullable=True)


class Project(Base):
    __tablename__ = "projects"
    id = Column(UUID(36), primary_key=True, default=gen_uuid)
    owner_id = Column(UUID(36), ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="projects")
    sequences = relationship("Sequence", back_populates="project")


class Sequence(Base):
    __tablename__ = "sequences"
    id = Column(UUID(36), primary_key=True, default=gen_uuid)
    project_id = Column(UUID(36), ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=False)
    seq_type = Column(String, nullable=False)  # DNA / RNA / PROTEIN
    raw_sequence = Column(Text, nullable=False)
    organism_id = Column(UUID(36), ForeignKey("organisms.id"), nullable=True)
    gc_content = Column(Float, nullable=True)
    length = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="sequences")
    proteins = relationship("Protein", back_populates="sequence")
    mutations = relationship("Mutation", back_populates="sequence")


class Protein(Base):
    __tablename__ = "proteins"
    id = Column(UUID(36), primary_key=True, default=gen_uuid)
    sequence_id = Column(UUID(36), ForeignKey("sequences.id"), nullable=False)
    protein_sequence = Column(Text, nullable=False)
    length = Column(Integer, nullable=True)
    molecular_weight = Column(Float, nullable=True)
    uniprot_id = Column(String, nullable=True)

    sequence = relationship("Sequence", back_populates="proteins")


class Mutation(Base):
    __tablename__ = "mutations"
    id = Column(UUID(36), primary_key=True, default=gen_uuid)
    sequence_id = Column(UUID(36), ForeignKey("sequences.id"), nullable=False)
    position = Column(Integer, nullable=False)
    original_codon = Column(String, nullable=True)
    mutated_codon = Column(String, nullable=True)
    mutation_type = Column(String, nullable=False)  # SNP, insertion, deletion, frameshift...
    impact = Column(String, nullable=True)
    severity = Column(String, nullable=True)  # Low/Medium/High
    severity_score = Column(Float, nullable=True)

    sequence = relationship("Sequence", back_populates="mutations")


class Experiment(Base):
    __tablename__ = "experiments"
    id = Column(UUID(36), primary_key=True, default=gen_uuid)
    project_id = Column(UUID(36), ForeignKey("projects.id"), nullable=False)
    sequence_id = Column(UUID(36), ForeignKey("sequences.id"), nullable=False)
    experiment_type = Column(String, nullable=False)
    target_organism_id = Column(UUID(36), ForeignKey("organisms.id"), nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)


class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    id = Column(UUID(36), primary_key=True, default=gen_uuid)
    sequence_id = Column(UUID(36), ForeignKey("sequences.id"), nullable=False)
    module = Column(String, nullable=False)  # e.g. "sequence", "restriction", "codon"
    result_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class PredictionResult(Base):
    __tablename__ = "prediction_results"
    id = Column(UUID(36), primary_key=True, default=gen_uuid)
    sequence_id = Column(UUID(36), ForeignKey("sequences.id"), nullable=False)
    model_name = Column(String, nullable=False)
    prediction = Column(JSON, nullable=False)
    confidence = Column(Float, nullable=True)
    shap_values = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Report(Base):
    __tablename__ = "reports"
    id = Column(UUID(36), primary_key=True, default=gen_uuid)
    sequence_id = Column(UUID(36), ForeignKey("sequences.id"), nullable=False)
    file_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
