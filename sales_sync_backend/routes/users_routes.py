from flask import Blueprint

from controllers.users_controller import (
    create_user_handler,
    get_users_handler,
    get_user_handler,
    update_user_handler,
    update_user_roles_handler,
    delete_user_handler
)

# Create blueprint
users_bp = Blueprint('users', __name__, url_prefix='/api/users')

# Register routes
users_bp.route('', methods=['POST'])(create_user_handler)
users_bp.route('', methods=['GET'])(get_users_handler)
users_bp.route('/<uuid:user_id>', methods=['GET'])(get_user_handler)
users_bp.route('/<uuid:user_id>', methods=['PUT'])(update_user_handler)
users_bp.route('/<uuid:user_id>/roles', methods=['POST'])(update_user_roles_handler)
users_bp.route('/<uuid:user_id>', methods=['DELETE'])(delete_user_handler)