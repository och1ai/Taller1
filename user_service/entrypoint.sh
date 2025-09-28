#!/bin/sh

# Extract database host from DATABASE_URL
if [ -n "$DATABASE_URL" ]; then
    # Extract host from postgresql://user:pass@host[:port]/db format
    # First try to extract host:port, then fall back to just host
    DB_HOST=$(echo $DATABASE_URL | sed 's|.*@\([^/]*\)/.*|\1|' | sed 's|:\([0-9]*\)$||')
    DB_PORT=$(echo $DATABASE_URL | sed -n 's|.*@[^:]*:\([0-9]\+\)/.*|\1|p')
    
    # If no port was found, default to 5432
    if [ -z "$DB_PORT" ]; then
        DB_PORT=5432
    fi
    
    echo "Parsed DB_HOST: $DB_HOST"
    echo "Parsed DB_PORT: $DB_PORT"
else
    # Fallback for local development
    DB_HOST="db"
    DB_PORT=5432
fi
    DB_HOST="db"
    DB_PORT=5432
fi

# Wait for the database to be ready
echo "Waiting for postgres at $DB_HOST:$DB_PORT..."

while ! nc -z "$DB_HOST" "$DB_PORT"; do
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
