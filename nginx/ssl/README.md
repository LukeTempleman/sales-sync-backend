# SSL Certificates

Place your SSL certificates in this directory:

- `cert.pem`: SSL certificate
- `key.pem`: SSL private key

For development or testing, you can generate self-signed certificates using:

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout key.pem -out cert.pem
```

For production, use certificates from a trusted certificate authority.