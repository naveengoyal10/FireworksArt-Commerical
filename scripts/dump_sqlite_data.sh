#!/usr/bin/env bash
set -euo pipefail

# Dumps most project data from the current (SQLite) database into a JSON fixture.
# Usage:
#   source .venv/bin/activate
#   ./scripts/dump_sqlite_data.sh

OUTFILE="data_dump.json"
EXCLUDE_APPS=("sessions" "django_session" "admin.LogEntry")

# Build exclude flags (empty by default)
EXCLUDE_FLAGS=()
for app in "${EXCLUDE_APPS[@]}"; do
  EXCLUDE_FLAGS+=("-e" "$app")
done

echo "Dumping data to $OUTFILE (excluding sessions and admin log entries)..."
python manage.py dumpdata --natural-foreign --natural-primary "-e" contenttypes --indent 2 > "$OUTFILE"

echo "NOTE: This dump includes contenttypes and permissions. If you have custom app hooks that expect a different state, review $OUTFILE before loading."

echo "Done: $OUTFILE"

echo "Remember to copy your media directory (media/) to the production storage (S3 or server) separately."