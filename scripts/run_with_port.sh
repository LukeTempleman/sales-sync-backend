#!/bin/bash

# Check if port is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <port>"
  echo "Example: $0 8000"
  exit 1
fi

PORT=$1

# Set environment variables
export FLASK_APP=sales_sync_backend/app.py
export FLASK_ENV=development
export FLASK_DEBUG=1
export ENABLE_API_DOCS=1

# Run Flask application
echo "Starting server on port $PORT..."
flask run --host=0.0.0.0 --port=$PORT