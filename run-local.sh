#!/usr/bin/env bash
# Run the GARUDA backend locally WITHOUT Docker.
# Uses a local SQLite database (./garuda.db) - no Postgres/Redis required
# for the core dashboard (synchronous /pipeline/full-analysis endpoint).
set -e

cd "$(dirname "$0")"

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
