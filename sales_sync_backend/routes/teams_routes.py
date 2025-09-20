from flask import Blueprint

from controllers.teams_controller import (
    get_teams_handler,
    get_team_handler,
    create_team_handler,
    update_team_handler,
    get_team_members_handler,
    add_team_member_handler,
    remove_team_member_handler
)

# Create blueprint
teams_bp = Blueprint('teams', __name__, url_prefix='/api/teams')

# Register routes
teams_bp.route('', methods=['GET'])(get_teams_handler)
teams_bp.route('', methods=['POST'])(create_team_handler)
teams_bp.route('/<uuid:team_id>', methods=['GET'])(get_team_handler)
teams_bp.route('/<uuid:team_id>', methods=['PUT'])(update_team_handler)
teams_bp.route('/<uuid:team_id>/members', methods=['GET'])(get_team_members_handler)
teams_bp.route('/<uuid:team_id>/members', methods=['POST'])(add_team_member_handler)
teams_bp.route('/<uuid:team_id>/members/<uuid:user_id>', methods=['DELETE'])(remove_team_member_handler)