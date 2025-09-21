from flask import request, current_app, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime

from services.admin_service import (
    get_user_activity,
    get_survey_completion_rates,
    get_audit_logs
)
from utils.auth_decorators import admin_required, super_admin_required
from utils.request_utils import get_tenant_id_from_jwt


@jwt_required()
@admin_required
def get_user_activity_handler():
    """
    Get user activity for the current tenant.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Parse date range
    start_date = None
    end_date = None
    if request.args.get('start_date'):
        start_date = datetime.fromisoformat(request.args.get('start_date'))
    if request.args.get('end_date'):
        end_date = datetime.fromisoformat(request.args.get('end_date'))
    
    # Get user activity
    activity = get_user_activity(
        current_app.db_session,
        tenant_id,
        start_date,
        end_date
    )
    
    # Return activity
    return jsonify(activity), 200


@jwt_required()
@admin_required
def get_survey_completion_rates_handler():
    """
    Get survey completion rates for the current tenant.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Parse date range
    start_date = None
    end_date = None
    if request.args.get('start_date'):
        start_date = datetime.fromisoformat(request.args.get('start_date'))
    if request.args.get('end_date'):
        end_date = datetime.fromisoformat(request.args.get('end_date'))
    
    # Get survey completion rates
    rates = get_survey_completion_rates(
        current_app.db_session,
        tenant_id,
        start_date,
        end_date
    )
    
    # Return rates
    return jsonify(rates), 200


@jwt_required()
@admin_required
def get_tenant_audit_logs_handler():
    """
    Get audit logs for the current tenant.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get filters from query params
    user_id = request.args.get('user_id')
    action = request.args.get('action')
    object_type = request.args.get('object_type')
    object_id = request.args.get('object_id')
    
    # Parse date range
    start_date = None
    end_date = None
    if request.args.get('start_date'):
        start_date = datetime.fromisoformat(request.args.get('start_date'))
    if request.args.get('end_date'):
        end_date = datetime.fromisoformat(request.args.get('end_date'))
    
    # Parse pagination
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))
    
    # Get audit logs
    logs = get_audit_logs(
        current_app.db_session,
        tenant_id,
        user_id,
        action,
        object_type,
        object_id,
        start_date,
        end_date,
        limit,
        offset
    )
    
    # Return logs
    return jsonify(logs), 200


@jwt_required()
@super_admin_required
def get_all_audit_logs_handler():
    """
    Get audit logs for all tenants.
    """
    # Get filters from query params
    tenant_id = request.args.get('tenant_id')
    user_id = request.args.get('user_id')
    action = request.args.get('action')
    object_type = request.args.get('object_type')
    object_id = request.args.get('object_id')
    
    # Parse date range
    start_date = None
    end_date = None
    if request.args.get('start_date'):
        start_date = datetime.fromisoformat(request.args.get('start_date'))
    if request.args.get('end_date'):
        end_date = datetime.fromisoformat(request.args.get('end_date'))
    
    # Parse pagination
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))
    
    # Get audit logs
    logs = get_audit_logs(
        current_app.db_session,
        tenant_id,
        user_id,
        action,
        object_type,
        object_id,
        start_date,
        end_date,
        limit,
        offset
    )
    
    # Return logs
    return jsonify(logs), 200