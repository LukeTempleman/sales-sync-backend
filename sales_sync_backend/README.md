# Sales-Sync Backend

A Flask-based backend for the Sales-Sync application with multi-tenancy, JWT authentication, and PostgreSQL database.

## Features

- Multi-tenant architecture with row-level tenant separation
- JWT-based authentication with role-based access control
- RESTful API for managing sales visits, surveys, brands, and more
- PostgreSQL database with SQLAlchemy ORM
- Alembic migrations
- Docker and docker-compose setup for easy deployment

## Tech Stack

- Flask (application)
- Flask-JWT-Extended (JWT access + refresh tokens)
- SQLAlchemy (ORM)
- Alembic / Flask-Migrate (migrations)
- Marshmallow (request/response schemas & validation)
- psycopg2 (Postgres driver)
- pytest + pytest-flask (unit tests)
- passlib / bcrypt (password hashing)
- Celery (optional) for async tasks
- S3-compatible storage (or local storage) for images

## Getting Started

### Prerequisites

- Docker and docker-compose

### Development Setup

1. Clone the repository
2. Copy the example environment file:
   ```
   cp .env.example .env
   ```
3. Start the development environment:
   ```
   docker-compose up -d
   ```
4. Create a superadmin user:
   ```
   docker-compose exec api python manage.py create-superadmin
   ```

### Production Setup

1. Clone the repository
2. Copy the example environment file and update with production values:
   ```
   cp .env.example .env
   ```
3. Start the production environment:
   ```
   docker-compose -f docker-compose.prod.yml up -d
   ```

## API Documentation

The API provides endpoints for managing:

- Authentication (login, register, refresh token)
- Tenants
- Users and roles
- Brands
- Surveys and questions
- Visits and answers
- Photos and shelf quadrants
- Goals and assignments
- Call cycles
- Teams

For detailed API documentation, see the [API Documentation](docs/api.md).

## Testing

Run the tests with:

```
docker-compose exec api pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Specification

### High-level architecture & libs

- Flask (application)
- Flask-JWT-Extended (JWT access + refresh tokens)
- SQLAlchemy (ORM)
- Alembic / Flask-Migrate (migrations)
- Marshmallow (request/response schemas & validation)
- psycopg2 (Postgres driver)
- pytest + pytest-flask (unit tests)
- passlib / bcrypt (password hashing)
- Celery (optional) for async tasks (image processing, analytics)
- S3-compatible storage (or local storage) for images
- Logging + audit trail

### Multi-tenancy approach

- Row-level tenant separation: EVERY business-data table includes tenant_id (UUID).
- Tenant enforced by middleware that:
  - Extracts tenant_id from JWT claims (users belong to a tenant), or
  - For cross-tenant admins, allow X-Tenant-ID header (only for admin role).
- Database-level FK constraints include tenant_id when appropriate.
- All queries must filter by tenant_id unless table is global (e.g., tenants, system_audit).

### Auth / RBAC

- JWT contains: user_id, tenant_id, roles (list), exp, iat.
- Roles: agent, team_leader, area_manager, regional_manager, national_manager, admin, super_admin.
- Role checks enforced in controllers (decorators).
- Passwords hashed with bcrypt (passlib).

### Folder structure

```
sales_sync_backend/
├─ app.py
├─ config.py
├─ manage.py
├─ requirements.txt
├─ alembic/
├─ migrations/
├─ tests/
│  ├─ conftest.py
│  ├─ test_auth.py
│  ├─ test_visits.py
│  └─ ...
├─ models/
│  ├─ __init__.py
│  ├─ base.py
│  ├─ tenant.py
│  ├─ user.py
│  ├─ role.py
│  ├─ brand.py
│  ├─ survey.py
│  ├─ question.py
│  ├─ visit.py
│  ├─ shelf_quadrant.py
│  ├─ photo.py
│  ├─ goal.py
│  ├─ call_cycle.py
│  └─ audit.py
├─ routes/
│  ├─ __init__.py
│  ├─ auth_routes.py
│  ├─ users_routes.py
│  ├─ tenants_routes.py
│  ├─ brands_routes.py
│  ├─ surveys_routes.py
│  ├─ visits_routes.py
│  ├─ goals_routes.py
│  ├─ call_cycles_routes.py
│  ├─ analytics_routes.py
│  └─ admin_routes.py
├─ controllers/
│  ├─ auth_controller.py
│  ├─ users_controller.py
│  ├─ brands_controller.py
│  ├─ surveys_controller.py
│  ├─ visits_controller.py
│  ├─ goals_controller.py
│  ├─ call_cycles_controller.py
│  ├─ analytics_controller.py
│  └─ admin_controller.py
├─ services/
│  ├─ auth_service.py
│  ├─ user_service.py
│  ├─ brand_service.py
│  ├─ survey_service.py
│  ├─ visit_service.py
│  ├─ photo_service.py
│  ├─ goal_service.py
│  ├─ call_cycle_service.py
│  ├─ analytics_service.py
│  └─ tenant_service.py
└─ utils/
   ├─ auth_decorators.py
   ├─ validators.py
   ├─ image_utils.py
   └─ db_utils.py
```

### Flow convention

- Route receives HTTP request, validates & parses input, and passes to Controller.
- Controller handles auth/context/tenant checks, calls Service for business logic.
- Service manages DB interaction via SQLAlchemy models and returns result.
- Controllers format the service result into a response schema.

### Database tables

Global tables (no tenant_id):
- tenants (tenant registry)
- system_audit (audits/logs - optionally tenant-aware but can be global)

Tenant-scoped tables (all include tenant_id):
- users
- roles (role definitions)
- user_roles (association)
- brands
- brand_infographics (media metadata)
- surveys (survey templates)
- survey_questions
- questions_options (if needed)
- visits (individual/shop visits)
- visit_answers (answers to survey questions)
- photos (photo metadata for visits)
- shelf_quadrants (marked quadrants per photo)
- goals (goal definitions)
- goals_assignments (goal -> user/team)
- call_cycles (cycle definitions)
- call_cycle_locations (locations in a cycle)
- teams (team entities)
- user_teams (association)
- audit_logs (tenant audit logs)
- shop (shop registry; optional cached shop data)

### Routes

Each entry: METHOD PATH — brief description — required roles

#### Auth
- POST /api/auth/register — Register tenant + first admin or user (super_admin or tenant admin creation flow). — public or super_admin
- POST /api/auth/login — Login, returns access & refresh JWT. — public
- POST /api/auth/refresh — Exchange refresh token for new access token. — authenticated
- POST /api/auth/logout — Invalidate refresh token (optional store). — authenticated
- POST /api/auth/forgot-password — Start reset flow (email). — public
- POST /api/auth/reset-password — Reset password. — public

#### Tenants & Admin
- GET /api/tenants — List tenants (super_admin). — super_admin
- POST /api/tenants — Create tenant (super_admin). — super_admin
- GET /api/tenants/:id — Get tenant info. — super_admin / tenant admin
- PUT /api/tenants/:id — Update tenant. — super_admin / tenant admin

#### Users & Roles
- POST /api/users — Create user (admin can create within tenant). — admin, super_admin
- GET /api/users — List users (tenant-scoped). — admin, managers (scoped)
- GET /api/users/:id — Get user profile. — owner/admin
- PUT /api/users/:id — Update user. — owner/admin
- DELETE /api/users/:id — Disable user. — admin
- GET /api/roles — List roles. — admin
- POST /api/users/:id/roles — Assign roles to user. — admin

#### Teams
- POST /api/teams — Create team. — admin, area_manager
- GET /api/teams — List teams. — admin/managers
- PUT /api/teams/:id — Update team. — admin/area_manager
- POST /api/teams/:id/members — Add user to team. — team_leader/admin

#### Brands & Infographics
- POST /api/brands — Create brand. — admin
- GET /api/brands — List brands (tenant). — all roles
- GET /api/brands/:id — Get brand. — all roles
- PUT /api/brands/:id — Update brand. — admin
- DELETE /api/brands/:id — Delete brand. — admin
- POST /api/brands/:id/infographics — Upload infographic (image meta). — admin
- GET /api/brands/:id/infographics — List infographics. — all roles

#### Surveys & Questions
- POST /api/surveys — Create survey template (admin). — admin
- GET /api/surveys — List surveys. — all roles
- GET /api/surveys/:id — Get survey. — all roles
- PUT /api/surveys/:id — Update survey. — admin
- DELETE /api/surveys/:id — Delete survey. — admin
- POST /api/surveys/:id/questions — Add question. — admin
- PUT /api/questions/:id — Update question. — admin
- DELETE /api/questions/:id — Delete question. — admin

#### Visits (core agent flows)
- POST /api/visits — Create a new visit (start). Payload includes survey_id, visit_type, geocode, optional shop_id. — agent
- PUT /api/visits/:id/complete — Mark visit complete; includes answers & photos payload. — agent
- GET /api/visits — List visits (tenant-scoped, filtered by role scope). — all roles (scoped)
- GET /api/visits/:id — Get visit details (answers + photos). — scoped
- GET /api/visits/:id/photos — Get photos for visit. — scoped

#### Photos & Shelf Share
- POST /api/photos — Upload photo (visit_id, purpose). Returns file_url. — agent
- POST /api/photos/:id/shelf_quadrants — Submit quadrant-of-brand selections for a shelf photo. Service calculates area_percentage and stores in shelf_quadrants. — agent
- GET /api/photos/:id — Get photo meta. — scoped

#### Goals
- POST /api/goals — Create goal (admin/manager). — manager/admin
- GET /api/goals — List goals (tenant). — all roles
- POST /api/goals/:id/assign — Assign to user/team. — manager/admin
- GET /api/goals/:id/progress — Get progress metrics. — scoped

#### Call Cycles
- POST /api/call_cycles — Create call cycle (manager). — manager
- GET /api/call_cycles — List call cycles. — scoped
- PUT /api/call_cycles/:id — Update. — manager
- POST /api/call_cycles/:id/locations — Add locations to cycle. — manager
- GET /api/call_cycles/:id/status — Get adherence status and upcoming schedule. — manager

#### Analytics
- GET /api/analytics/overview — Role-scoped KPIs (visits, conversions, shelf share). — scoped
- GET /api/analytics/visits — Time-series visits. — scoped
- GET /api/analytics/shelf_share — Shelf-share aggregation by brand. — scoped
- GET /api/analytics/call_cycle_coverage — Heatmap data. — manager/national

#### Admin / Audit
- GET /api/admin/users/activity — Platform usage (admin). — admin
- GET /api/admin/surveys/completion — Survey completion rates. — admin
- GET /api/audit — Audit logs for tenant (or global for super_admin). — admin/super_admin