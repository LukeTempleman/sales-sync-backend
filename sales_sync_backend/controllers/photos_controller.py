from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from services.photo_service import (
    get_photos,
    get_photo_by_id,
    create_photo,
    get_shelf_quadrants,
    create_shelf_quadrant
)
from utils.auth_decorators import agent_required, tenant_required
from utils.request_utils import get_tenant_id_from_jwt
from utils.image_utils import upload_file_to_s3


@jwt_required()
@tenant_required
def get_photos_handler():
    """
    Get photos for the current tenant.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get filters from query params
    filters = {}
    if request.args.get('visit_id'):
        filters['visit_id'] = request.args.get('visit_id')
    if request.args.get('purpose'):
        filters['purpose'] = request.args.get('purpose')
    
    # Get photos
    photos = get_photos(request.app.db_session, tenant_id, filters)
    
    # Return photos
    return jsonify([photo.to_dict() for photo in photos]), 200


@jwt_required()
@tenant_required
def get_photo_handler(photo_id):
    """
    Get photo by ID.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get photo
    photo = get_photo_by_id(request.app.db_session, tenant_id, photo_id)
    if not photo:
        return jsonify({'error': 'Photo not found'}), 404
    
    # Return photo
    return jsonify(photo.to_dict()), 200


@jwt_required()
@agent_required
def create_photo_handler():
    """
    Create a new photo.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get request data
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Get form data
    visit_id = request.form.get('visit_id')
    if not visit_id:
        return jsonify({'error': 'Visit ID is required'}), 400
    
    purpose = request.form.get('purpose')
    metadata = {}
    
    # Upload image
    file_url = upload_file_to_s3(file)
    
    # Create photo
    photo = create_photo(
        request.app.db_session,
        tenant_id,
        visit_id,
        file_url,
        purpose,
        metadata
    )
    
    # Return photo
    return jsonify(photo.to_dict()), 201


@jwt_required()
@tenant_required
def get_shelf_quadrants_handler(photo_id):
    """
    Get shelf quadrants for a photo.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get photo
    photo = get_photo_by_id(request.app.db_session, tenant_id, photo_id)
    if not photo:
        return jsonify({'error': 'Photo not found'}), 404
    
    # Get shelf quadrants
    shelf_quadrants = get_shelf_quadrants(request.app.db_session, tenant_id, photo_id)
    
    # Return shelf quadrants
    return jsonify([sq.to_dict() for sq in shelf_quadrants]), 200


@jwt_required()
@agent_required
def create_shelf_quadrant_handler(photo_id):
    """
    Create a new shelf quadrant.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get photo
    photo = get_photo_by_id(request.app.db_session, tenant_id, photo_id)
    if not photo:
        return jsonify({'error': 'Photo not found'}), 404
    
    # Get request data
    data = request.get_json()
    
    # Validate request data
    if not data.get('brand_id'):
        return jsonify({'error': 'Brand ID is required'}), 400
    if not data.get('quadrant_coords'):
        return jsonify({'error': 'Quadrant coordinates are required'}), 400
    
    # Create shelf quadrant
    shelf_quadrant = create_shelf_quadrant(
        request.app.db_session,
        tenant_id,
        photo_id,
        data.get('brand_id'),
        data.get('quadrant_coords'),
        data.get('area_percentage')
    )
    
    # Return shelf quadrant
    return jsonify(shelf_quadrant.to_dict()), 201