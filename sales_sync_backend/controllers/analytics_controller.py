from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from services.analytics_service import (
    get_overview_metrics,
    get_visits_metrics,
    get_shelf_share_metrics,
    get_call_cycle_coverage_metrics
)
from utils.auth_decorators import tenant_required
from utils.request_utils import get_tenant_id_from_jwt


@jwt_required()
@tenant_required
def get_overview_handler():
    """
    Get overview metrics for the current tenant.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get filters from query params
    user_id = request.args.get('user_id')
    
    # Parse date range
    start_date = None
    end_date = None
    if request.args.get('start_date'):
        start_date = datetime.fromisoformat(request.args.get('start_date'))
    if request.args.get('end_date'):
        end_date = datetime.fromisoformat(request.args.get('end_date'))
    
    # Get overview metrics
    metrics = get_overview_metrics(
        request.app.db_session,
        tenant_id,
        user_id,
        start_date,
        end_date
    )
    
    # Return metrics
    return jsonify(metrics), 200


@jwt_required()
@tenant_required
def get_visits_handler():
    """
    Get visits metrics for the current tenant.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get filters from query params
    user_id = request.args.get('user_id')
    group_by = request.args.get('group_by', 'day')
    
    # Parse date range
    start_date = None
    end_date = None
    if request.args.get('start_date'):
        start_date = datetime.fromisoformat(request.args.get('start_date'))
    if request.args.get('end_date'):
        end_date = datetime.fromisoformat(request.args.get('end_date'))
    
    # Get visits metrics
    metrics = get_visits_metrics(
        request.app.db_session,
        tenant_id,
        user_id,
        start_date,
        end_date,
        group_by
    )
    
    # Return metrics
    return jsonify(metrics), 200


@jwt_required()
@tenant_required
def get_shelf_share_handler():
    """
    Get shelf share metrics for the current tenant.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get filters from query params
    user_id = request.args.get('user_id')
    
    # Parse date range
    start_date = None
    end_date = None
    if request.args.get('start_date'):
        start_date = datetime.fromisoformat(request.args.get('start_date'))
    if request.args.get('end_date'):
        end_date = datetime.fromisoformat(request.args.get('end_date'))
    
    # Get shelf share metrics
    metrics = get_shelf_share_metrics(
        request.app.db_session,
        tenant_id,
        user_id,
        start_date,
        end_date
    )
    
    # Return metrics
    return jsonify(metrics), 200


@jwt_required()
@tenant_required
def get_call_cycle_coverage_handler():
    """
    Get call cycle coverage metrics for the current tenant.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get filters from query params
    user_id = request.args.get('user_id')
    
    # Parse date range
    start_date = None
    end_date = None
    if request.args.get('start_date'):
        start_date = datetime.fromisoformat(request.args.get('start_date'))
    if request.args.get('end_date'):
        end_date = datetime.fromisoformat(request.args.get('end_date'))
    
    # Get call cycle coverage metrics
    metrics = get_call_cycle_coverage_metrics(
        request.app.db_session,
        tenant_id,
        user_id,
        start_date,
        end_date
    )
    
    # Return metrics
    return jsonify(metrics), 200