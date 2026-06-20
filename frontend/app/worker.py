"""
Celery application for asynchronous task processing.

Used for:
  - Large/batch sequence analyses
  - PDF report generation
  - ML prediction jobs
  - Database synchronization with NCBI/UniProt/Ensembl/ClinVar/AlphaFold
"""
from app.core.config import settings

try:
    from celery import Celery
    CELERY_AVAILABLE = True
except ImportError:  # celery/redis not installed in this environment
    Celery = None
    CELERY_AVAILABLE = False


if CELERY_AVAILABLE:
    celery_app = Celery(
        "garuda",
        broker=settings.REDIS_URL,
        backend=settings.REDIS_URL,
    )

    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        beat_schedule={
            "sync-organism-codon-tables-nightly": {
                "task": "garuda.sync_reference_data",
                "schedule": 60 * 60 * 24,  # every 24h
            },
        },
    )
    task = celery_app.task
else:
    class _NoCeleryApp:
        """Stub used when celery/redis are not installed (e.g. local SQLite mode).
        Install requirements-extra.txt and a Redis server to enable async jobs."""

        def task(self, *args, **kwargs):
            def decorator(func):
                func.delay = self._unavailable
                return func
            return decorator

        @staticmethod
        def _unavailable(*args, **kwargs):
            raise RuntimeError(
                "Async task queue unavailable: install requirements-extra.txt "
                "(celery, redis) and run a Redis server + Celery worker."
            )

        def AsyncResult(self, task_id):
            raise RuntimeError(
                "Async task queue unavailable: install requirements-extra.txt "
                "(celery, redis) and run a Redis server + Celery worker."
            )

    celery_app = _NoCeleryApp()
    task = celery_app.task


@task(name="garuda.sync_reference_data")
def sync_reference_data_task():
    """
    Module 8 scheduled ETL: refresh cached organism/gene/protein/variant
    reference data from NCBI, UniProt, Ensembl, ClinVar, and AlphaFold.
    Intended to run on Celery beat (see beat_schedule above). Populate
    the `organisms` table and any per-gene caches in Postgres here.
    """
    import asyncio
    from app.services import external_db_service as ext

    async def _run():
        # Example: refresh a small reference set. Extend with real
        # gene/accession lists pulled from the `organisms` table.
        results = {}
        try:
            results["ncbi_sample"] = await ext.fetch_ncbi_gene_sequence("NM_000546")
        except Exception as e:
            results["ncbi_sample"] = {"error": str(e)}
        return results

    return asyncio.run(_run())


@task(name="garuda.run_full_analysis")
def run_full_analysis_task(original_sequence: str, mutated_sequence: str | None, organism: str):
    from app.services import (
        sequence_service, mutation_service, protein_service,
        restriction_service, codon_service, expression_service, readiness_service,
    )
    from app.ml import predict as ml_predict
    from app.services.parsing import strip_fasta

    original = strip_fasta(original_sequence)
    seq_analysis = sequence_service.analyze_sequence(original, "DNA")
    restriction = restriction_service.analyze_restriction_sites(original)
    optimization = codon_service.optimize_sequence(original, organism)
    expression = expression_service.assess_expression_feasibility(original, organism)

    mutation_report, protein_impact = None, None
    if mutated_sequence:
        mutated = strip_fasta(mutated_sequence)
        mutation_report = mutation_service.detect_mutations(original, mutated)
        protein_impact = protein_service.analyze_protein_impact(original, mutated)

    readiness = readiness_service.compute_readiness_score(
        expression_result=expression,
        mutation_summary=mutation_report["summary"] if mutation_report else None,
        protein_impact=protein_impact,
        restriction_result=restriction,
        codon_optimization=optimization,
    )
    ml_prediction = ml_predict.predict_construct_viability(original, organism)

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


@task(name="garuda.generate_pdf_report")
def generate_pdf_report_task(analysis_result: dict, output_path: str):
    from app.services.report_service import generate_pdf_report
    return generate_pdf_report(analysis_result, output_path)
