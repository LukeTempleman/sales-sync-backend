#!/bin/bash

# Set environment variables
export FLASK_APP=sales_sync_backend/app.py
export FLASK_ENV=development

# Seed the database with initial data
flask seed-db

echo "Database seeded successfully"