#!/bin/sh

# Wait for the database to be ready
echo "Waiting for postgres..."

while ! nc -z db 5432; do
  sleep 0.1
done

echo "PostgreSQL started"

# Run migrations
if [ -f /app/migrations.sh ]; then
    echo "Running migrations..."
    /app/migrations.sh
fi

# Run seeder
echo "Running database seeder..."
python -m app.seeders.seed

# Run the application
exec "$@"
