from flask import Blueprint

from controllers.visits_controller import (
    get_visits_handler,
    get_visit_handler,
    create_visit_handler,
    complete_visit_handler,
    get_visit_answers_handler,
    get_visit_photos_handler
)

# Create blueprint
visits_bp = Blueprint('visits', __name__, url_prefix='/api/visits')

# Register routes
visits_bp.route('', methods=['GET'])(get_visits_handler)
visits_bp.route('', methods=['POST'])(create_visit_handler)
visits_bp.route('/<uuid:visit_id>', methods=['GET'])(get_visit_handler)
visits_bp.route('/<uuid:visit_id>/complete', methods=['PUT'])(complete_visit_handler)
visits_bp.route('/<uuid:visit_id>/answers', methods=['GET'])(get_visit_answers_handler)
visits_bp.route('/<uuid:visit_id>/photos', methods=['GET'])(get_visit_photos_handler)