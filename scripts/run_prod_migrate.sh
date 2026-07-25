#!/usr/bin/env bash
set -euo pipefail

# Usage: export DATABASE_URL='postgres://user:pass@host:port/dbname'
# Activate your virtualenv first: source .venv/bin/activate

if [ -z "${DATABASE_URL:-}" ]; then
  echo "ERROR: DATABASE_URL is not set. Export it and retry."
  exit 1
fi

echo "Running Django migrations against: ${DATABASE_URL%%@*}..."
python -u manage.py migrate --noinput

echo "Migrations completed successfully."
