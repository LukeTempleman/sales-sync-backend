from flask import Flask

from routes.auth_routes import auth_bp
from routes.users_routes import users_bp
from routes.tenants_routes import tenants_bp
from routes.brands_routes import brands_bp
from routes.surveys_routes import surveys_bp, questions_bp
from routes.visits_routes import visits_bp
from routes.photos_routes import photos_bp
from routes.teams_routes import teams_bp
from routes.roles_routes import roles_bp
from routes.goals_routes import goals_bp
from routes.call_cycles_routes import call_cycles_bp
from routes.analytics_routes import analytics_bp
from routes.admin_routes import admin_bp, audit_bp
# Import other route blueprints here as they are implemented


def register_routes(app: Flask):
    """
    Register all route blueprints with the Flask app.
    
    Args:
        app: Flask application instance
    """
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(tenants_bp)
    app.register_blueprint(brands_bp)
    app.register_blueprint(surveys_bp)
    app.register_blueprint(questions_bp)
    app.register_blueprint(visits_bp)
    app.register_blueprint(photos_bp)
    app.register_blueprint(teams_bp)
    app.register_blueprint(roles_bp)
    app.register_blueprint(goals_bp)
    app.register_blueprint(call_cycles_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(audit_bp)
    # Register other blueprints here as they are implemented