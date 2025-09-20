#!/bin/bash

# Set environment variables
export FLASK_APP=sales_sync_backend/app.py
export FLASK_ENV=development
export FLASK_DEBUG=1
export ENABLE_API_DOCS=1

# Run Flask application
flask run --host=0.0.0.0 --port=5000