#!/bin/bash

# Set environment variables
export FLASK_APP=sales_sync_backend/app.py
export FLASK_ENV=testing
export DATABASE_URL=sqlite:///test.db
export TESTING=True

# Run tests
pytest -v sales_sync_backend/tests/