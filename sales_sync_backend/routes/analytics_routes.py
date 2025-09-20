from flask import Blueprint

from controllers.analytics_controller import (
    get_overview_handler,
    get_visits_handler,
    get_shelf_share_handler,
    get_call_cycle_coverage_handler
)

# Create blueprint
analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

# Register routes
analytics_bp.route('/overview', methods=['GET'])(get_overview_handler)
analytics_bp.route('/visits', methods=['GET'])(get_visits_handler)
analytics_bp.route('/shelf_share', methods=['GET'])(get_shelf_share_handler)
analytics_bp.route('/call_cycle_coverage', methods=['GET'])(get_call_cycle_coverage_handler)