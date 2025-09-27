#!/bin/bash

echo "Building and starting services..."
docker-compose up -d --build

echo "Waiting for services to be healthy..."
until docker-compose exec db pg_isready -U user -d user_db > /dev/null 2>&1; do
    echo "Waiting for database to be ready..."
    sleep 2
done

echo "Database is ready! Running seeders..."
docker-compose exec -w /app user_service python -m app.seeders.seed

echo "Setup complete! Services are running at:"
echo "- User Service: http://localhost:8000"
echo "- Mock Main API: http://localhost:8001"
