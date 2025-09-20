#!/bin/bash

# Set environment variables
export FLASK_APP=sales_sync_backend/app.py
export FLASK_ENV=development

# Run database migrations
flask db upgrade

echo "Database migrations completed successfully"