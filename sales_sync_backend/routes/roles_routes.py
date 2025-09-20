from flask import Blueprint

from controllers.roles_controller import get_roles_handler

# Create blueprint
roles_bp = Blueprint('roles', __name__, url_prefix='/api/roles')

# Register routes
roles_bp.route('', methods=['GET'])(get_roles_handler)