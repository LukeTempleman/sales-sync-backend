from flask import jsonify, request, g, current_app
from marshmallow import ValidationError

from services.brand_service import (
    get_brands,
    get_brand_by_id,
    create_brand,
    update_brand,
    delete_brand,
    get_brand_infographics,
    create_brand_infographic
)
from utils.validators import (
    BrandCreateSchema,
    BrandUpdateSchema,
    BrandInfographicSchema
)
from utils.auth_decorators import admin_required, tenant_required


@tenant_required
def get_brands_handler():
    """
    Get brands for a tenant.
    
    Returns:
        JSON response with brands
    """
    try:
        # Get filters from query params
        filters = {}
        if request.args.get('name'):
            filters['name'] = request.args.get('name')
        if request.args.get('active'):
            filters['active'] = request.args.get('active').lower() == 'true'
        
        # Get brands
        brands = get_brands(current_app.db_session, g.tenant_id, filters)
        
        # Return response
        return jsonify({
            'brands': [brand.to_dict() for brand in brands]
        }), 200
    except Exception as e:
        current_app.logger.error(f"Get brands error: {str(e)}")
        return jsonify({'error': 'Failed to get brands'}), 500


@tenant_required
@admin_required
def create_brand_handler():
    """
    Create a new brand.
    
    Returns:
        JSON response with created brand
    """
    try:
        # Validate request data
        schema = BrandCreateSchema()
        data = schema.load(request.json)
        
        # Create brand
        brand = create_brand(
            current_app.db_session,
            g.tenant_id,
            data['name'],
            data.get('slug'),
            data.get('active', True)
        )
        
        # Return response
        return jsonify({
            'message': 'Brand created successfully',
            'brand': brand.to_dict()
        }), 201
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except Exception as e:
        current_app.logger.error(f"Brand creation error: {str(e)}")
        return jsonify({'error': 'Brand creation failed'}), 500


@tenant_required
def get_brand_handler(brand_id):
    """
    Get brand by ID.
    
    Args:
        brand_id: Brand ID
    
    Returns:
        JSON response with brand
    """
    try:
        # Get brand
        brand = get_brand_by_id(current_app.db_session, g.tenant_id, brand_id)
        
        if not brand:
            return jsonify({'error': 'Brand not found'}), 404
        
        # Return response
        return jsonify({
            'brand': brand.to_dict()
        }), 200
    except Exception as e:
        current_app.logger.error(f"Get brand error: {str(e)}")
        return jsonify({'error': 'Failed to get brand'}), 500


@tenant_required
@admin_required
def update_brand_handler(brand_id):
    """
    Update a brand.
    
    Args:
        brand_id: Brand ID
    
    Returns:
        JSON response with updated brand
    """
    try:
        # Validate request data
        schema = BrandUpdateSchema()
        data = schema.load(request.json)
        
        # Update brand
        brand = update_brand(current_app.db_session, g.tenant_id, brand_id, data)
        
        if not brand:
            return jsonify({'error': 'Brand not found'}), 404
        
        # Return response
        return jsonify({
            'message': 'Brand updated successfully',
            'brand': brand.to_dict()
        }), 200
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except Exception as e:
        current_app.logger.error(f"Brand update error: {str(e)}")
        return jsonify({'error': 'Brand update failed'}), 500


@tenant_required
@admin_required
def delete_brand_handler(brand_id):
    """
    Delete a brand.
    
    Args:
        brand_id: Brand ID
    
    Returns:
        JSON response with success message
    """
    try:
        # Delete brand
        success = delete_brand(current_app.db_session, g.tenant_id, brand_id)
        
        if not success:
            return jsonify({'error': 'Brand not found'}), 404
        
        # Return response
        return jsonify({
            'message': 'Brand deleted successfully'
        }), 200
    except Exception as e:
        current_app.logger.error(f"Brand deletion error: {str(e)}")
        return jsonify({'error': 'Brand deletion failed'}), 500


@tenant_required
def get_brand_infographics_handler(brand_id):
    """
    Get infographics for a brand.
    
    Args:
        brand_id: Brand ID
    
    Returns:
        JSON response with infographics
    """
    try:
        # Check if brand exists
        brand = get_brand_by_id(current_app.db_session, g.tenant_id, brand_id)
        if not brand:
            return jsonify({'error': 'Brand not found'}), 404
        
        # Get infographics
        infographics = get_brand_infographics(current_app.db_session, g.tenant_id, brand_id)
        
        # Return response
        return jsonify({
            'infographics': [infographic.to_dict() for infographic in infographics]
        }), 200
    except Exception as e:
        current_app.logger.error(f"Get brand infographics error: {str(e)}")
        return jsonify({'error': 'Failed to get brand infographics'}), 500


@tenant_required
@admin_required
def create_brand_infographic_handler(brand_id):
    """
    Create a new brand infographic.
    
    Args:
        brand_id: Brand ID
    
    Returns:
        JSON response with created infographic
    """
    try:
        # Check if brand exists
        brand = get_brand_by_id(current_app.db_session, g.tenant_id, brand_id)
        if not brand:
            return jsonify({'error': 'Brand not found'}), 404
        
        # Validate request data
        schema = BrandInfographicSchema()
        data = schema.load(request.json)
        
        # Create infographic
        infographic = create_brand_infographic(
            current_app.db_session,
            g.tenant_id,
            brand_id,
            data['file_url'],
            data.get('caption')
        )
        
        # Return response
        return jsonify({
            'message': 'Brand infographic created successfully',
            'infographic': infographic.to_dict()
        }), 201
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    except Exception as e:
        current_app.logger.error(f"Brand infographic creation error: {str(e)}")
        return jsonify({'error': 'Brand infographic creation failed'}), 500