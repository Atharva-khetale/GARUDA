# GARUDA
**G**enetic **A**nalysis, **R**esearch, **U**nderstanding, **D**esign & **A**ssessment

A unified bioinformatics platform that lets researchers evaluate engineered DNA
constructs — sequence validity, mutations, protein impact, restriction sites,
codon optimization, expression feasibility, and ML-based viability — in one
pipeline call instead of switching between five separate tools.

This repository contains the **backend API (production-ready FastAPI service)**
that implements Modules 1–10 of the GARUDA specification with real
Biopython-based bioinformatics logic (no mocked science). Frontend mockups for
the Next.js dashboard were generated separately (see `frontend/` notes below)
and plug into this API.

---

## 0. Quick start (no Docker)

```bash
cd garuda && ./run-local.sh          # backend on :8000 (SQLite)
cd garuda/frontend && ./run-local.sh # frontend on :3000
```

See **[LOCAL_SETUP.md](./LOCAL_SETUP.md)** for full details.

## 1. What's implemented vs. roadmap

| Module | Status |
|---|---|
| 1. Sequence Analysis Engine (validation, GC%, ORF, codon stats, transcription/translation) | ✅ Implemented (Biopython) |
| 2. Mutation Analysis Engine (SNP/indel/frameshift/silent/missense/nonsense) | ✅ Implemented |
| 3. Protein Impact Analysis (functional impact score 0–100) | ✅ Implemented |
| 4. Restriction Enzyme Analysis (EcoRI, BamHI, HindIII, XhoI, NotI, PstI + map + add/remove suggestions) | ✅ Implemented (Bio.Restriction) |
| 5. Codon Optimization Engine (CAI, rare codons, optimized sequence, before/after) | ✅ Implemented (5 organisms) |
| 6. Expression Feasibility Engine (0–100 score, weighted components, reasoning) | ✅ Implemented |
| 7. ML Prediction Engine (XGBoost construct viability, SHAP, feature importance) | ✅ Implemented w/ training script + heuristic fallback |
| 8. Biological Database Integration (NCBI/UniProt/Ensembl/ClinVar/AlphaFold) | ✅ ETL client stubs (real endpoints, async httpx) — wire to Celery beat in deployment |
| 9. Experiment Readiness Score | ✅ Implemented |
| 10. PDF Report Generation | ✅ Implemented (ReportLab) |
| Auth (JWT, RBAC), rate limiting, Swagger docs | ✅ Implemented |
| Celery/Redis async pipeline + report jobs | ✅ Implemented |
| MLflow training/registry | ✅ Training script wired to MLflow |
| Docker Compose (api, worker, db, redis, mlflow, nginx) | ✅ Implemented |
| CI/CD (GitHub Actions: test, build, retrain) | ✅ Implemented |
| Next.js/ShadCN frontend (dashboard, sequence upload, mutation explorer, dark mode) | 🚧 Wireframes generated (Stitch exports in uploaded project); integrate against this API's `/api/v1` endpoints |
| WebSockets for live job progress | 🚧 Stub — add a `/ws/jobs/{id}` channel that subscribes to Celery task state |
| Alembic migrations | 🚧 Models defined; run `alembic init` and autogenerate against `app/db/models.py` |

---

## 2. Architecture overview

```
                         ┌─────────────────────┐
                         │   Next.js Frontend   │
                         │ (dashboard, upload,  │
                         │  mutation explorer)  │
                         └──────────┬───────────┘
                                    │ HTTPS / JWT
                         ┌──────────▼───────────┐
                         │   Nginx (reverse      │
                         │   proxy / TLS)        │
                         └──────────┬───────────┘
                                    │
                         ┌──────────▼───────────┐
                         │   FastAPI (api)       │◄──── Swagger /api/v1/docs
                         │  - Auth (JWT/RBAC)    │
                         │  - Rate limiting       │
                         │  - Modules 1-6,9,10    │
                         └───┬───────────┬───────┘
                             │           │
                  ┌──────────▼──┐   ┌────▼─────────┐
                  │ PostgreSQL  │   │ Redis (broker)│
                  │ (users,     │   └────┬─────────┘
                  │ sequences,  │        │
                  │ mutations,  │   ┌────▼─────────┐
                  │ results...) │   │ Celery Worker │
                  └─────────────┘   │ - full pipeline│
                                     │ - PDF reports  │
                                     │ - ETL syncs    │
                                     └────┬───────────┘
                                          │
                              ┌───────────▼────────────┐
                              │ External APIs (Module 8)│
                              │ NCBI / UniProt /        │
                              │ Ensembl / ClinVar /     │
                              │ AlphaFold               │
                              └─────────────────────────┘

                  ┌─────────────────────────────┐
                  │  MLflow (Module 7 MLOps)     │
                  │  - experiment tracking        │
                  │  - model registry             │
                  │  - app/ml/train.py            │
                  └─────────────────────────────┘
```

---

## 3. Folder structure

```
garuda/
├── app/
│   ├── main.py                  # FastAPI app, middleware, rate limiter
│   ├── worker.py                 # Celery app + async tasks
│   ├── core/
│   │   ├── config.py              # env-based settings
│   │   └── security.py            # JWT + password hashing
│   ├── db/
│   │   ├── session.py             # SQLAlchemy engine/session
│   │   └── models.py              # Users, Projects, Sequences, Proteins,
│   │                               # Mutations, Experiments, AnalysisResults,
│   │                               # PredictionResults, Reports, Organisms
│   ├── schemas/schemas.py        # Pydantic request/response models
│   ├── api/
│   │   ├── deps.py                # auth dependencies / RBAC
│   │   └── v1/
│   │       ├── api.py             # router aggregation
│   │       └── endpoints/
│   │           ├── auth.py        # register/login (JWT)
│   │           ├── sequence.py    # Module 1
│   │           ├── mutation.py    # Module 2 + 3
│   │           ├── restriction.py # Module 4
│   │           ├── codon.py       # Module 5
│   │           └── pipeline.py    # Module 6, 7, 9 + full pipeline
│   ├── services/                 # pure bioinformatics logic (no FastAPI deps)
│   │   ├── codon_tables.py        # genetic code + organism codon usage tables
│   │   ├── parsing.py             # FASTA stripping
│   │   ├── sequence_service.py    # Module 1
│   │   ├── mutation_service.py    # Module 2
│   │   ├── protein_service.py     # Module 3
│   │   ├── restriction_service.py # Module 4
│   │   ├── codon_service.py       # Module 5 (CAI, optimization)
│   │   ├── expression_service.py  # Module 6
│   │   ├── readiness_service.py   # Module 9
│   │   ├── report_service.py      # Module 10 (PDF via ReportLab)
│   │   └── external_db_service.py # Module 8 (NCBI/UniProt/Ensembl/ClinVar/AlphaFold)
│   └── ml/
│       ├── predict.py             # feature extraction + inference (XGBoost/SHAP)
│       ├── train.py                # MLflow-tracked training script
│       └── artifacts/              # saved model artifacts (.joblib)
├── tests/test_services.py        # unit tests for all bioinformatics modules
├── nginx/nginx.conf
├── .github/workflows/ci.yml       # test -> build -> retrain pipeline
├── Dockerfile
├── docker-compose.yml             # api, worker, db, redis, mlflow, nginx
├── requirements.txt
└── .env.example
```

---

## 4. Database schema (PostgreSQL)

| Table | Key columns |
|---|---|
| `users` | id (UUID), email, hashed_password, role (admin/researcher/viewer), is_active |
| `organisms` | id, name, taxonomy_id, codon_usage_table (JSON) |
| `projects` | id, owner_id → users, name, description |
| `sequences` | id, project_id → projects, name, seq_type, raw_sequence, organism_id, gc_content, length |
| `proteins` | id, sequence_id → sequences, protein_sequence, length, molecular_weight, uniprot_id |
| `mutations` | id, sequence_id → sequences, position, original_codon, mutated_codon, mutation_type, impact, severity, severity_score |
| `experiments` | id, project_id, sequence_id, experiment_type, target_organism_id, status |
| `analysis_results` | id, sequence_id, module, result_json, created_at |
| `prediction_results` | id, sequence_id, model_name, prediction (JSON), confidence, shap_values (JSON) |
| `reports` | id, sequence_id, file_path, created_at |

All defined in `app/db/models.py`. Generate Alembic migrations with:
```bash
alembic init migrations
alembic revision --autogenerate -m "init"
alembic upgrade head
```

---

## 5. API design (v1)

Base path: `/api/v1` · Interactive docs: `/api/v1/docs`

| Endpoint | Method | Module | Description |
|---|---|---|---|
| `/auth/register` | POST | — | Create a researcher account |
| `/auth/login` | POST | — | OAuth2 password flow → JWT |
| `/sequence/analyze` | POST | 1 | Validate + analyze DNA/RNA/Protein, ORFs, codon table, GC% |
| `/mutation/analyze` | POST | 2, 3 | Compare original vs mutated sequence → mutation report + protein impact |
| `/restriction/analyze` | POST | 4 | Cut sites for EcoRI/BamHI/HindIII/XhoI/NotI/PstI + restriction map |
| `/restriction/{enzyme}/remove-suggestions` | GET | 4 | Silent-mutation suggestions to remove a site |
| `/restriction/{enzyme}/add-suggestions` | GET | 4 | Feasibility check for introducing a site |
| `/codon/optimize` | POST | 5 | CAI before/after, rare codons, optimized sequence |
| `/codon/usage` | POST | 5 | Codon usage comparison vs. organism reference |
| `/expression/analyze` | POST | 6 | 0–100 expression score with weighted reasoning |
| `/ml/predict-viability` | POST | 7 | XGBoost construct viability, confidence, SHAP, feature importance |
| `/pipeline/full-analysis` | POST | 1,2,3,4,5,6,7,9 | Runs the entire GARUDA pipeline in one call |

All endpoints (except `/auth/*` and `/health`) require `Authorization: Bearer <JWT>`.
Rate limiting: 60 requests/minute/IP (in-memory; swap for Redis-backed limiter at scale).

### Example: full pipeline call
```bash
curl -X POST http://localhost:8000/api/v1/pipeline/full-analysis \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
        "original_sequence": "ATGGCCATTGTAATGGGCCGCTGA",
        "mutated_sequence": "ATGGCCATTGTAATGTGCCGCTGA",
        "organism": "human"
      }'
```
Response includes `sequence_analysis`, `restriction_analysis`,
`codon_optimization`, `expression_feasibility`, `mutation_report`,
`protein_impact`, `ml_prediction`, and `readiness_score`.

---

## 6. ML architecture (Module 7)

- **Feature extraction** (`app/ml/predict.py`): GC content, CAI, rare-codon
  density, expression score, sequence length, 5′ GC — all derived
  deterministically from Modules 1, 5, 6 (no leakage from labels).
- **Model**: XGBoost binary classifier (`construct viable / not viable`),
  with Random Forest / LightGBM swappable via the same feature vector.
- **Explainability**: SHAP `TreeExplainer` values + `feature_importances_`
  returned alongside every prediction.
- **Training** (`app/ml/train.py`): generates a biologically-grounded
  synthetic dataset from the same feature pipeline (replace with real
  labeled data from Module 8 ETL once available), logs params/metrics/model
  to **MLflow** (experiment tracking + model registry), saves a `.joblib`
  artifact consumed by `predict.py`.
- **Fallback**: if no trained artifact exists yet, `predict.py` uses a
  transparent rule-based heuristic (still non-LLM) so the API never breaks.
- **Drift monitoring / retraining**: the CI workflow includes a
  `train-model` job that can be scheduled (cron trigger) to retrain and
  re-upload the artifact; wire MLflow's model registry stage transitions to
  gate promotion to production.
- **Security**: model weights, training data, and scoring logic stay
  server-side — only predictions/scores/explanations are exposed via the API.

---

## 7. Data ingestion architecture (Module 8)

`app/services/external_db_service.py` provides async clients for:
- **NCBI E-utilities** — gene/nucleotide sequences
- **UniProt REST** — protein info & functional annotations
- **Ensembl REST** — gene models & orthologs
- **ClinVar (via NCBI E-utilities)** — known variants & clinical significance
- **AlphaFold DB** — structure prediction metadata

In production, schedule these via **Celery beat** (add a `beat_schedule` to
`app/worker.py`) to populate the `organisms`, `sequences`, and
`prediction_results` tables on a cadence (e.g. nightly), with results cached
in Postgres and re-fetched only on TTL expiry.

---

## 8. Deployment architecture

- **Local/dev**: `docker compose up --build` brings up `api`, `worker`, `db`
  (Postgres), `redis`, `mlflow`, and `nginx`.
- **Production (AWS)**:
  - `api` + `worker` → ECS Fargate services (or EKS), behind an ALB
  - `db` → RDS Postgres (Multi-AZ)
  - `redis` → ElastiCache
  - `mlflow` → ECS service with S3 artifact store + RDS/Postgres backend store
  - Static frontend → S3 + CloudFront
  - Secrets → AWS Secrets Manager, injected as env vars
  - Logs/metrics → CloudWatch; add OpenTelemetry exporters for tracing
- **CI/CD** (`.github/workflows/ci.yml`): test → build Docker image → (push
  to registry — add your ECR/GHCR login step) → scheduled model retraining job.

---

## 9. Running locally

```bash
cp .env.example .env
docker compose up --build
# API:    http://localhost:8000/api/v1/docs
# MLflow: http://localhost:5000
```

Train the initial ML model (creates `app/ml/artifacts/construct_viability_xgb.joblib`):
```bash
docker compose exec api python -m app.ml.train
```

Run tests:
```bash
docker compose exec api pytest -q
```

---

## 10. Roadmap

**MVP (Sprints 1–3)**
1. Sprint 1: Modules 1–4 + auth + DB schema + Docker (this repo's core).
2. Sprint 2: Modules 5–6, 9, 10 (optimization, expression, readiness, PDF).
3. Sprint 3: Module 7 ML pipeline + MLflow, basic Next.js dashboard wired to API.

**Production roadmap (Sprints 4–8)**
4. Module 8 ETL pipelines on Celery beat; populate `organisms`/reference data.
5. WebSocket job-progress channel; async job UI in frontend.
6. Alembic migrations, audit logging, API key issuance for B2B customers.
7. AWS deployment (ECS/RDS/ElastiCache), CloudWatch monitoring, autoscaling.
8. Drift monitoring + automated retraining gates; multi-tenant billing (SaaS).

---

## 11. Frontend

A working Next.js 14 (App Router) + TypeScript + Tailwind frontend lives in
`frontend/`:

```
frontend/
├── app/
│   ├── page.tsx          # landing page
│   ├── login/page.tsx    # login / register (JWT)
│   ├── dashboard/page.tsx# sequence input form + full results dashboard
│   ├── layout.tsx, globals.css
├── components/Navbar.tsx, ScoreCard.tsx, SeverityPill.tsx
├── lib/api.ts            # typed API client (auth, full-analysis)
├── run-local.sh
└── .env.local.example    # NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

It calls `/auth/register`, `/auth/login`, and `/pipeline/full-analysis` and
renders the construct readiness score, expression breakdown (with bar
charts), codon optimization before/after, restriction map table, mutation
table with severity pills, protein impact, and ML viability prediction with
feature importances — all in a dark "scientific SaaS" theme.

The uploaded Stitch project (`project_ashwini_*` folders) contains additional
high-fidelity mockups (project management, admin panel, report viewer) that
can be incorporated as further pages calling the same API.

