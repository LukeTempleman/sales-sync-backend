from flask import jsonify, request, g, current_app
from marshmallow import ValidationError

from services.user_service import (
    get_users,
    get_user_by_id,
    create_user,
    update_user,
    update_user_password,
    update_user_roles,
    delete_user
)
from utils.validators import (
    UserCreateSchema,
    UserUpdateSchema
)
from utils.auth_decorators import admin_required, tenant_required


@tenant_required
@admin_required
def create_user_handler():
    """
    Create a new user.
    
    Returns:
        JSON response with created user
    """
    try:
        # Validate request data
        schema = UserCreateSchema()
        data = schema.load(request.json)
        
        # Create user
        user = create_user(
            current_app.db_session,
            g.tenant_id,
            data['email'],
            data['password'],
            data['first_name'],
            data['last_name'],
            data.get('phone'),
            data.get('roles', ['agent'])  # Default role is agent
        )
        
        # Return response
        return jsonify({
            'message': 'User created successfully',
            'user': user.to_dict()
        }), 201
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except Exception as e:
        current_app.logger.error(f"User creation error: {str(e)}")
        return jsonify({'error': 'User creation failed'}), 500


@tenant_required
def get_users_handler():
    """
    Get users for a tenant.
    
    Returns:
        JSON response with users
    """
    try:
        # Get filters from query params
        filters = {}
        if request.args.get('email'):
            filters['email'] = request.args.get('email')
        if request.args.get('is_active'):
            filters['is_active'] = request.args.get('is_active').lower() == 'true'
        
        # Get users
        users = get_users(current_app.db_session, g.tenant_id, filters)
        
        # Return response
        return jsonify({
            'users': [user.to_dict() for user in users]
        }), 200
    except Exception as e:
        current_app.logger.error(f"Get users error: {str(e)}")
        return jsonify({'error': 'Failed to get users'}), 500


@tenant_required
def get_user_handler(user_id):
    """
    Get user by ID.
    
    Args:
        user_id: User ID
    
    Returns:
        JSON response with user
    """
    try:
        # Get user
        user = get_user_by_id(current_app.db_session, g.tenant_id, user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Return response
        return jsonify({
            'user': user.to_dict()
        }), 200
    except Exception as e:
        current_app.logger.error(f"Get user error: {str(e)}")
        return jsonify({'error': 'Failed to get user'}), 500


@tenant_required
@admin_required
def update_user_handler(user_id):
    """
    Update a user.
    
    Args:
        user_id: User ID
    
    Returns:
        JSON response with updated user
    """
    try:
        # Validate request data
        schema = UserUpdateSchema()
        data = schema.load(request.json)
        
        # Update user
        user = update_user(current_app.db_session, g.tenant_id, user_id, data)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Return response
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        }), 200
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except Exception as e:
        current_app.logger.error(f"User update error: {str(e)}")
        return jsonify({'error': 'User update failed'}), 500


@tenant_required
@admin_required
def update_user_roles_handler(user_id):
    """
    Update a user's roles.
    
    Args:
        user_id: User ID
    
    Returns:
        JSON response with updated user
    """
    try:
        # Validate request data
        if not request.json or 'roles' not in request.json:
            return jsonify({'error': 'Roles are required'}), 400
        
        roles = request.json['roles']
        if not isinstance(roles, list):
            return jsonify({'error': 'Roles must be a list'}), 400
        
        # Update user roles
        user = update_user_roles(current_app.db_session, g.tenant_id, user_id, roles)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Return response
        return jsonify({
            'message': 'User roles updated successfully',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        current_app.logger.error(f"User roles update error: {str(e)}")
        return jsonify({'error': 'User roles update failed'}), 500


@tenant_required
@admin_required
def delete_user_handler(user_id):
    """
    Delete a user (soft delete).
    
    Args:
        user_id: User ID
    
    Returns:
        JSON response with success message
    """
    try:
        # Delete user
        success = delete_user(current_app.db_session, g.tenant_id, user_id)
        
        if not success:
            return jsonify({'error': 'User not found'}), 404
        
        # Return response
        return jsonify({
            'message': 'User deleted successfully'
        }), 200
    except Exception as e:
        current_app.logger.error(f"User deletion error: {str(e)}")
        return jsonify({'error': 'User deletion failed'}), 500