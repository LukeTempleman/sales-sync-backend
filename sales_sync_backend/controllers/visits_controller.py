from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from services.visit_service import (
    get_visits,
    get_visit_by_id,
    create_visit,
    complete_visit,
    get_visit_answers,
    get_visit_photos
)
from utils.auth_decorators import agent_required, tenant_required
from utils.request_utils import get_tenant_id_from_jwt


@jwt_required()
@tenant_required
def get_visits_handler():
    """
    Get visits for the current tenant.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get filters from query params
    filters = {}
    if request.args.get('user_id'):
        filters['user_id'] = request.args.get('user_id')
    if request.args.get('survey_id'):
        filters['survey_id'] = request.args.get('survey_id')
    if request.args.get('visit_type'):
        filters['visit_type'] = request.args.get('visit_type')
    if request.args.get('shop_id'):
        filters['shop_id'] = request.args.get('shop_id')
    if request.args.get('start_date'):
        filters['start_date'] = request.args.get('start_date')
    if request.args.get('end_date'):
        filters['end_date'] = request.args.get('end_date')
    if request.args.get('completed'):
        filters['completed'] = request.args.get('completed').lower() == 'true'
    
    # Get visits
    visits = get_visits(request.app.db_session, tenant_id, filters)
    
    # Return visits
    return jsonify([visit.to_dict() for visit in visits]), 200


@jwt_required()
@tenant_required
def get_visit_handler(visit_id):
    """
    Get visit by ID.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get visit
    visit = get_visit_by_id(request.app.db_session, tenant_id, visit_id)
    if not visit:
        return jsonify({'error': 'Visit not found'}), 404
    
    # Return visit
    return jsonify(visit.to_dict()), 200


@jwt_required()
@agent_required
def create_visit_handler():
    """
    Create a new visit.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get user ID from JWT
    user_id = get_jwt_identity()
    
    # Get request data
    data = request.get_json()
    
    # Validate request data
    if not data.get('survey_id'):
        return jsonify({'error': 'Survey ID is required'}), 400
    if not data.get('visit_type'):
        return jsonify({'error': 'Visit type is required'}), 400
    if data.get('visit_type') not in ['individual', 'shop']:
        return jsonify({'error': 'Visit type must be "individual" or "shop"'}), 400
    
    # Create visit
    visit = create_visit(
        request.app.db_session,
        tenant_id,
        user_id,
        data.get('survey_id'),
        data.get('visit_type'),
        data.get('geocode'),
        data.get('shop_id')
    )
    
    # Return visit
    return jsonify(visit.to_dict()), 201


@jwt_required()
@agent_required
def complete_visit_handler(visit_id):
    """
    Complete a visit.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get user ID from JWT
    user_id = get_jwt_identity()
    
    # Get visit
    visit = get_visit_by_id(request.app.db_session, tenant_id, visit_id)
    if not visit:
        return jsonify({'error': 'Visit not found'}), 404
    
    # Check if user owns the visit
    if str(visit.user_id) != user_id:
        return jsonify({'error': 'You do not have permission to complete this visit'}), 403
    
    # Check if visit is already completed
    if visit.completed_at:
        return jsonify({'error': 'Visit is already completed'}), 400
    
    # Get request data
    data = request.get_json()
    
    # Complete visit
    visit = complete_visit(
        request.app.db_session,
        tenant_id,
        visit_id,
        data.get('answers')
    )
    
    # Return visit
    return jsonify(visit.to_dict()), 200


@jwt_required()
@tenant_required
def get_visit_answers_handler(visit_id):
    """
    Get answers for a visit.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get visit
    visit = get_visit_by_id(request.app.db_session, tenant_id, visit_id)
    if not visit:
        return jsonify({'error': 'Visit not found'}), 404
    
    # Get answers
    answers = get_visit_answers(request.app.db_session, tenant_id, visit_id)
    
    # Return answers
    return jsonify([answer.to_dict() for answer in answers]), 200


@jwt_required()
@tenant_required
def get_visit_photos_handler(visit_id):
    """
    Get photos for a visit.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get visit
    visit = get_visit_by_id(request.app.db_session, tenant_id, visit_id)
    if not visit:
        return jsonify({'error': 'Visit not found'}), 404
    
    # Get photos
    photos = get_visit_photos(request.app.db_session, tenant_id, visit_id)
    
    # Return photos
    return jsonify([photo.to_dict() for photo in photos]), 200