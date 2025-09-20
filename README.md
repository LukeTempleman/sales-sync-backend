# Sales-Sync Backend

A Flask-based backend for the Sales-Sync application with multi-tenancy, JWT authentication, and various business models for tracking sales activities.

## Features

- Multi-tenant architecture with row-level tenant separation
- JWT-based authentication with refresh tokens
- Role-based access control (agent, team_leader, area_manager, regional_manager, national_manager, admin, super_admin)
- Cross-tenant administration for super_admin users
- RESTful API for managing sales activities
- User and team management
- Survey creation and management with customizable questions
- Visit tracking and completion with geocoding
- Shop registry for visit locations
- Photo capture and management
- Shelf share analysis with quadrant marking
- Brand and infographics management
- Goals and targets tracking with progress monitoring
- Call cycles planning and adherence tracking
- Advanced analytics and reporting (visits, shelf share, call cycle coverage)
- Comprehensive audit logging
- Input validation and serialization with Marshmallow
- Secure password handling with bcrypt
- Password reset flow
- Database migrations with Alembic
- Optional asynchronous processing with Celery

## Tech Stack

- **Framework**: Flask
- **Authentication**: Flask-JWT-Extended
- **ORM**: SQLAlchemy
- **Migrations**: Alembic / Flask-Migrate
- **Validation**: Marshmallow
- **Database**: PostgreSQL with psycopg2
- **Testing**: pytest + pytest-flask
- **Password Hashing**: passlib / bcrypt
- **Async Tasks**: Celery (optional)
- **Storage**: S3-compatible or local storage

## Project Structure

```
/workspace/
├─ requirements.txt            # Project dependencies
├─ docker-compose.yml          # Development Docker configuration
├─ docker-compose.prod.yml     # Production Docker configuration
├─ scripts/                    # Helper scripts
│  ├─ run.sh
│  ├─ run_prod.sh
│  ├─ init_db.sh
│  ├─ seed_db.sh
│  ├─ create_superadmin.sh
│  ├─ create_tenant_admin.sh
│  ├─ run_tests.sh
│  ├─ run_tests_with_coverage.sh
│  ├─ run_migrations.sh
│  └─ generate_api_docs.sh
├─ sales_sync_backend/         # Main application code
│  ├─ app.py                   # Application factory
│  ├─ config.py                # Configuration settings
│  ├─ manage.py                # Management commands
│  ├─ migrations/              # Database migrations
│  ├─ tests/                   # Test suite
│  │  ├─ conftest.py           # Test fixtures
│  │  ├─ test_auth.py          # Authentication tests
│  │  ├─ test_users.py         # Users API tests
│  │  ├─ test_tenants.py       # Tenants API tests
│  │  ├─ test_brands.py        # Brands API tests
│  │  ├─ test_surveys.py       # Surveys API tests
│  │  ├─ test_visits.py        # Visits API tests
│  │  ├─ test_photos.py        # Photos API tests
│  │  ├─ test_teams.py         # Teams API tests
│  │  ├─ test_goals.py         # Goals API tests
│  │  ├─ test_call_cycles.py   # Call Cycles API tests
│  │  ├─ test_analytics.py     # Analytics API tests
│  │  └─ test_admin.py         # Admin API tests
│  ├─ models/                  # Database models
│  │  ├─ __init__.py
│  │  ├─ base.py               # Base model with common fields
│  │  ├─ tenant.py             # Tenant model
│  │  ├─ user.py               # User model
│  │  ├─ role.py               # Role model
│  │  ├─ brand.py              # Brand model
│  │  ├─ survey.py             # Survey model
│  │  ├─ question.py           # Question model
│  │  ├─ visit.py              # Visit model
│  │  ├─ shelf_quadrant.py     # Shelf quadrant model
│  │  ├─ photo.py              # Photo model
│  │  ├─ goal.py               # Goal model
│  │  ├─ call_cycle.py         # Call cycle model
│  │  └─ audit.py              # Audit log model
│  ├─ routes/                  # API routes
│  │  ├─ __init__.py
│  │  ├─ auth_routes.py        # Authentication routes
│  │  ├─ users_routes.py       # Users routes
│  │  ├─ tenants_routes.py     # Tenants routes
│  │  ├─ brands_routes.py      # Brands routes
│  │  ├─ surveys_routes.py     # Surveys routes
│  │  ├─ visits_routes.py      # Visits routes
│  │  ├─ goals_routes.py       # Goals routes
│  │  ├─ call_cycles_routes.py # Call cycles routes
│  │  ├─ analytics_routes.py   # Analytics routes
│  │  └─ admin_routes.py       # Admin routes
│  ├─ controllers/             # Request handlers
│  │  ├─ auth_controller.py    # Authentication controller
│  │  ├─ users_controller.py   # Users controller
│  │  ├─ brands_controller.py  # Brands controller
│  │  ├─ surveys_controller.py # Surveys controller
│  │  ├─ visits_controller.py  # Visits controller
│  │  ├─ goals_controller.py   # Goals controller
│  │  ├─ call_cycles_controller.py # Call cycles controller
│  │  ├─ analytics_controller.py # Analytics controller
│  │  └─ admin_controller.py   # Admin controller
│  ├─ services/                # Business logic
│  │  ├─ auth_service.py       # Authentication service
│  │  ├─ user_service.py       # User service
│  │  ├─ brand_service.py      # Brand service
│  │  ├─ survey_service.py     # Survey service
│  │  ├─ visit_service.py      # Visit service
│  │  ├─ photo_service.py      # Photo service
│  │  ├─ goal_service.py       # Goal service
│  │  ├─ call_cycle_service.py # Call cycle service
│  │  ├─ analytics_service.py  # Analytics service
│  │  └─ tenant_service.py     # Tenant service
│  └─ utils/                   # Utility functions
│     ├─ auth_decorators.py    # Authentication decorators
│     ├─ validators.py         # Input validators
│     ├─ image_utils.py        # Image processing utilities
│     └─ db_utils.py           # Database utilities
└─ nginx/                      # Nginx configuration for production
   ├─ conf.d/                  # Nginx site configuration
   └─ ssl/                     # SSL certificates
```

## Getting Started

### Prerequisites

- Docker and Docker Compose

### Development Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd sales-sync-backend
   ```

2. Start the development environment:
   ```bash
   docker-compose up -d
   ```

3. Initialize the database:
   ```bash
   docker-compose exec api ./scripts/init_db.sh
   ```

4. Create a superadmin user:
   ```bash
   docker-compose exec api ./scripts/create_superadmin.sh
   ```

5. Create a tenant and admin user:
   ```bash
   docker-compose exec api ./scripts/create_tenant_admin.sh
   ```

6. Access the API at http://localhost:5000/api

### Running Locally (without Docker)

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables:
   ```bash
   export FLASK_APP=sales_sync_backend/app.py
   export FLASK_ENV=development
   export FLASK_DEBUG=1
   export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/sales_sync
   ```

3. Initialize the database:
   ```bash
   ./scripts/init_db.sh
   ```

4. Create a superadmin user:
   ```bash
   ./scripts/create_superadmin.sh
   ```

5. Create a tenant and admin user:
   ```bash
   ./scripts/create_tenant_admin.sh
   ```

6. Run the application:
   ```bash
   ./scripts/run.sh
   ```

7. Access the API at http://localhost:5000/api

### Running with SQLite (for testing)

1. Initialize the SQLite database:
   ```bash
   ./scripts/init_sqlite_db.sh
   ```

2. Create a superadmin user:
   ```bash
   DATABASE_URL=sqlite:///sales_sync.db ./scripts/create_superadmin.sh
   ```

3. Create a tenant and admin user:
   ```bash
   DATABASE_URL=sqlite:///sales_sync.db ./scripts/create_tenant_admin.sh
   ```

4. Run the application with SQLite:
   ```bash
   ./scripts/run_with_sqlite.sh
   ```

5. Access the API at http://localhost:5000/api

### Production Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your production settings.

3. Generate SSL certificates (or place your own certificates in nginx/ssl/):
   ```bash
   ./scripts/generate_ssl_certs.sh
   ```

4. Start the production environment:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

5. Initialize the database:
   ```bash
   docker-compose -f docker-compose.prod.yml exec api ./scripts/run_migrations.sh
   ```

6. Create a superadmin user:
   ```bash
   docker-compose -f docker-compose.prod.yml exec api ./scripts/create_superadmin.sh
   ```

## API Documentation

### Authentication

- `POST /api/auth/register` - Register tenant + first admin
- `POST /api/auth/login` - Login, returns access & refresh JWT
- `POST /api/auth/refresh` - Exchange refresh token for new access token
- `POST /api/auth/logout` - Invalidate refresh token
- `POST /api/auth/forgot-password` - Start reset flow
- `POST /api/auth/reset-password` - Reset password

### Tenants & Admin

- `GET /api/tenants` - List tenants (super_admin)
- `POST /api/tenants` - Create tenant (super_admin)
- `GET /api/tenants/:id` - Get tenant info
- `PUT /api/tenants/:id` - Update tenant

### Users & Roles

- `POST /api/users` - Create user
- `GET /api/users` - List users
- `GET /api/users/:id` - Get user profile
- `PUT /api/users/:id` - Update user
- `DELETE /api/users/:id` - Disable user
- `GET /api/roles` - List roles
- `POST /api/users/:id/roles` - Assign roles to user

### Teams

- `POST /api/teams` - Create team
- `GET /api/teams` - List teams
- `PUT /api/teams/:id` - Update team
- `POST /api/teams/:id/members` - Add user to team

### Brands & Infographics

- `POST /api/brands` - Create brand
- `GET /api/brands` - List brands
- `GET /api/brands/:id` - Get brand
- `PUT /api/brands/:id` - Update brand
- `DELETE /api/brands/:id` - Delete brand
- `POST /api/brands/:id/infographics` - Upload infographic
- `GET /api/brands/:id/infographics` - List infographics

### Surveys & Questions

- `POST /api/surveys` - Create survey template
- `GET /api/surveys` - List surveys
- `GET /api/surveys/:id` - Get survey
- `PUT /api/surveys/:id` - Update survey
- `DELETE /api/surveys/:id` - Delete survey
- `POST /api/surveys/:id/questions` - Add question
- `PUT /api/questions/:id` - Update question
- `DELETE /api/questions/:id` - Delete question

### Visits

- `POST /api/visits` - Create a new visit
- `PUT /api/visits/:id/complete` - Mark visit complete
- `GET /api/visits` - List visits
- `GET /api/visits/:id` - Get visit details
- `GET /api/visits/:id/photos` - Get photos for visit

### Photos & Shelf Share

- `POST /api/photos` - Upload photo
- `POST /api/photos/:id/shelf_quadrants` - Submit quadrant-of-brand selections
- `GET /api/photos/:id` - Get photo meta

### Goals

- `POST /api/goals` - Create goal
- `GET /api/goals` - List goals
- `POST /api/goals/:id/assign` - Assign to user/team
- `GET /api/goals/:id/progress` - Get progress metrics

### Call Cycles

- `POST /api/call_cycles` - Create call cycle
- `GET /api/call_cycles` - List call cycles
- `PUT /api/call_cycles/:id` - Update
- `POST /api/call_cycles/:id/locations` - Add locations to cycle
- `GET /api/call_cycles/:id/status` - Get adherence status

### Analytics

- `GET /api/analytics/overview` - Role-scoped KPIs
- `GET /api/analytics/visits` - Time-series visits
- `GET /api/analytics/shelf_share` - Shelf-share aggregation by brand
- `GET /api/analytics/call_cycle_coverage` - Heatmap data

### Admin / Audit

- `GET /api/admin/users/activity` - Platform usage
- `GET /api/admin/surveys/completion` - Survey completion rates
- `GET /api/audit` - Audit logs for tenant

## Scripts

All scripts are located in the `scripts` directory:

- `run.sh`: Run the application in development mode
- `run_with_docs.sh`: Run the application in development mode with API documentation
- `run_with_sqlite.sh`: Run the application with SQLite database (for testing)
- `run_with_port.sh`: Run the application on a specific port (e.g., `./scripts/run_with_port.sh 8000`)
- `run_prod.sh`: Run the application in production mode with Gunicorn
- `init_db.sh`: Initialize the PostgreSQL database with tables and seed data
- `init_sqlite_db.sh`: Initialize the SQLite database with tables and seed data
- `seed_db.sh`: Seed the database with initial data
- `create_superadmin.sh`: Create a superadmin user
- `create_tenant_admin.sh`: Create a tenant and admin user
- `run_tests.sh`: Run the test suite with PostgreSQL
- `run_tests_with_sqlite.sh`: Run the test suite with SQLite
- `run_tests_with_coverage.sh`: Run the test suite with coverage report (PostgreSQL)
- `run_tests_with_coverage_sqlite.sh`: Run the test suite with coverage report (SQLite)
- `run_migrations.sh`: Run database migrations
- `generate_api_docs.sh`: Generate API documentation
- `generate_ssl_certs.sh`: Generate self-signed SSL certificates for development

## License

[MIT](LICENSE)