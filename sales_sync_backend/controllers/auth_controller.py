from flask import jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from marshmallow import ValidationError

from services.auth_service import (
    register_tenant_and_admin,
    authenticate_user,
    generate_tokens
)
from utils.validators import (
    RegisterSchema,
    LoginSchema,
    ForgotPasswordSchema,
    ResetPasswordSchema
)


def register():
    """
    Register a new tenant and admin user.
    
    Returns:
        JSON response with tenant and admin user
    """
    try:
        # Validate request data
        schema = RegisterSchema()
        data = schema.load(request.json)
        
        # Register tenant and admin
        result = register_tenant_and_admin(
            current_app.db_session,
            data['tenant_name'],
            data.get('subdomain'),
            data['email'],
            data['password'],
            data['first_name'],
            data['last_name'],
            data.get('phone')
        )
        
        # Generate tokens
        tokens = generate_tokens(result['admin'])
        
        # Return response
        return jsonify({
            'message': 'Registration successful',
            'tenant': result['tenant'].to_dict(),
            'user': result['admin'].to_dict(),
            'tokens': tokens
        }), 201
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except Exception as e:
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500


def login():
    """
    Login user with email and password.
    
    Returns:
        JSON response with user and tokens
    """
    try:
        # Validate request data
        schema = LoginSchema()
        data = schema.load(request.json)
        
        # Authenticate user
        user = authenticate_user(
            current_app.db_session,
            data['email'],
            data['password']
        )
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate tokens
        tokens = generate_tokens(user)
        
        # Return response
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'tokens': tokens
        }), 200
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500


@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token.
    
    Returns:
        JSON response with new access token
    """
    try:
        # Get user ID from JWT
        user_id = get_jwt_identity()
        
        # Get claims from refresh token
        claims = get_jwt()
        
        # Create new access token with same claims
        access_token = {
            'access_token': generate_tokens({
                'id': user_id,
                'tenant_id': claims['tenant_id'],
                'roles': claims['roles'],
                'email': claims['email']
            })['access_token']
        }
        
        # Return response
        return jsonify({
            'message': 'Token refresh successful',
            'access_token': access_token
        }), 200
    except Exception as e:
        current_app.logger.error(f"Token refresh error: {str(e)}")
        return jsonify({'error': 'Token refresh failed'}), 500


@jwt_required()
def logout():
    """
    Logout user by revoking refresh token.
    
    Returns:
        JSON response with success message
    """
    try:
        # In a real application, you would add the token to a blocklist
        # For simplicity, we'll just return success
        return jsonify({'message': 'Logout successful'}), 200
    except Exception as e:
        current_app.logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'Logout failed'}), 500


def forgot_password():
    """
    Start password reset flow.
    
    Returns:
        JSON response with success message
    """
    try:
        # Validate request data
        schema = ForgotPasswordSchema()
        data = schema.load(request.json)
        
        # In a real application, you would:
        # 1. Generate a reset token
        # 2. Store it in the database
        # 3. Send an email with a reset link
        
        # For simplicity, we'll just return success
        return jsonify({'message': 'Password reset instructions sent'}), 200
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except Exception as e:
        current_app.logger.error(f"Forgot password error: {str(e)}")
        return jsonify({'error': 'Forgot password failed'}), 500


def reset_password():
    """
    Reset password with token.
    
    Returns:
        JSON response with success message
    """
    try:
        # Validate request data
        schema = ResetPasswordSchema()
        data = schema.load(request.json)
        
        # In a real application, you would:
        # 1. Verify the reset token
        # 2. Update the user's password
        
        # For simplicity, we'll just return success
        return jsonify({'message': 'Password reset successful'}), 200
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except Exception as e:
        current_app.logger.error(f"Reset password error: {str(e)}")
        return jsonify({'error': 'Reset password failed'}), 500