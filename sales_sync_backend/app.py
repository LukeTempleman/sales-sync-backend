import os
import logging
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from config import config
from utils.api_docs import setup_swagger, init_api_docs

# Initialize extensions
jwt = JWTManager()

def create_app(config_name=None):
    """Application factory pattern."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    jwt.init_app(app)
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, app.config['LOG_LEVEL']),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create database engine and session
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    app.db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    
    # Create tables for SQLite (only in testing mode)
    if config_name == 'testing' and app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite'):
        from models import Base
        Base.metadata.create_all(engine)
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found"}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({"error": "Internal server error"}), 500
    
    # Register blueprints
    from routes import register_routes
    register_routes(app)
    
    # Set up Swagger UI
    setup_swagger(app)
    init_api_docs()
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "ok", "version": "1.0.0"}), 200
    
    # Tenant middleware
    @app.before_request
    def before_request():
        from utils.tenant_middleware import set_tenant_from_jwt
        set_tenant_from_jwt()
    
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        app.db_session.remove()
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)