"""
API documentation utilities using apispec and OpenAPI.
"""
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask import Flask, jsonify, current_app
from flask_swagger_ui import get_swaggerui_blueprint

def create_spec():
    """Create a new APISpec instance."""
    spec = APISpec(
        title="Sales-Sync API",
        version="1.0.0",
        openapi_version="3.0.2",
        plugins=[MarshmallowPlugin()],
        info={
            "description": "API for Sales-Sync application",
            "contact": {"email": "support@sales-sync.com"},
            "license": {"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
        },
        servers=[
            {"url": "/api", "description": "Development server"},
            {"url": "https://api.sales-sync.com/api", "description": "Production server"},
        ],
        tags=[
            {"name": "auth", "description": "Authentication operations"},
            {"name": "tenants", "description": "Tenant management"},
            {"name": "users", "description": "User management"},
            {"name": "roles", "description": "Role management"},
            {"name": "teams", "description": "Team management"},
            {"name": "brands", "description": "Brand management"},
            {"name": "surveys", "description": "Survey management"},
            {"name": "visits", "description": "Visit tracking"},
            {"name": "photos", "description": "Photo management"},
            {"name": "goals", "description": "Goal management"},
            {"name": "call_cycles", "description": "Call cycle management"},
            {"name": "analytics", "description": "Analytics and reporting"},
            {"name": "admin", "description": "Admin operations"},
        ],
    )
    
    # Security schemes
    spec.components.security_scheme(
        "bearerAuth", {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    )
    
    return spec


def setup_swagger(app: Flask, base_url: str = "/api/docs"):
    """
    Set up Swagger UI for the Flask application.
    
    Args:
        app: Flask application
        base_url: Base URL for Swagger UI
    """
    # Create Swagger UI blueprint
    swagger_ui_blueprint = get_swaggerui_blueprint(
        base_url,
        f"{base_url}/swagger.json",
        config={"app_name": "Sales-Sync API"},
    )
    
    # Register blueprint
    app.register_blueprint(swagger_ui_blueprint, url_prefix=base_url)
    
    # Add route for Swagger JSON
    @app.route(f"{base_url}/swagger.json")
    def swagger_json():
        # Create a new spec instance for each request
        spec = create_spec()
        # Register schemas and routes
        register_schemas(spec)
        register_all_routes(spec)
        return jsonify(spec.to_dict())


def register_schemas(spec):
    """Register all Marshmallow schemas with APISpec."""
    from utils.validators import (
        TenantSchema, UserSchema, RoleSchema,
        BrandSchema, BrandInfographicSchema,
        SurveySchema, SurveyQuestionSchema,
        VisitSchema, VisitAnswerSchema,
        PhotoSchema, ShelfQuadrantSchema,
        GoalSchema, GoalAssignmentSchema,
        CallCycleSchema, CallCycleLocationSchema,
        TeamSchema, UserTeamSchema,
        AuditLogSchema
    )
    
    # Register schemas
    spec.components.schema("Tenant", schema=TenantSchema)
    spec.components.schema("User", schema=UserSchema)
    spec.components.schema("Role", schema=RoleSchema)
    spec.components.schema("Brand", schema=BrandSchema)
    spec.components.schema("BrandInfographic", schema=BrandInfographicSchema)
    spec.components.schema("Survey", schema=SurveySchema)
    spec.components.schema("SurveyQuestion", schema=SurveyQuestionSchema)
    spec.components.schema("Visit", schema=VisitSchema)
    spec.components.schema("VisitAnswer", schema=VisitAnswerSchema)
    spec.components.schema("Photo", schema=PhotoSchema)
    spec.components.schema("ShelfQuadrant", schema=ShelfQuadrantSchema)
    spec.components.schema("Goal", schema=GoalSchema)
    spec.components.schema("GoalAssignment", schema=GoalAssignmentSchema)
    spec.components.schema("CallCycle", schema=CallCycleSchema)
    spec.components.schema("CallCycleLocation", schema=CallCycleLocationSchema)
    spec.components.schema("Team", schema=TeamSchema)
    spec.components.schema("UserTeam", schema=UserTeamSchema)
    spec.components.schema("AuditLog", schema=AuditLogSchema)


def register_auth_routes(spec):
    """Register authentication routes with APISpec."""
    # Register endpoint
    spec.path(
        path="/auth/register",
        operations={
            "post": {
                "tags": ["auth"],
                "summary": "Register a new tenant and admin user",
                "description": "Creates a new tenant and admin user",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "email": {"type": "string", "format": "email"},
                                    "password": {"type": "string", "format": "password"},
                                    "first_name": {"type": "string"},
                                    "last_name": {"type": "string"},
                                    "tenant_name": {"type": "string"},
                                    "subdomain": {"type": "string"},
                                },
                                "required": ["email", "password", "tenant_name"],
                            }
                        }
                    },
                },
                "responses": {
                    "201": {
                        "description": "Tenant and admin user created successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "tokens": {
                                            "type": "object",
                                            "properties": {
                                                "access_token": {"type": "string"},
                                                "refresh_token": {"type": "string"},
                                            },
                                        },
                                        "tenant": {"$ref": "#/components/schemas/Tenant"},
                                        "user": {"$ref": "#/components/schemas/User"},
                                    },
                                }
                            }
                        },
                    },
                    "400": {
                        "description": "Invalid input",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                },
            }
        },
    )
    
    # Login endpoint
    spec.path(
        path="/auth/login",
        operations={
            "post": {
                "tags": ["auth"],
                "summary": "Login with email and password",
                "description": "Authenticates a user and returns JWT tokens",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "email": {"type": "string", "format": "email"},
                                    "password": {"type": "string", "format": "password"},
                                },
                                "required": ["email", "password"],
                            }
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "Login successful",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "tokens": {
                                            "type": "object",
                                            "properties": {
                                                "access_token": {"type": "string"},
                                                "refresh_token": {"type": "string"},
                                            },
                                        },
                                        "user": {"$ref": "#/components/schemas/User"},
                                    },
                                }
                            }
                        },
                    },
                    "401": {
                        "description": "Invalid credentials",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                },
            }
        },
    )
    
    # Refresh token endpoint
    spec.path(
        path="/auth/refresh",
        operations={
            "post": {
                "tags": ["auth"],
                "summary": "Refresh access token",
                "description": "Exchanges a refresh token for a new access token",
                "security": [{"bearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "Token refreshed successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "access_token": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "401": {
                        "description": "Invalid or expired refresh token",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                },
            }
        },
    )
    
    # Logout endpoint
    spec.path(
        path="/auth/logout",
        operations={
            "post": {
                "tags": ["auth"],
                "summary": "Logout",
                "description": "Invalidates the refresh token",
                "security": [{"bearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "Logout successful",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "message": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "401": {
                        "description": "Unauthorized",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                },
            }
        },
    )
    
    # Forgot password endpoint
    spec.path(
        path="/auth/forgot-password",
        operations={
            "post": {
                "tags": ["auth"],
                "summary": "Forgot password",
                "description": "Initiates the password reset flow",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "email": {"type": "string", "format": "email"},
                                },
                                "required": ["email"],
                            }
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "Password reset email sent",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "message": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "400": {
                        "description": "Invalid email",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                },
            }
        },
    )
    
    # Reset password endpoint
    spec.path(
        path="/auth/reset-password",
        operations={
            "post": {
                "tags": ["auth"],
                "summary": "Reset password",
                "description": "Resets the password using a reset token",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "token": {"type": "string"},
                                    "password": {"type": "string", "format": "password"},
                                },
                                "required": ["token", "password"],
                            }
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "Password reset successful",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "message": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "400": {
                        "description": "Invalid token or password",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                },
            }
        },
    )


def register_tenant_routes(spec):
    """Register tenant routes with APISpec."""
    # List tenants endpoint
    spec.path(
        path="/tenants",
        operations={
            "get": {
                "tags": ["tenants"],
                "summary": "List tenants",
                "description": "Returns a list of all tenants (super_admin only)",
                "security": [{"bearerAuth": []}],
                "parameters": [
                    {
                        "name": "page",
                        "in": "query",
                        "description": "Page number",
                        "schema": {"type": "integer", "default": 1},
                    },
                    {
                        "name": "per_page",
                        "in": "query",
                        "description": "Items per page",
                        "schema": {"type": "integer", "default": 20},
                    },
                ],
                "responses": {
                    "200": {
                        "description": "List of tenants",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "tenants": {
                                            "type": "array",
                                            "items": {"$ref": "#/components/schemas/Tenant"},
                                        },
                                        "pagination": {
                                            "type": "object",
                                            "properties": {
                                                "total": {"type": "integer"},
                                                "pages": {"type": "integer"},
                                                "page": {"type": "integer"},
                                                "per_page": {"type": "integer"},
                                            },
                                        },
                                    },
                                }
                            }
                        },
                    },
                    "401": {
                        "description": "Unauthorized",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "403": {
                        "description": "Forbidden - Not a super_admin",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                },
            }
        },
    )
    
    # Create tenant endpoint
    spec.path(
        path="/tenants",
        operations={
            "post": {
                "tags": ["tenants"],
                "summary": "Create tenant",
                "description": "Creates a new tenant (super_admin only)",
                "security": [{"bearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "subdomain": {"type": "string"},
                                },
                                "required": ["name"],
                            }
                        }
                    },
                },
                "responses": {
                    "201": {
                        "description": "Tenant created successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "tenant": {"$ref": "#/components/schemas/Tenant"},
                                    },
                                }
                            }
                        },
                    },
                    "400": {
                        "description": "Invalid input",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "401": {
                        "description": "Unauthorized",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "403": {
                        "description": "Forbidden - Not a super_admin",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                },
            }
        },
    )
    
    # Get tenant endpoint
    spec.path(
        path="/tenants/{id}",
        operations={
            "get": {
                "tags": ["tenants"],
                "summary": "Get tenant",
                "description": "Returns a tenant by ID (super_admin or tenant admin)",
                "security": [{"bearerAuth": []}],
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "description": "Tenant ID",
                        "required": True,
                        "schema": {"type": "string", "format": "uuid"},
                    },
                ],
                "responses": {
                    "200": {
                        "description": "Tenant details",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "tenant": {"$ref": "#/components/schemas/Tenant"},
                                    },
                                }
                            }
                        },
                    },
                    "401": {
                        "description": "Unauthorized",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "403": {
                        "description": "Forbidden - Not authorized to view this tenant",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "404": {
                        "description": "Tenant not found",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                },
            }
        },
    )
    
    # Update tenant endpoint
    spec.path(
        path="/tenants/{id}",
        operations={
            "put": {
                "tags": ["tenants"],
                "summary": "Update tenant",
                "description": "Updates a tenant by ID (super_admin or tenant admin)",
                "security": [{"bearerAuth": []}],
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "description": "Tenant ID",
                        "required": True,
                        "schema": {"type": "string", "format": "uuid"},
                    },
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "subdomain": {"type": "string"},
                                },
                            }
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "Tenant updated successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "tenant": {"$ref": "#/components/schemas/Tenant"},
                                    },
                                }
                            }
                        },
                    },
                    "400": {
                        "description": "Invalid input",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "401": {
                        "description": "Unauthorized",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "403": {
                        "description": "Forbidden - Not authorized to update this tenant",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "404": {
                        "description": "Tenant not found",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                },
            }
        },
    )


def register_user_routes(spec):
    """Register user routes with APISpec."""
    # Create user endpoint
    spec.path(
        path="/users",
        operations={
            "post": {
                "tags": ["users"],
                "summary": "Create user",
                "description": "Creates a new user (admin can create within tenant)",
                "security": [{"bearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "email": {"type": "string", "format": "email"},
                                    "password": {"type": "string", "format": "password"},
                                    "first_name": {"type": "string"},
                                    "last_name": {"type": "string"},
                                    "phone": {"type": "string"},
                                    "roles": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "List of role names",
                                    },
                                },
                                "required": ["email", "password"],
                            }
                        }
                    },
                },
                "responses": {
                    "201": {
                        "description": "User created successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "user": {"$ref": "#/components/schemas/User"},
                                    },
                                }
                            }
                        },
                    },
                    "400": {
                        "description": "Invalid input",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "401": {
                        "description": "Unauthorized",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "403": {
                        "description": "Forbidden - Not authorized to create users",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                },
            }
        },
    )
    
    # List users endpoint
    spec.path(
        path="/users",
        operations={
            "get": {
                "tags": ["users"],
                "summary": "List users",
                "description": "Returns a list of users (tenant-scoped)",
                "security": [{"bearerAuth": []}],
                "parameters": [
                    {
                        "name": "page",
                        "in": "query",
                        "description": "Page number",
                        "schema": {"type": "integer", "default": 1},
                    },
                    {
                        "name": "per_page",
                        "in": "query",
                        "description": "Items per page",
                        "schema": {"type": "integer", "default": 20},
                    },
                    {
                        "name": "role",
                        "in": "query",
                        "description": "Filter by role",
                        "schema": {"type": "string"},
                    },
                    {
                        "name": "search",
                        "in": "query",
                        "description": "Search by name or email",
                        "schema": {"type": "string"},
                    },
                ],
                "responses": {
                    "200": {
                        "description": "List of users",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "users": {
                                            "type": "array",
                                            "items": {"$ref": "#/components/schemas/User"},
                                        },
                                        "pagination": {
                                            "type": "object",
                                            "properties": {
                                                "total": {"type": "integer"},
                                                "pages": {"type": "integer"},
                                                "page": {"type": "integer"},
                                                "per_page": {"type": "integer"},
                                            },
                                        },
                                    },
                                }
                            }
                        },
                    },
                    "401": {
                        "description": "Unauthorized",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "403": {
                        "description": "Forbidden - Not authorized to list users",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                },
            }
        },
    )
    
    # Get user endpoint
    spec.path(
        path="/users/{id}",
        operations={
            "get": {
                "tags": ["users"],
                "summary": "Get user",
                "description": "Returns a user by ID",
                "security": [{"bearerAuth": []}],
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "description": "User ID",
                        "required": True,
                        "schema": {"type": "string", "format": "uuid"},
                    },
                ],
                "responses": {
                    "200": {
                        "description": "User details",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "user": {"$ref": "#/components/schemas/User"},
                                    },
                                }
                            }
                        },
                    },
                    "401": {
                        "description": "Unauthorized",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "403": {
                        "description": "Forbidden - Not authorized to view this user",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "404": {
                        "description": "User not found",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                },
            }
        },
    )
    
    # Update user endpoint
    spec.path(
        path="/users/{id}",
        operations={
            "put": {
                "tags": ["users"],
                "summary": "Update user",
                "description": "Updates a user by ID",
                "security": [{"bearerAuth": []}],
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "description": "User ID",
                        "required": True,
                        "schema": {"type": "string", "format": "uuid"},
                    },
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "email": {"type": "string", "format": "email"},
                                    "first_name": {"type": "string"},
                                    "last_name": {"type": "string"},
                                    "phone": {"type": "string"},
                                    "is_active": {"type": "boolean"},
                                },
                            }
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "User updated successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "user": {"$ref": "#/components/schemas/User"},
                                    },
                                }
                            }
                        },
                    },
                    "400": {
                        "description": "Invalid input",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "401": {
                        "description": "Unauthorized",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "403": {
                        "description": "Forbidden - Not authorized to update this user",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "404": {
                        "description": "User not found",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                },
            }
        },
    )
    
    # Delete user endpoint
    spec.path(
        path="/users/{id}",
        operations={
            "delete": {
                "tags": ["users"],
                "summary": "Disable user",
                "description": "Disables a user by ID (soft delete)",
                "security": [{"bearerAuth": []}],
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "description": "User ID",
                        "required": True,
                        "schema": {"type": "string", "format": "uuid"},
                    },
                ],
                "responses": {
                    "200": {
                        "description": "User disabled successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "message": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "401": {
                        "description": "Unauthorized",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "403": {
                        "description": "Forbidden - Not authorized to disable this user",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "404": {
                        "description": "User not found",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                },
            }
        },
    )
    
    # Assign roles to user endpoint
    spec.path(
        path="/users/{id}/roles",
        operations={
            "post": {
                "tags": ["users"],
                "summary": "Assign roles to user",
                "description": "Assigns roles to a user",
                "security": [{"bearerAuth": []}],
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "description": "User ID",
                        "required": True,
                        "schema": {"type": "string", "format": "uuid"},
                    },
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "roles": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "List of role names",
                                    },
                                },
                                "required": ["roles"],
                            }
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "Roles assigned successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "user": {"$ref": "#/components/schemas/User"},
                                    },
                                }
                            }
                        },
                    },
                    "400": {
                        "description": "Invalid input",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "401": {
                        "description": "Unauthorized",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "403": {
                        "description": "Forbidden - Not authorized to assign roles",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "404": {
                        "description": "User not found",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                },
            }
        },
    )


def register_all_routes(spec):
    """Register all routes with APISpec."""
    register_auth_routes(spec)
    register_tenant_routes(spec)
    register_user_routes(spec)
    # Add more route registrations here
    # register_role_routes(spec)
    # register_team_routes(spec)
    # register_brand_routes(spec)
    # register_survey_routes(spec)
    # register_visit_routes(spec)
    # register_photo_routes(spec)
    # register_goal_routes(spec)
    # register_call_cycle_routes(spec)
    # register_analytics_routes(spec)
    # register_admin_routes()


def init_api_docs():
    """Initialize API documentation."""
    # Create a new spec instance
    spec = create_spec()
    register_schemas(spec)
    register_all_routes(spec)