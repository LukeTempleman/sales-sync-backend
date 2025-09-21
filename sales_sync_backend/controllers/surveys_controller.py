from flask import request, current_app, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from services.survey_service import (
    get_surveys,
    get_survey_by_id,
    create_survey,
    update_survey,
    delete_survey,
    get_survey_questions,
    get_question_by_id,
    create_question,
    update_question,
    delete_question
)
from utils.auth_decorators import admin_required, tenant_required
from utils.request_utils import get_tenant_id_from_jwt


@jwt_required()
@tenant_required
def get_surveys_handler():
    """
    Get surveys for the current tenant.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get filters from query params
    filters = {}
    if request.args.get('name'):
        filters['name'] = request.args.get('name')
    if request.args.get('type'):
        filters['type'] = request.args.get('type')
    if request.args.get('active'):
        filters['active'] = request.args.get('active').lower() == 'true'
    if request.args.get('brand_id'):
        filters['brand_id'] = request.args.get('brand_id')
    
    # Get surveys
    surveys = get_surveys(current_app.db_session, tenant_id, filters)
    
    # Return surveys
    return jsonify([survey.to_dict() for survey in surveys]), 200


@jwt_required()
@tenant_required
def get_survey_handler(survey_id):
    """
    Get survey by ID.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get survey
    survey = get_survey_by_id(current_app.db_session, tenant_id, survey_id)
    if not survey:
        return jsonify({'error': 'Survey not found'}), 404
    
    # Return survey
    return jsonify(survey.to_dict()), 200


@jwt_required()
@admin_required
def create_survey_handler():
    """
    Create a new survey.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get user ID from JWT
    user_id = get_jwt_identity()
    
    # Get request data
    data = request.get_json()
    
    # Validate request data
    if not data.get('name'):
        return jsonify({'error': 'Survey name is required'}), 400
    if not data.get('type'):
        return jsonify({'error': 'Survey type is required'}), 400
    if data.get('type') not in ['individual', 'shop']:
        return jsonify({'error': 'Survey type must be "individual" or "shop"'}), 400
    
    # Create survey
    survey = create_survey(
        current_app.db_session,
        tenant_id,
        data.get('name'),
        data.get('type'),
        data.get('brand_id'),
        data.get('active', True),
        user_id
    )
    
    # Return survey
    return jsonify(survey.to_dict()), 201


@jwt_required()
@admin_required
def update_survey_handler(survey_id):
    """
    Update a survey.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get request data
    data = request.get_json()
    
    # Update survey
    survey = update_survey(current_app.db_session, tenant_id, survey_id, data)
    if not survey:
        return jsonify({'error': 'Survey not found'}), 404
    
    # Return survey
    return jsonify(survey.to_dict()), 200


@jwt_required()
@admin_required
def delete_survey_handler(survey_id):
    """
    Delete a survey.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Delete survey
    success = delete_survey(current_app.db_session, tenant_id, survey_id)
    if not success:
        return jsonify({'error': 'Survey not found'}), 404
    
    # Return success
    return jsonify({'message': 'Survey deleted successfully'}), 200


@jwt_required()
@tenant_required
def get_survey_questions_handler(survey_id):
    """
    Get questions for a survey.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get survey
    survey = get_survey_by_id(current_app.db_session, tenant_id, survey_id)
    if not survey:
        return jsonify({'error': 'Survey not found'}), 404
    
    # Get questions
    questions = get_survey_questions(current_app.db_session, tenant_id, survey_id)
    
    # Return questions
    return jsonify([question.to_dict() for question in questions]), 200


@jwt_required()
@admin_required
def create_question_handler(survey_id):
    """
    Create a new question for a survey.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get survey
    survey = get_survey_by_id(current_app.db_session, tenant_id, survey_id)
    if not survey:
        return jsonify({'error': 'Survey not found'}), 404
    
    # Get request data
    data = request.get_json()
    
    # Validate request data
    if not data.get('question_text'):
        return jsonify({'error': 'Question text is required'}), 400
    if not data.get('input_type'):
        return jsonify({'error': 'Input type is required'}), 400
    if data.get('input_type') not in ['text', 'select', 'boolean', 'photo', 'number']:
        return jsonify({'error': 'Input type must be "text", "select", "boolean", "photo", or "number"'}), 400
    
    # Create question
    question = create_question(
        current_app.db_session,
        tenant_id,
        survey_id,
        data.get('question_text'),
        data.get('input_type'),
        data.get('meta'),
        data.get('order_num', 0)
    )
    
    # Return question
    return jsonify(question.to_dict()), 201


@jwt_required()
@admin_required
def update_question_handler(question_id):
    """
    Update a question.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get request data
    data = request.get_json()
    
    # Update question
    question = update_question(current_app.db_session, tenant_id, question_id, data)
    if not question:
        return jsonify({'error': 'Question not found'}), 404
    
    # Return question
    return jsonify(question.to_dict()), 200


@jwt_required()
@admin_required
def delete_question_handler(question_id):
    """
    Delete a question.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Delete question
    success = delete_question(current_app.db_session, tenant_id, question_id)
    if not success:
        return jsonify({'error': 'Question not found'}), 404
    
    # Return success
    return jsonify({'message': 'Question deleted successfully'}), 200