#!/bin/bash

# Set environment variables
export FLASK_APP=sales_sync_backend/app.py
export FLASK_ENV=development

# Initialize database
flask init-db

# Seed database
flask seed-db

echo "Database initialized and seeded successfully."