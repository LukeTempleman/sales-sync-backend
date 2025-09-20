from flask import Blueprint

from controllers.auth_controller import (
    register,
    login,
    refresh,
    logout,
    forgot_password,
    reset_password
)

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Register routes
auth_bp.route('/register', methods=['POST'])(register)
auth_bp.route('/login', methods=['POST'])(login)
auth_bp.route('/refresh', methods=['POST'])(refresh)
auth_bp.route('/logout', methods=['POST'])(logout)
auth_bp.route('/forgot-password', methods=['POST'])(forgot_password)
auth_bp.route('/reset-password', methods=['POST'])(reset_password)