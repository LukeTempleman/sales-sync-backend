from flask import Blueprint

from controllers.brands_controller import (
    get_brands_handler,
    create_brand_handler,
    get_brand_handler,
    update_brand_handler,
    delete_brand_handler,
    get_brand_infographics_handler,
    create_brand_infographic_handler
)

# Create blueprint
brands_bp = Blueprint('brands', __name__, url_prefix='/api/brands')

# Register routes
brands_bp.route('', methods=['GET'])(get_brands_handler)
brands_bp.route('', methods=['POST'])(create_brand_handler)
brands_bp.route('/<uuid:brand_id>', methods=['GET'])(get_brand_handler)
brands_bp.route('/<uuid:brand_id>', methods=['PUT'])(update_brand_handler)
brands_bp.route('/<uuid:brand_id>', methods=['DELETE'])(delete_brand_handler)
brands_bp.route('/<uuid:brand_id>/infographics', methods=['GET'])(get_brand_infographics_handler)
brands_bp.route('/<uuid:brand_id>/infographics', methods=['POST'])(create_brand_infographic_handler)