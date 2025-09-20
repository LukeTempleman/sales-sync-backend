#!/bin/bash

# Set environment variables
export FLASK_APP=sales_sync_backend/app.py
export FLASK_ENV=development

# Create tenant and admin
flask create-tenant-admin