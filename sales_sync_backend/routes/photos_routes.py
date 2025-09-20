from flask import Blueprint

from controllers.photos_controller import (
    get_photos_handler,
    get_photo_handler,
    create_photo_handler,
    get_shelf_quadrants_handler,
    create_shelf_quadrant_handler
)

# Create blueprint
photos_bp = Blueprint('photos', __name__, url_prefix='/api/photos')

# Register routes
photos_bp.route('', methods=['GET'])(get_photos_handler)
photos_bp.route('', methods=['POST'])(create_photo_handler)
photos_bp.route('/<uuid:photo_id>', methods=['GET'])(get_photo_handler)
photos_bp.route('/<uuid:photo_id>/shelf_quadrants', methods=['GET'])(get_shelf_quadrants_handler)
photos_bp.route('/<uuid:photo_id>/shelf_quadrants', methods=['POST'])(create_shelf_quadrant_handler)