#!/bin/bash

# Wait for database to be ready
echo "Waiting for postgres..."
while ! pg_isready -h db -p 5432 -U postgres; do
  sleep 1
done
echo "PostgreSQL started"

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Seed data if needed (optional)
# echo "Seeding data..."
# python manage.py seed_data

# Train MiniLM model to generate embeddings
echo "Generating product embeddings..."
python manage.py train_minilm

# Start server
echo "Starting server..."
python manage.py runserver 0.0.0.0:8000
