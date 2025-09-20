#!/bin/bash

# Set environment variables
export FLASK_APP=sales_sync_backend/app.py
export FLASK_ENV=development
export DATABASE_URL=sqlite:///sales_sync.db

# Create database directory if it doesn't exist
mkdir -p instance

# Initialize database
echo "Creating database tables..."
flask db upgrade

# Seed database with initial data
echo "Seeding database with initial data..."
flask seed-db

echo "SQLite database initialized successfully."