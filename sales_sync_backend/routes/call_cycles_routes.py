from flask import Blueprint

from controllers.call_cycles_controller import (
    get_call_cycles_handler,
    get_call_cycle_handler,
    create_call_cycle_handler,
    update_call_cycle_handler,
    delete_call_cycle_handler,
    get_call_cycle_locations_handler,
    add_call_cycle_location_handler,
    remove_call_cycle_location_handler,
    update_call_cycle_location_order_handler,
    get_call_cycle_status_handler
)

# Create blueprint
call_cycles_bp = Blueprint('call_cycles', __name__, url_prefix='/api/call_cycles')

# Register routes
call_cycles_bp.route('', methods=['GET'])(get_call_cycles_handler)
call_cycles_bp.route('', methods=['POST'])(create_call_cycle_handler)
call_cycles_bp.route('/<uuid:call_cycle_id>', methods=['GET'])(get_call_cycle_handler)
call_cycles_bp.route('/<uuid:call_cycle_id>', methods=['PUT'])(update_call_cycle_handler)
call_cycles_bp.route('/<uuid:call_cycle_id>', methods=['DELETE'])(delete_call_cycle_handler)
call_cycles_bp.route('/<uuid:call_cycle_id>/locations', methods=['GET'])(get_call_cycle_locations_handler)
call_cycles_bp.route('/<uuid:call_cycle_id>/locations', methods=['POST'])(add_call_cycle_location_handler)
call_cycles_bp.route('/<uuid:call_cycle_id>/locations/<uuid:location_id>', methods=['DELETE'])(remove_call_cycle_location_handler)
call_cycles_bp.route('/<uuid:call_cycle_id>/locations/<uuid:location_id>/order', methods=['PUT'])(update_call_cycle_location_order_handler)
call_cycles_bp.route('/<uuid:call_cycle_id>/status', methods=['GET'])(get_call_cycle_status_handler)