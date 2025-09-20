#!/bin/bash

# Create SSL directory if it doesn't exist
mkdir -p nginx/ssl

# Generate self-signed SSL certificate
echo "Generating self-signed SSL certificate for development..."
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/sales_sync.key \
  -out nginx/ssl/sales_sync.crt \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

echo "SSL certificate generated successfully."
echo "Certificate: nginx/ssl/sales_sync.crt"
echo "Private key: nginx/ssl/sales_sync.key"

# Create README file for SSL directory
cat > nginx/ssl/README.md << 'EOF'
# SSL Certificates

This directory contains SSL certificates for the Sales-Sync application.

## Development

For development, you can use self-signed certificates generated with the `generate_ssl_certs.sh` script:

```bash
./scripts/generate_ssl_certs.sh
```

## Production

For production, you should replace these certificates with valid SSL certificates from a trusted certificate authority.

1. Replace the following files with your own certificates:
   - `sales_sync.crt`: SSL certificate
   - `sales_sync.key`: SSL private key

2. Make sure the Nginx configuration in `nginx/conf.d/sales_sync.conf` points to the correct certificate files.

3. Restart the Nginx container:
   ```bash
   docker-compose -f docker-compose.prod.yml restart nginx
   ```
EOF

echo "README file created at nginx/ssl/README.md"