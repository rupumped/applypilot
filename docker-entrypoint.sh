#!/bin/sh
# Run DB migrations before uvicorn so `make start` / `just start` need no extra step.
# Compose injects DATABASE_URL (and friends); no .env file is baked into the image.
set -e
cd /app
python scripts/run_alembic.py upgrade
exec "$@"
