from flask import jsonify, request, current_app
from marshmallow import ValidationError

from services.tenant_service import (
    get_tenants,
    get_tenant_by_id,
    create_tenant,
    update_tenant
)
from utils.auth_decorators import super_admin_required, admin_required, tenant_required


@super_admin_required
def get_tenants_handler():
    """
    Get all tenants.
    
    Returns:
        JSON response with tenants
    """
    try:
        # Get tenants
        tenants = get_tenants(current_app.db_session)
        
        # Return response
        return jsonify({
            'tenants': [tenant.to_dict() for tenant in tenants]
        }), 200
    except Exception as e:
        current_app.logger.error(f"Get tenants error: {str(e)}")
        return jsonify({'error': 'Failed to get tenants'}), 500


@super_admin_required
def create_tenant_handler():
    """
    Create a new tenant.
    
    Returns:
        JSON response with created tenant
    """
    try:
        # Validate request data
        if not request.json or 'name' not in request.json:
            return jsonify({'error': 'Tenant name is required'}), 400
        
        # Create tenant
        tenant = create_tenant(
            current_app.db_session,
            request.json['name'],
            request.json.get('subdomain')
        )
        
        # Return response
        return jsonify({
            'message': 'Tenant created successfully',
            'tenant': tenant.to_dict()
        }), 201
    except Exception as e:
        current_app.logger.error(f"Tenant creation error: {str(e)}")
        return jsonify({'error': 'Tenant creation failed'}), 500


@super_admin_required
def get_tenant_handler(tenant_id):
    """
    Get tenant by ID.
    
    Args:
        tenant_id: Tenant ID
    
    Returns:
        JSON response with tenant
    """
    try:
        # Get tenant
        tenant = get_tenant_by_id(current_app.db_session, tenant_id)
        
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
        
        # Return response
        return jsonify({
            'tenant': tenant.to_dict()
        }), 200
    except Exception as e:
        current_app.logger.error(f"Get tenant error: {str(e)}")
        return jsonify({'error': 'Failed to get tenant'}), 500


@super_admin_required
def update_tenant_handler(tenant_id):
    """
    Update a tenant.
    
    Args:
        tenant_id: Tenant ID
    
    Returns:
        JSON response with updated tenant
    """
    try:
        # Validate request data
        if not request.json:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update tenant
        tenant = update_tenant(current_app.db_session, tenant_id, request.json)
        
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
        
        # Return response
        return jsonify({
            'message': 'Tenant updated successfully',
            'tenant': tenant.to_dict()
        }), 200
    except Exception as e:
        current_app.logger.error(f"Tenant update error: {str(e)}")
        return jsonify({'error': 'Tenant update failed'}), 500