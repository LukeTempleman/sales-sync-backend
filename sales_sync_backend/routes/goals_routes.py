from flask import Blueprint

from controllers.goals_controller import (
    get_goals_handler,
    get_goal_handler,
    create_goal_handler,
    update_goal_handler,
    delete_goal_handler,
    get_goal_assignments_handler,
    assign_goal_handler,
    unassign_goal_handler,
    update_goal_progress_handler,
    get_goal_progress_handler
)

# Create blueprint
goals_bp = Blueprint('goals', __name__, url_prefix='/api/goals')

# Register routes
goals_bp.route('', methods=['GET'])(get_goals_handler)
goals_bp.route('', methods=['POST'])(create_goal_handler)
goals_bp.route('/<uuid:goal_id>', methods=['GET'])(get_goal_handler)
goals_bp.route('/<uuid:goal_id>', methods=['PUT'])(update_goal_handler)
goals_bp.route('/<uuid:goal_id>', methods=['DELETE'])(delete_goal_handler)
goals_bp.route('/<uuid:goal_id>/assignments', methods=['GET'])(get_goal_assignments_handler)
goals_bp.route('/<uuid:goal_id>/assign', methods=['POST'])(assign_goal_handler)
goals_bp.route('/<uuid:goal_id>/unassign/<string:assignee_type>/<uuid:assignee_id>', methods=['DELETE'])(unassign_goal_handler)
goals_bp.route('/<uuid:goal_id>/progress/<string:assignee_type>/<uuid:assignee_id>', methods=['PUT'])(update_goal_progress_handler)
goals_bp.route('/<uuid:goal_id>/progress', methods=['GET'])(get_goal_progress_handler)