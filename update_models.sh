#!/bin/bash

# Update all model files to use the custom UUID type
find /workspace/sales_sync_backend/models -type f -name "*.py" -not -path "*/\.*" | while read -r file; do
    # Skip base.py as we've already updated it
    if [[ "$file" == *"/base.py" ]]; then
        continue
    fi
    
    # Replace the import statement
    sed -i 's/from sqlalchemy.dialects.postgresql import UUID/from models.base import UUID/' "$file"
    
    # Also handle cases where it's imported as PostgresUUID
    sed -i 's/from sqlalchemy.dialects.postgresql import UUID as PostgresUUID/from models.base import UUID/' "$file"
    
    echo "Updated $file"
done

echo "All model files updated to use the custom UUID type."