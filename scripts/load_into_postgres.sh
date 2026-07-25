#!/usr/bin/env bash
set -euo pipefail

# Loads a JSON fixture into the database pointed to by DATABASE_URL.
# Usage:
#   export DATABASE_URL='postgresql://...'
#   source .venv/bin/activate
#   ./scripts/load_into_postgres.sh data_dump.json

if [ -z "${DATABASE_URL:-}" ]; then
  echo "ERROR: DATABASE_URL not set. Export it and retry."
  exit 1
fi

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <fixture.json>" >&2
  exit 1
fi

FIXTURE=$1

if [ ! -f "$FIXTURE" ]; then
  echo "Fixture file not found: $FIXTURE" >&2
  exit 1
fi

# Ensure migrations are applied before loading data
python manage.py migrate --noinput

# Load fixtures
python manage.py loaddata "$FIXTURE"

echo "Data loaded from $FIXTURE into DB: ${DATABASE_URL%%@*}"

echo "Reminder: copy media files (media/) to your production storage separately."