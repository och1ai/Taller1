#!/bin/bash
echo "Running migrations..."
for migration in /app/app/migrations/*.sql; do
    echo "Applying $migration..."
    psql "$DATABASE_URL" -f "$migration"
done
