# Running GARUDA Locally (No Docker)

This sets up the full stack — FastAPI backend + Next.js frontend — using a
local SQLite database. No Postgres, Redis, or Docker required for the core
dashboard experience.

**Requirements:** Python 3.11+, Node.js 18+

## 1. Start the backend

```bash
cd garuda
./run-local.sh
```

This script will:
1. Create a Python virtual environment (`.venv/`)
2. Install backend dependencies
3. Copy `.env.local.example` → `.env` (configures SQLite at `./garuda.db`)
4. Seed the `organisms` reference table
5. Start the API at **http://localhost:8000**, docs at
   **http://localhost:8000/api/v1/docs**

## 2. Start the frontend (in a new terminal)

```bash
cd garuda/frontend
./run-local.sh
```

This script will:
1. Copy `.env.local.example` → `.env.local` (points to `http://localhost:8000/api/v1`)
2. `npm install`
3. Start the dev server at **http://localhost:3000**

## 3. Use it

1. Open http://localhost:3000
2. Click **Log in** → switch to **Register** → create an account
3. Go to **Dashboard**, paste a DNA sequence (a sample is pre-filled),
   optionally a mutated version, pick a target organism, and click
   **Run Full Analysis**.
4. View the construct readiness score, expression feasibility breakdown,
   codon optimization before/after, restriction sites, mutation table, and
   ML viability prediction.

## Notes on what's simplified in local/no-Docker mode

- **Database**: SQLite (`garuda.db`) instead of Postgres. Same SQLAlchemy
  models (`app/db/models.py`) — swap `DATABASE_URL` in `.env` to a Postgres
  URL and rerun to switch back.
- **Redis/Celery**: not started. The dashboard uses the synchronous
  `/pipeline/full-analysis` endpoint, so this isn't needed. The async
  `/pipeline/full-analysis-async` endpoint and the Celery worker (background
  reports, scheduled ETL) require Redis — start one separately
  (`redis-server` or `docker run -p 6379:6379 redis:7-alpine`) and run:
  ```bash
  celery -A app.worker.celery_app worker --loglevel=info
  ```
- **MLflow**: the ML prediction endpoint works without it via the heuristic
  fallback in `app/ml/predict.py`. To train and use the XGBoost model:
  ```bash
  source .venv/bin/activate
  python -m app.ml.train
  ```
  This writes `app/ml/artifacts/construct_viability_xgb.joblib`, which
  `predict.py` automatically picks up on the next API request (restart the
  server to be safe).

## Troubleshooting

- **Login/Register fails / CORS error in browser console**: fixed in this
  version — `app/main.py` now whitelists `http://localhost:3000` explicitly
  (a wildcard `*` origin combined with credentials is rejected by browsers).
  If you run the frontend on a different port, add that origin too.
- **"email-validator is not installed" error on register**: `email-validator`
  is now in `requirements.txt` (required by Pydantic's `EmailStr`). Re-run
  `./run-local.sh` to install it.
- **bcrypt warnings/errors on register/login**: `bcrypt` is pinned to
  `4.0.1` for compatibility with `passlib==1.7.4`.
- **Backend won't start due to Celery/Redis import errors**: Celery is now
  optional (`app/worker.py`). The core API and dashboard run fine without it;
  only `/pipeline/full-analysis-async` and the WebSocket job endpoint require
  `pip install -r requirements-extra.txt` plus a running Redis server.
- **Port already in use**: change `--port 8000` in `run-local.sh` or
  `NEXT_PUBLIC_API_URL`/`next dev -p <port>` for the frontend.
- **`Bio` / Biopython import errors**: ensure the venv is activated and
  `pip install -r requirements.txt` completed successfully.
- **Stale `.env`**: if you edited `requirements.txt`/`.env.local.example`
  after a previous run, delete `.venv/` and `.env`/`garuda.db` and re-run
  `./run-local.sh` for a clean setup.

## Quick smoke test (backend only)

After `./run-local.sh` is running, in another terminal:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","passwordA":"password123","full_name":"Test User"}'

curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=password123"
```
The second call should return `{"access_token": "...", "token_type": "bearer"}`.
If both succeed, the frontend login/register will work too.
