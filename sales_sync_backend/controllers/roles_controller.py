from flask import request, jsonify
from flask_jwt_extended import jwt_required

from models.role import Role
from utils.auth_decorators import admin_required


@jwt_required()
@admin_required
def get_roles_handler():
    """
    Get all roles.
    """
    # Get roles
    roles = request.app.db_session.query(Role).all()
    
    # Return roles
    return jsonify([role.to_dict() for role in roles]), 200