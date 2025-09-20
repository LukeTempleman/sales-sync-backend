#!/bin/bash

# Set environment variables
export FLASK_APP=sales_sync_backend/app.py
export FLASK_ENV=development

# Generate API documentation
echo "Generating API documentation..."
python -c "from sales_sync_backend.utils.api_docs import create_spec, register_schemas, register_all_routes; spec = create_spec(); register_schemas(spec); register_all_routes(spec); print(spec.to_yaml())" > api_docs.yaml

echo "API documentation generated successfully at api_docs.yaml"
echo "You can view the API documentation at http://localhost:5000/api/docs"