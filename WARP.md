# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Essential Development Commands

### Docker Development (Recommended)
```bash
# Start development environment with API docs
docker-compose up -d

# Initialize database with tables and seed data
docker-compose exec api ./scripts/init_db.sh

# Create superadmin user (interactive)
docker-compose exec api ./scripts/create_superadmin.sh

# Create tenant and admin user (interactive)
docker-compose exec api ./scripts/create_tenant_admin.sh

# Run all tests
docker-compose exec api ./scripts/run_tests.sh

# Run tests with coverage
docker-compose exec api ./scripts/run_tests_with_coverage.sh

# Run database migrations
docker-compose exec api ./scripts/run_migrations.sh
```

### Local Development (without Docker)
```bash
# Set up environment
export FLASK_APP=sales_sync_backend/app.py
export FLASK_ENV=development
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/sales_sync

# Install dependencies
pip install -r requirements.txt

# Initialize database
./scripts/init_db.sh

# Run application
./scripts/run.sh

# Run tests (requires test database)
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/sales_sync_test
./scripts/run_tests.sh
```

### Testing Commands
```bash
# Run all tests
./scripts/run_tests.sh

# Run specific test file
pytest -v sales_sync_backend/tests/test_auth.py

# Run tests with SQLite (faster for development)
./scripts/run_tests_with_sqlite.sh

# Run single test method
pytest -v sales_sync_backend/tests/test_auth.py::test_login_success
```

### Database Management
```bash
# Initialize fresh database
./scripts/init_db.sh

# Run database migrations
./scripts/run_migrations.sh

# Create SQLite database for testing
./scripts/init_sqlite_db.sh
```

## Architecture Overview

### Multi-Tenant Architecture
This application implements **row-level tenant separation** where:
- All tenant-scoped models inherit from `TenantScopedMixin`
- Each request is automatically filtered by `tenant_id` from JWT token
- Super admin users can access cross-tenant data
- Tenant context is set via `tenant_middleware.py` before each request

### Core Components Architecture

**Application Factory Pattern**: The app uses Flask's application factory in `app.py` with configuration-based initialization.

**Layered Architecture**:
- **Routes** (`routes/`): Handle HTTP requests, parameter validation, authentication
- **Controllers** (`controllers/`): Orchestrate business logic, handle request/response formatting
- **Services** (`services/`): Core business logic, data transformations, external integrations
- **Models** (`models/`): SQLAlchemy ORM models with tenant-scoped base classes

**Authentication & Authorization**:
- JWT-based authentication with access/refresh token pattern
- Role-based access control with 7 roles: `agent` → `team_leader` → `area_manager` → `regional_manager` → `national_manager` → `admin` → `super_admin`
- Decorators in `utils/auth_decorators.py` handle role enforcement

### Database Design Patterns

**Base Models**: All models extend `BaseModel` with UUID primary keys and timestamps. Tenant-scoped models include `TenantScopedMixin`.

**Cross-Database Compatibility**: Custom type decorators (`UUID`, `JSONB`, `Geography`) ensure compatibility between PostgreSQL and SQLite for testing.

**Audit Trail**: `AuditLog` model tracks all significant actions with tenant isolation.

### Key Business Domains

1. **Tenant Management**: Multi-tenant SaaS with tenant isolation
2. **User & Team Management**: Hierarchical role-based teams
3. **Survey System**: Configurable surveys with custom questions
4. **Visit Tracking**: Geocoded visits with survey completion
5. **Photo & Shelf Share**: Image capture with quadrant-based brand analysis
6. **Goals & Analytics**: Progress tracking with role-scoped KPIs
7. **Call Cycles**: Territory planning and adherence tracking

### Testing Architecture

- **Fixtures**: `conftest.py` provides database setup, test clients, and sample data
- **Test Isolation**: Each test uses fresh database state with proper tenant scoping
- **Dual Database Support**: Tests can run on PostgreSQL (production-like) or SQLite (fast)

## Development Patterns

### Adding New Features
1. Create model in `models/` (inherit from appropriate base classes)
2. Create service in `services/` for business logic
3. Create controller in `controllers/` for request handling
4. Create routes in `routes/` with proper authentication decorators
5. Add comprehensive tests in `tests/`
6. Register new blueprint in `routes/__init__.py`

### Role-Based Access Control
Use decorators from `auth_decorators.py`:
```python
@jwt_required()
@require_role(['admin', 'super_admin'])
@tenant_required  # For tenant-scoped resources
```

### Multi-Tenant Data Access
- All tenant-scoped queries automatically filter by `tenant_id`
- Use `get_current_tenant()` to access tenant context
- Super admin can override tenant filtering for cross-tenant operations

### Database Migrations
- Use Flask-Migrate/Alembic for schema changes
- Run `flask db migrate -m "description"` to create migrations
- Always test migrations on both PostgreSQL and SQLite

### File Storage
- Supports both S3 and local file storage
- Configuration-driven via `S3_BUCKET` environment variable
- Images are processed and validated via `image_utils.py`

## Configuration

### Environment Variables
- `FLASK_ENV`: `development`, `testing`, or `production`
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET_KEY`: JWT signing key (change in production)
- `S3_BUCKET`: S3 bucket for file storage (optional)
- `UPLOAD_FOLDER`: Local file storage path

### Docker Configuration
- Development: `docker-compose.yml` with hot reload and API docs
- Production: `docker-compose.prod.yml` with Nginx and SSL
- Database: PostgreSQL 13 with persistent volumes

### API Documentation
- Swagger UI available at `/api/docs` in development
- Generated from route definitions and marshmallow schemas
- Enable with `ENABLE_API_DOCS=1` environment variable