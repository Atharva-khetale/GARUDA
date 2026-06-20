#!/usr/bin/env bash
<<<<<<<<<HEAD
# Run the GARUDA backend locally WITHOUT Docker.
# Uses a local SQLite database (./garuda.db) - no Postgres/Redis required
# for the core dashboard (synchronous /pipeline/full-analysis endpoint).

# Run the GARUDA Next.js frontend locally WITHOUT Docker.
# Requires Node.js 18+.
>>>>>>> 5bf1095 (Initial commit for frontend)
set -e

cd "$(dirname "$0")"

<<<<<<< HEAD
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
fi

source .venv/bin/activate

echo "Installing dependencies (first run may take a few minutes)..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

if [ ! -f ".env" ]; then
  cp .env.local.example .env
  echo "Created .env from .env.local.example (SQLite mode)."
fi

# Seed reference organism data (idempotent)
python -m app.db.seed || true

echo ""
echo "Starting GARUDA API on http://localhost:8000"
echo "Swagger docs:        http://localhost:8000/api/v1/docs"
echo ""
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
=======
if [ ! -f ".env.local" ]; then
  cp .env.local.example .env.local
  echo "Created .env.local (pointing to http://localhost:8000/api/v1)."
fi

echo "Installing dependencies (first run may take a few minutes)..."
npm install

echo ""
echo "Starting GARUDA frontend on http://localhost:3000"
echo "Make sure the backend is running first: ../run-local.sh"
echo ""
npm run dev
>>>>>>> 5bf1095 (Initial commit for frontend)
