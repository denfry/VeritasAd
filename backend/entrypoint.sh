#!/bin/sh
set -e

# Run Alembic migrations before startup unless explicitly disabled.
if [ "$SKIP_MIGRATIONS" != "true" ]; then
    echo "Running Alembic migrations..."
    i=1
    while [ "$i" -le 5 ]; do
        if alembic upgrade head; then
            break
        fi
        echo "Migration attempt $i failed, retrying in 2s..."
        sleep 2
        i=$((i + 1))
    done
else
    echo "Skipping migrations as requested..."
fi

exec "$@"
