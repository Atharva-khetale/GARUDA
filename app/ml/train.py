"""
Training script for Module 7's construct-viability model.

Generates a synthetic-but-rule-grounded dataset using the same feature
extraction pipeline used at inference time (app/ml/predict.py), trains
an XGBoost classifier, logs the run to MLflow (model registry +
experiment tracking), and saves the model artifact for `predict.py`
to load.

Usage:
    python -m app.ml.train

Replace `generate_training_data` with real labeled data pulled from
Module 8's ETL pipelines (NCBI / UniProt / ClinVar / Ensembl) once
available.
"""
from __future__ import annotations

import os
import random

import numpy as np
import joblib
import mlflow
import mlflow.xgboost
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score

from app.ml.predict import MODEL_DIR, MODEL_PATH, FEATURE_NAMES
from app.services.codon_tables import SUPPORTED_ORGANISMS, ORGANISM_CODON_USAGE, SYNONYMOUS_CODONS


def _random_codon_sequence(num_codons: int, organism: str, optimized: bool) -> str:
    usage = ORGANISM_CODON_USAGE[organism]
    seq_codons = []
    for _ in range(num_codons):
        aa = random.choice([a for a in SYNONYMOUS_CODONS if a != "*"])
        candidates = SYNONYMOUS_CODONS[aa]
        if optimized:
            codon = max(candidates, key=lambda c: usage.get(c, 0))
        else:
            codon = random.choice(candidates)
        seq_codons.append(codon)
    return "ATG" + "".join(seq_codons) + random.choice(["TAA", "TAG", "TGA"])


def generate_training_data(n_samples: int = 1000, seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)

    from app.ml.predict import extract_features

    X, y = [], []
    for i in range(n_samples):
        organism = random.choice(SUPPORTED_ORGANISMS)
        optimized = random.random() < 0.5
        length = random.randint(50, 300)
        dna = _random_codon_sequence(length, organism, optimized)

        feats = extract_features(dna, organism)[0]
        X.append(feats)

        # Ground-truth label heuristic for synthetic supervision:
        # "viable" if expression score high and rare codon density low
        cai, rare_density, expr_score = feats[1], feats[2], feats[3]
        viable_prob = 0.4 * cai + 0.3 * (1 - rare_density) + 0.3 * (expr_score / 100)
        label = 1 if viable_prob + np.random.normal(0, 0.05) > 0.55 else 0
        y.append(label)

    return np.array(X), np.array(y)


def main():
    os.makedirs(MODEL_DIR, exist_ok=True)
    mlflow.set_experiment("garuda-construct-viability")

    X, y = generate_training_data()
    print("Class distribution:", np.unique(y, return_counts=True))
    X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)

    with mlflow.start_run(run_name="xgb-construct-viability"):
        model = XGBClassifier(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            eval_metric="logloss",
        )
        model.fit(X_train, y_train)

        preds = model.predict(X_test)
        proba = model.predict_proba(X_test)[:, 1]
        acc = accuracy_score(y_test, preds)
        if len(np.unique(y_test)) > 1:
            auc = roc_auc_score(y_test, proba)
        else:
            auc = 0.5
    print("Warning: Only one class present in y_test. Using auc=0.5")

        mlflow.log_param("n_samples", len(X))
        mlflow.log_param("features", FEATURE_NAMES)
        mlflow.log_metric("accuracy", acc)
        mlflow.log_metric("roc_auc", auc)
        mlflow.xgboost.log_model(model, "model", registered_model_name="construct-viability")

        joblib.dump(model, MODEL_PATH)
        print(f"Saved model to {MODEL_PATH} | accuracy={acc:.3f} auc={auc:.3f}")


if __name__ == "__main__":
    main()
