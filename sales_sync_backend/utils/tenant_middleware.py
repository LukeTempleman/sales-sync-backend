from flask import g, request
from flask_jwt_extended import get_jwt, verify_jwt_in_request

def set_tenant_from_jwt():
    """
    Middleware to set tenant_id from JWT.
    This is called before each request to ensure tenant_id is available.
    """
    # Skip for public endpoints
    if request.path.startswith('/api/auth/') and request.method == 'POST':
        return
    
    try:
        verify_jwt_in_request(optional=True)
        claims = get_jwt()
        
        # Get tenant_id from JWT
        jwt_tenant_id = claims.get('tenant_id')
        
        # Check if user is super_admin (can access any tenant)
        user_roles = claims.get('roles', [])
        is_super_admin = 'super_admin' in user_roles if user_roles else False
        
        # If super_admin, allow X-Tenant-ID header to override tenant_id
        if is_super_admin and request.headers.get('X-Tenant-ID'):
            g.tenant_id = request.headers.get('X-Tenant-ID')
        else:
            g.tenant_id = jwt_tenant_id
    except:
        # If no JWT, tenant_id is None
        g.tenant_id = None