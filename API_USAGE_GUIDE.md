# Sales Sync Backend API Usage Guide

## Overview
This guide provides instructions for using the Sales Sync Backend API with the provided Postman collection.

## Files Created
1. **Sales_Sync_Backend_API.postman_collection.json** - Complete Postman collection with all API endpoints
2. **Sales_Sync_Backend.postman_environment.json** - Environment variables for the collection

## Quick Start

### 1. Import into Postman
1. Open Postman
2. Click "Import" button
3. Import both files:
   - `Sales_Sync_Backend_API.postman_collection.json`
   - `Sales_Sync_Backend.postman_environment.json`

### 2. Start the API Server
```bash
cd sales_sync_backend
docker-compose up
```

### 3. Basic Authentication Flow
1. **Register** (creates tenant and admin user):
   ```json
   POST /api/auth/register
   {
     "email": "admin@example.com",
     "password": "Password123",
     "first_name": "John",
     "last_name": "Doe",
     "phone": "+1234567890",
     "tenant_name": "Example Corp",
     "subdomain": "example"
   }
   ```

2. **Login** (get JWT tokens):
   ```json
   POST /api/auth/login
   {
     "email": "admin@example.com",
     "password": "Password123"
   }
   ```

The Postman collection automatically extracts and sets JWT tokens from login responses.

## API Endpoints Summary

### Authentication
- `POST /api/auth/register` - Register new tenant and admin
- `POST /api/auth/login` - Login and get JWT tokens
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Logout and revoke tokens
- `POST /api/auth/forgot-password` - Request password reset
- `POST /api/auth/reset-password` - Reset password with token

### Core Resources
- **Users**: CRUD operations, role management
- **Brands**: Brand management with infographics
- **Surveys**: Survey creation with proper field validation
- **Visits**: Visit scheduling and completion
- **Teams**: Team management with members
- **Goals**: Goal setting and progress tracking
- **Call Cycles**: Route planning and management
- **Photos**: Photo management with shelf analysis

### Analytics & Admin
- **Analytics**: Overview, visits, shelf share, call cycle coverage
- **Admin**: User activity, survey completion rates
- **Audit**: Audit log access
- **Tenants**: Multi-tenant management
- **Roles**: Role definitions

## Important Survey Field Requirements

**Survey Creation** requires these specific fields:
```json
{
  "name": "Survey Name",           // Required
  "type": "shop",                  // Required: "individual" or "shop"
  "brand_id": "uuid-optional",     // Optional
  "active": true                   // Optional, defaults to true
}
```

## Authentication Notes

1. **JWT Tokens**: All protected endpoints require `Authorization: Bearer <token>` header
2. **Token Auto-Management**: The Postman collection automatically:
   - Extracts tokens from login/register responses
   - Sets Authorization headers for protected endpoints
   - Stores user/tenant IDs for reference

3. **Token Expiration**: Access tokens expire after 15 minutes. Use the refresh endpoint or login again.

## Role-Based Access Control

- **superadmin**: Full system access
- **admin**: Tenant-wide management
- **manager**: Team and user management
- **agent**: Basic operations and data entry

## Database Setup

If you encounter "table does not exist" errors:
```bash
cd sales_sync_backend
python manage.py init_db
python manage.py seed_db
```

## Common Issues Fixed

1. **Survey Validation**: Updated field names from `title` to `name` and added required `type` field
2. **Database Session**: Fixed `request.app.db_session` to `current_app.db_session` across all controllers
3. **SQLAlchemy Warnings**: Added overlaps parameters to relationship definitions
4. **Missing Tables**: Proper database initialization and seeding

## Testing the API

The Postman collection includes example requests for all endpoints. Key test scenarios:

1. **Authentication Flow**: Register → Login → Access protected endpoints
2. **CRUD Operations**: Create, Read, Update, Delete for all resources
3. **Multi-tenant Isolation**: Users can only access their tenant's data
4. **Role Permissions**: Different endpoints require different roles

## Environment Variables

The collection uses these environment variables:
- `baseUrl`: API base URL (default: http://localhost:5000)
- `accessToken`: JWT access token (auto-managed)
- `refreshToken`: JWT refresh token (auto-managed)
- `userId`: Current user ID (auto-extracted)
- `tenantId`: Current tenant ID (auto-extracted)

## Support

For issues:
1. Check the API is running on http://localhost:5000
2. Verify database is initialized and seeded
3. Ensure JWT tokens are valid (not expired)
4. Check endpoint-specific role requirements

All endpoints return appropriate HTTP status codes and error messages for debugging.