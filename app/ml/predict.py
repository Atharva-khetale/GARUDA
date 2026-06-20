"""
MODULE 7: MACHINE LEARNING PREDICTION ENGINE

Traditional ML only (XGBoost / Random Forest) — no generative AI, no
LLM dependencies. Predicts construct viability and expression success
from sequence-derived features computed by Modules 1, 5, and 6.

Models are trained on a synthetic-but-biologically-grounded dataset
generated from the deterministic feature functions in this codebase
(see train.py). In production, replace `generate_training_data` with
real labeled data sourced via Module 8's ETL pipelines, and track
training runs in MLflow (see app/ml/mlops.py).
"""
from __future__ import annotations

import os
import joblib
import numpy as np

from app.services.codon_service import calculate_cai, find_rare_codons
from app.services.codon_tables import SUPPORTED_ORGANISMS
from app.services.sequence_service import gc_content, codon_frequency_table
from app.services.expression_service import assess_expression_feasibility

MODEL_DIR = os.path.join(os.path.dirname(__file__), "artifacts")
MODEL_PATH = os.path.join(MODEL_DIR, "construct_viability_xgb.joblib")

FEATURE_NAMES = [
    "gc_content",
    "cai",
    "rare_codon_density",
    "expression_score",
    "sequence_length",
    "five_prime_gc",
]


def extract_features(dna: str, organism: str) -> np.ndarray:
    dna = dna.upper()
    gc = gc_content(dna)
    cai = calculate_cai(dna, organism)
    codon_table = codon_frequency_table(dna)
    rare = find_rare_codons(dna, organism)
    rare_density = len(rare) / max(1, codon_table["total_codons"])
    expression = assess_expression_feasibility(dna, organism)
    five_prime_gc = gc_content(dna[:30]) if len(dna) >= 3 else gc

    return np.array([[
        gc,
        cai,
        rare_density,
        expression["expression_score"],
        len(dna),
        five_prime_gc,
    ]], dtype=float)


def _load_model():
    if not os.path.exists(MODEL_PATH):
        return None
    return joblib.load(MODEL_PATH)


def predict_construct_viability(dna: str, organism: str) -> dict:
    """
    Returns construct viability prediction with confidence and feature
    importance / SHAP-based explainability. Falls back to a rule-based
    heuristic (still non-LLM) if no trained model artifact is present.
    """
    features = extract_features(dna, organism)
    model = _load_model()

    if model is not None:
        proba = model.predict_proba(features)[0]
        viable_proba = float(proba[1])
        prediction = "Viable" if viable_proba >= 0.5 else "Not Viable"

        try:
            import shap
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(features)
            sv = shap_values[1][0] if isinstance(shap_values, list) else shap_values[0]
            shap_dict = {name: round(float(val), 4) for name, val in zip(FEATURE_NAMES, sv)}
        except Exception:
            shap_dict = {}

        importances = getattr(model, "feature_importances_", None)
        feature_importance = (
            {name: round(float(val), 4) for name, val in zip(FEATURE_NAMES, importances)}
            if importances is not None else {}
        )

        return {
            "model": "xgboost-construct-viability-v1",
            "prediction": prediction,
            "confidence": round(viable_proba if prediction == "Viable" else 1 - viable_proba, 4),
            "viability_probability": round(viable_proba, 4),
            "feature_importance": feature_importance,
            "shap_values": shap_dict,
            "features": dict(zip(FEATURE_NAMES, features[0].tolist())),
        }

    # --- Heuristic fallback (no trained artifact yet) ---
    f = dict(zip(FEATURE_NAMES, features[0].tolist()))
    score = (
        0.3 * min(1.0, f["cai"])
        + 0.25 * (1 - f["rare_codon_density"])
        + 0.25 * (f["expression_score"] / 100)
        + 0.2 * (1 - abs(f["gc_content"] - 50) / 50)
    )
    prediction = "Viable" if score >= 0.5 else "Not Viable"
    return {
        "model": "heuristic-fallback-v0 (train an XGBoost model via app/ml/train.py for production use)",
        "prediction": prediction,
        "confidence": round(score if prediction == "Viable" else 1 - score, 4),
        "viability_probability": round(score, 4),
        "feature_importance": {},
        "shap_values": {},
        "features": f,
    }
