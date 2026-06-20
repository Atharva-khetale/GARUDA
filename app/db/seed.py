"""
Seed the `organisms` table with the codon usage tables bundled in
app/services/codon_tables.py so the frontend organism selector and
Module 5/6/7 endpoints have a reference DB row per supported organism.

Usage:
    python -m app.db.seed
"""
from app.db.session import SessionLocal, Base, engine
from app.db import models
from app.services.codon_tables import ORGANISM_CODON_USAGE

DISPLAY_NAMES = {
    "human": "Homo sapiens (Human)",
    "mouse": "Mus musculus (Mouse)",
    "ecoli": "Escherichia coli",
    "yeast": "Saccharomyces cerevisiae (Yeast)",
    "cho": "CHO Cells (Cricetulus griseus)",
}

TAXONOMY_IDS = {
    "human": "9606",
    "mouse": "10090",
    "ecoli": "562",
    "yeast": "4932",
    "cho": "10029",
}


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for key, usage in ORGANISM_CODON_USAGE.items():
            existing = db.query(models.Organism).filter(models.Organism.name == DISPLAY_NAMES[key]).first()
            if existing:
                continue
            db.add(models.Organism(
                name=DISPLAY_NAMES[key],
                taxonomy_id=TAXONOMY_IDS.get(key),
                codon_usage_table=usage,
            ))
        db.commit()
        print(f"Seeded {len(ORGANISM_CODON_USAGE)} organisms.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
