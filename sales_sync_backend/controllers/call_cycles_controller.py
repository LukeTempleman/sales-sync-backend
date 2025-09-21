from flask import request, current_app, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from services.call_cycle_service import (
    get_call_cycles,
    get_call_cycle_by_id,
    create_call_cycle,
    update_call_cycle,
    delete_call_cycle,
    get_call_cycle_locations,
    add_call_cycle_location,
    remove_call_cycle_location,
    update_call_cycle_location_order,
    get_call_cycle_status
)
from utils.auth_decorators import manager_required, tenant_required
from utils.request_utils import get_tenant_id_from_jwt


@jwt_required()
@tenant_required
def get_call_cycles_handler():
    """
    Get call cycles for the current tenant.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get filters from query params
    filters = {}
    if request.args.get('name'):
        filters['name'] = request.args.get('name')
    if request.args.get('frequency'):
        filters['frequency'] = request.args.get('frequency')
    if request.args.get('created_by'):
        filters['created_by'] = request.args.get('created_by')
    
    # Get call cycles
    call_cycles = get_call_cycles(current_app.db_session, tenant_id, filters)
    
    # Return call cycles
    return jsonify([call_cycle.to_dict() for call_cycle in call_cycles]), 200


@jwt_required()
@tenant_required
def get_call_cycle_handler(call_cycle_id):
    """
    Get call cycle by ID.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get call cycle
    call_cycle = get_call_cycle_by_id(current_app.db_session, tenant_id, call_cycle_id)
    if not call_cycle:
        return jsonify({'error': 'Call cycle not found'}), 404
    
    # Return call cycle
    return jsonify(call_cycle.to_dict()), 200


@jwt_required()
@manager_required
def create_call_cycle_handler():
    """
    Create a new call cycle.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get user ID from JWT
    user_id = get_jwt_identity()
    
    # Get request data
    data = request.get_json()
    
    # Validate request data
    if not data.get('name'):
        return jsonify({'error': 'Call cycle name is required'}), 400
    if not data.get('frequency'):
        return jsonify({'error': 'Call cycle frequency is required'}), 400
    if data.get('frequency') not in ['daily', 'weekly', 'monthly']:
        return jsonify({'error': 'Call cycle frequency must be "daily", "weekly", or "monthly"'}), 400
    
    # Create call cycle
    call_cycle = create_call_cycle(
        current_app.db_session,
        tenant_id,
        data.get('name'),
        data.get('frequency'),
        user_id
    )
    
    # Return call cycle
    return jsonify(call_cycle.to_dict()), 201


@jwt_required()
@manager_required
def update_call_cycle_handler(call_cycle_id):
    """
    Update a call cycle.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get request data
    data = request.get_json()
    
    # Update call cycle
    call_cycle = update_call_cycle(current_app.db_session, tenant_id, call_cycle_id, data)
    if not call_cycle:
        return jsonify({'error': 'Call cycle not found'}), 404
    
    # Return call cycle
    return jsonify(call_cycle.to_dict()), 200


@jwt_required()
@manager_required
def delete_call_cycle_handler(call_cycle_id):
    """
    Delete a call cycle.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Delete call cycle
    success = delete_call_cycle(current_app.db_session, tenant_id, call_cycle_id)
    if not success:
        return jsonify({'error': 'Call cycle not found'}), 404
    
    # Return success
    return jsonify({'message': 'Call cycle deleted successfully'}), 200


@jwt_required()
@tenant_required
def get_call_cycle_locations_handler(call_cycle_id):
    """
    Get locations for a call cycle.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get call cycle
    call_cycle = get_call_cycle_by_id(current_app.db_session, tenant_id, call_cycle_id)
    if not call_cycle:
        return jsonify({'error': 'Call cycle not found'}), 404
    
    # Get call cycle locations
    locations = get_call_cycle_locations(current_app.db_session, tenant_id, call_cycle_id)
    
    # Return call cycle locations
    return jsonify([location.to_dict() for location in locations]), 200


@jwt_required()
@manager_required
def add_call_cycle_location_handler(call_cycle_id):
    """
    Add a location to a call cycle.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get call cycle
    call_cycle = get_call_cycle_by_id(current_app.db_session, tenant_id, call_cycle_id)
    if not call_cycle:
        return jsonify({'error': 'Call cycle not found'}), 404
    
    # Get request data
    data = request.get_json()
    
    # Validate request data
    if not data.get('location'):
        return jsonify({'error': 'Location is required'}), 400
    
    # Add location to call cycle
    location = add_call_cycle_location(
        current_app.db_session,
        call_cycle_id,
        data.get('location'),
        data.get('shop_id'),
        data.get('order_num', 0)
    )
    
    # Return call cycle location
    return jsonify(location.to_dict()), 201


@jwt_required()
@manager_required
def remove_call_cycle_location_handler(call_cycle_id, location_id):
    """
    Remove a location from a call cycle.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get call cycle
    call_cycle = get_call_cycle_by_id(current_app.db_session, tenant_id, call_cycle_id)
    if not call_cycle:
        return jsonify({'error': 'Call cycle not found'}), 404
    
    # Remove location from call cycle
    success = remove_call_cycle_location(
        current_app.db_session,
        call_cycle_id,
        location_id
    )
    
    if not success:
        return jsonify({'error': 'Call cycle location not found'}), 404
    
    # Return success
    return jsonify({'message': 'Call cycle location removed successfully'}), 200


@jwt_required()
@manager_required
def update_call_cycle_location_order_handler(call_cycle_id, location_id):
    """
    Update the order of a call cycle location.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get call cycle
    call_cycle = get_call_cycle_by_id(current_app.db_session, tenant_id, call_cycle_id)
    if not call_cycle:
        return jsonify({'error': 'Call cycle not found'}), 404
    
    # Get request data
    data = request.get_json()
    
    # Validate request data
    if 'order_num' not in data:
        return jsonify({'error': 'Order number is required'}), 400
    
    # Update call cycle location order
    location = update_call_cycle_location_order(
        current_app.db_session,
        call_cycle_id,
        location_id,
        data.get('order_num')
    )
    
    if not location:
        return jsonify({'error': 'Call cycle location not found'}), 404
    
    # Return call cycle location
    return jsonify(location.to_dict()), 200


@jwt_required()
@tenant_required
def get_call_cycle_status_handler(call_cycle_id):
    """
    Get status for a call cycle.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get call cycle status
    status = get_call_cycle_status(current_app.db_session, tenant_id, call_cycle_id)
    if not status:
        return jsonify({'error': 'Call cycle not found'}), 404
    
    # Return call cycle status
    return jsonify(status), 200