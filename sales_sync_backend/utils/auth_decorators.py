from functools import wraps
from flask import jsonify, request, g
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def role_required(roles):
    """
    Decorator to check if the user has the required role.
    
    Args:
        roles (str or list): Role or list of roles required to access the endpoint.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            
            # Convert single role to list
            required_roles = roles if isinstance(roles, list) else [roles]
            
            # Check if user has any of the required roles
            user_roles = claims.get('roles', [])
            if not any(role in user_roles for role in required_roles):
                return jsonify({"error": "Insufficient permissions"}), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def admin_required(fn):
    """Decorator to check if the user has admin role."""
    return role_required(['admin', 'super_admin'])(fn)


def super_admin_required(fn):
    """Decorator to check if the user has super_admin role."""
    return role_required('super_admin')(fn)


def agent_required(fn):
    """Decorator to check if the user has agent role or higher."""
    return role_required(['agent', 'team_leader', 'area_manager', 'regional_manager', 
                         'national_manager', 'admin', 'super_admin'])(fn)


def team_leader_required(fn):
    """Decorator to check if the user has team_leader role or higher."""
    return role_required(['team_leader', 'area_manager', 'regional_manager', 
                         'national_manager', 'admin', 'super_admin'])(fn)


def area_manager_required(fn):
    """Decorator to check if the user has area_manager role or higher."""
    return role_required(['area_manager', 'regional_manager', 
                         'national_manager', 'admin', 'super_admin'])(fn)


def regional_manager_required(fn):
    """Decorator to check if the user has regional_manager role or higher."""
    return role_required(['regional_manager', 'national_manager', 'admin', 'super_admin'])(fn)


def national_manager_required(fn):
    """Decorator to check if the user has national_manager role or higher."""
    return role_required(['national_manager', 'admin', 'super_admin'])(fn)


def manager_required(fn):
    """Decorator to check if the user has any manager role or higher."""
    return role_required(['team_leader', 'area_manager', 'regional_manager', 
                         'national_manager', 'admin', 'super_admin'])(fn)


def tenant_required(fn):
    """
    Decorator to check if the tenant_id in the JWT matches the tenant_id in the request.
    This is used for tenant-scoped endpoints.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        
        # Get tenant_id from JWT
        jwt_tenant_id = claims.get('tenant_id')
        
        # Check if user is super_admin (can access any tenant)
        user_roles = claims.get('roles', [])
        is_super_admin = 'super_admin' in user_roles
        
        # If super_admin, allow X-Tenant-ID header to override tenant_id
        if is_super_admin and request.headers.get('X-Tenant-ID'):
            g.tenant_id = request.headers.get('X-Tenant-ID')
        else:
            g.tenant_id = jwt_tenant_id
        
        # If no tenant_id, return error
        if not g.tenant_id:
            return jsonify({"error": "Tenant ID is required"}), 403
        
        return fn(*args, **kwargs)
    return wrapper