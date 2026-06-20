"""
MODULE 8: BIOLOGICAL DATABASE INTEGRATION

Automated ETL clients for NCBI, UniProt, Ensembl, ClinVar, and AlphaFold.
All data is fetched programmatically (no manual dataset downloads) and
cached locally. These functions are designed to be called from Celery
beat-scheduled tasks (see app/worker.py) for periodic syncing.

NOTE: Network access is required at runtime. In the sandboxed dev
environment these are stubs demonstrating the integration pattern;
wire them up to live endpoints in deployment.
"""
from __future__ import annotations

import httpx

NCBI_EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
UNIPROT_API = "https://rest.uniprot.org/uniprotkb"
ENSEMBL_API = "https://rest.ensembl.org"
CLINVAR_EUTILS = NCBI_EUTILS  # ClinVar is queried via NCBI E-utilities
ALPHAFOLD_API = "https://alphafold.ebi.ac.uk/api/prediction"


async def fetch_ncbi_gene_sequence(accession: str) -> dict:
    """Fetch a gene/nucleotide sequence record from NCBI by accession."""
    params = {
        "db": "nuccore",
        "id": accession,
        "rettype": "fasta",
        "retmode": "text",
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(f"{NCBI_EUTILS}/efetch.fcgi", params=params)
        resp.raise_for_status()
        return {"accession": accession, "fasta": resp.text}


async def fetch_uniprot_protein(uniprot_id: str) -> dict:
    """Fetch protein information and functional annotations from UniProt."""
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(f"{UNIPROT_API}/{uniprot_id}.json")
        resp.raise_for_status()
        return resp.json()


async def fetch_ensembl_gene(gene_id: str, species: str = "homo_sapiens") -> dict:
    """Fetch gene model and ortholog data from Ensembl."""
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"{ENSEMBL_API}/lookup/id/{gene_id}",
            params={"content-type": "application/json", "expand": 1},
        )
        resp.raise_for_status()
        return resp.json()


async def fetch_clinvar_variants(gene_symbol: str) -> dict:
    """Fetch known variants and clinical significance for a gene symbol."""
    params = {"db": "clinvar", "term": f"{gene_symbol}[gene]", "retmode": "json"}
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(f"{CLINVAR_EUTILS}/esearch.fcgi", params=params)
        resp.raise_for_status()
        return resp.json()


async def fetch_alphafold_structure(uniprot_id: str) -> dict:
    """Fetch AlphaFold structure prediction metadata for a UniProt ID."""
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(f"{ALPHAFOLD_API}/{uniprot_id}")
        resp.raise_for_status()
        return resp.json()
