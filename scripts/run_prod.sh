#!/bin/bash

# Set environment variables
export FLASK_APP=sales_sync_backend/app.py
export FLASK_ENV=production
export FLASK_DEBUG=0

# Run gunicorn
gunicorn --bind 0.0.0.0:5000 "sales_sync_backend.app:create_app()"