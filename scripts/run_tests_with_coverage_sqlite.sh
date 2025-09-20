#!/bin/bash

# Set environment variables
export FLASK_APP=sales_sync_backend/app.py
export FLASK_ENV=testing
export DATABASE_URL=sqlite:///test.db
export TESTING=True

# Run tests with coverage
pytest --cov=sales_sync_backend --cov-report=term-missing --cov-report=html sales_sync_backend/tests/

echo "Coverage report generated in htmlcov/ directory"