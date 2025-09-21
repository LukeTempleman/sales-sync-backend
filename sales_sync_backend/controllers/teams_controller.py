from flask import request, current_app, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from services.team_service import (
    get_teams,
    get_team_by_id,
    create_team,
    update_team,
    get_team_members,
    add_team_member,
    remove_team_member
)
from utils.auth_decorators import admin_required, area_manager_required, team_leader_required, tenant_required
from utils.request_utils import get_tenant_id_from_jwt


@jwt_required()
@tenant_required
def get_teams_handler():
    """
    Get teams for the current tenant.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get filters from query params
    filters = {}
    if request.args.get('name'):
        filters['name'] = request.args.get('name')
    if request.args.get('manager_id'):
        filters['manager_id'] = request.args.get('manager_id')
    
    # Get teams
    teams = get_teams(current_app.db_session, tenant_id, filters)
    
    # Return teams
    return jsonify([team.to_dict() for team in teams]), 200


@jwt_required()
@tenant_required
def get_team_handler(team_id):
    """
    Get team by ID.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get team
    team = get_team_by_id(current_app.db_session, tenant_id, team_id)
    if not team:
        return jsonify({'error': 'Team not found'}), 404
    
    # Return team
    return jsonify(team.to_dict()), 200


@jwt_required()
@admin_required
@area_manager_required
def create_team_handler():
    """
    Create a new team.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get request data
    data = request.get_json()
    
    # Validate request data
    if not data.get('name'):
        return jsonify({'error': 'Team name is required'}), 400
    
    # Create team
    team = create_team(
        current_app.db_session,
        tenant_id,
        data.get('name'),
        data.get('manager_id')
    )
    
    # Return team
    return jsonify(team.to_dict()), 201


@jwt_required()
@admin_required
@area_manager_required
def update_team_handler(team_id):
    """
    Update a team.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get request data
    data = request.get_json()
    
    # Update team
    team = update_team(current_app.db_session, tenant_id, team_id, data)
    if not team:
        return jsonify({'error': 'Team not found'}), 404
    
    # Return team
    return jsonify(team.to_dict()), 200


@jwt_required()
@tenant_required
def get_team_members_handler(team_id):
    """
    Get members of a team.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get team
    team = get_team_by_id(current_app.db_session, tenant_id, team_id)
    if not team:
        return jsonify({'error': 'Team not found'}), 404
    
    # Get team members
    members = get_team_members(current_app.db_session, tenant_id, team_id)
    
    # Return team members
    return jsonify([member.to_dict() for member in members]), 200


@jwt_required()
@admin_required
@team_leader_required
def add_team_member_handler(team_id):
    """
    Add a user to a team.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get team
    team = get_team_by_id(current_app.db_session, tenant_id, team_id)
    if not team:
        return jsonify({'error': 'Team not found'}), 404
    
    # Get request data
    data = request.get_json()
    
    # Validate request data
    if not data.get('user_id'):
        return jsonify({'error': 'User ID is required'}), 400
    
    # Add user to team
    user_team = add_team_member(
        current_app.db_session,
        team_id,
        data.get('user_id')
    )
    
    # Return success
    return jsonify({'message': 'User added to team successfully'}), 201


@jwt_required()
@admin_required
@team_leader_required
def remove_team_member_handler(team_id, user_id):
    """
    Remove a user from a team.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get team
    team = get_team_by_id(current_app.db_session, tenant_id, team_id)
    if not team:
        return jsonify({'error': 'Team not found'}), 404
    
    # Remove user from team
    success = remove_team_member(
        current_app.db_session,
        team_id,
        user_id
    )
    
    if not success:
        return jsonify({'error': 'User is not a member of this team'}), 404
    
    # Return success
    return jsonify({'message': 'User removed from team successfully'}), 200