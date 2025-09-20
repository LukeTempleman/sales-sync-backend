#!/bin/bash

# Set environment variables
export FLASK_APP=sales_sync_backend/app.py
export FLASK_ENV=testing
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/sales_sync_test

# Run tests with coverage
pytest --cov=sales_sync_backend --cov-report=term --cov-report=html:coverage_report -v sales_sync_backend/tests/

echo "Coverage report generated in coverage_report directory"