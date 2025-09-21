from flask import request, current_app, jsonify
from flask_jwt_extended import jwt_required

from services.goal_service import (
    get_goals,
    get_goal_by_id,
    create_goal,
    update_goal,
    delete_goal,
    get_goal_assignments,
    assign_goal,
    unassign_goal,
    update_goal_progress,
    get_goal_progress
)
from utils.auth_decorators import admin_required, manager_required, tenant_required
from utils.request_utils import get_tenant_id_from_jwt


@jwt_required()
@tenant_required
def get_goals_handler():
    """
    Get goals for the current tenant.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get filters from query params
    filters = {}
    if request.args.get('name'):
        filters['name'] = request.args.get('name')
    if request.args.get('metric'):
        filters['metric'] = request.args.get('metric')
    if request.args.get('period'):
        filters['period'] = request.args.get('period')
    if request.args.get('start_date'):
        filters['start_date'] = request.args.get('start_date')
    if request.args.get('end_date'):
        filters['end_date'] = request.args.get('end_date')
    
    # Get goals
    goals = get_goals(current_app.db_session, tenant_id, filters)
    
    # Return goals
    return jsonify([goal.to_dict() for goal in goals]), 200


@jwt_required()
@tenant_required
def get_goal_handler(goal_id):
    """
    Get goal by ID.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get goal
    goal = get_goal_by_id(current_app.db_session, tenant_id, goal_id)
    if not goal:
        return jsonify({'error': 'Goal not found'}), 404
    
    # Return goal
    return jsonify(goal.to_dict()), 200


@jwt_required()
@admin_required
@manager_required
def create_goal_handler():
    """
    Create a new goal.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get request data
    data = request.get_json()
    
    # Validate request data
    if not data.get('name'):
        return jsonify({'error': 'Goal name is required'}), 400
    if not data.get('metric'):
        return jsonify({'error': 'Goal metric is required'}), 400
    if not data.get('target_value'):
        return jsonify({'error': 'Goal target value is required'}), 400
    if not data.get('period'):
        return jsonify({'error': 'Goal period is required'}), 400
    if data.get('period') not in ['daily', 'weekly', 'monthly', 'quarterly']:
        return jsonify({'error': 'Goal period must be "daily", "weekly", "monthly", or "quarterly"'}), 400
    
    # Create goal
    goal = create_goal(
        current_app.db_session,
        tenant_id,
        data.get('name'),
        data.get('metric'),
        data.get('target_value'),
        data.get('period'),
        data.get('start_date'),
        data.get('end_date')
    )
    
    # Return goal
    return jsonify(goal.to_dict()), 201


@jwt_required()
@admin_required
@manager_required
def update_goal_handler(goal_id):
    """
    Update a goal.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get request data
    data = request.get_json()
    
    # Update goal
    goal = update_goal(current_app.db_session, tenant_id, goal_id, data)
    if not goal:
        return jsonify({'error': 'Goal not found'}), 404
    
    # Return goal
    return jsonify(goal.to_dict()), 200


@jwt_required()
@admin_required
@manager_required
def delete_goal_handler(goal_id):
    """
    Delete a goal.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Delete goal
    success = delete_goal(current_app.db_session, tenant_id, goal_id)
    if not success:
        return jsonify({'error': 'Goal not found'}), 404
    
    # Return success
    return jsonify({'message': 'Goal deleted successfully'}), 200


@jwt_required()
@tenant_required
def get_goal_assignments_handler(goal_id):
    """
    Get assignments for a goal.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get goal
    goal = get_goal_by_id(current_app.db_session, tenant_id, goal_id)
    if not goal:
        return jsonify({'error': 'Goal not found'}), 404
    
    # Get goal assignments
    assignments = get_goal_assignments(current_app.db_session, tenant_id, goal_id)
    
    # Return goal assignments
    return jsonify([assignment.to_dict() for assignment in assignments]), 200


@jwt_required()
@admin_required
@manager_required
def assign_goal_handler(goal_id):
    """
    Assign a goal to a user or team.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get goal
    goal = get_goal_by_id(current_app.db_session, tenant_id, goal_id)
    if not goal:
        return jsonify({'error': 'Goal not found'}), 404
    
    # Get request data
    data = request.get_json()
    
    # Validate request data
    if not data.get('assignee_type'):
        return jsonify({'error': 'Assignee type is required'}), 400
    if data.get('assignee_type') not in ['user', 'team']:
        return jsonify({'error': 'Assignee type must be "user" or "team"'}), 400
    if not data.get('assignee_id'):
        return jsonify({'error': 'Assignee ID is required'}), 400
    
    # Assign goal
    assignment = assign_goal(
        current_app.db_session,
        goal_id,
        data.get('assignee_type'),
        data.get('assignee_id'),
        data.get('progress')
    )
    
    # Return goal assignment
    return jsonify(assignment.to_dict()), 201


@jwt_required()
@admin_required
@manager_required
def unassign_goal_handler(goal_id, assignee_type, assignee_id):
    """
    Unassign a goal from a user or team.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get goal
    goal = get_goal_by_id(current_app.db_session, tenant_id, goal_id)
    if not goal:
        return jsonify({'error': 'Goal not found'}), 404
    
    # Unassign goal
    success = unassign_goal(
        current_app.db_session,
        goal_id,
        assignee_type,
        assignee_id
    )
    
    if not success:
        return jsonify({'error': 'Goal assignment not found'}), 404
    
    # Return success
    return jsonify({'message': 'Goal unassigned successfully'}), 200


@jwt_required()
@admin_required
@manager_required
def update_goal_progress_handler(goal_id, assignee_type, assignee_id):
    """
    Update goal progress.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get goal
    goal = get_goal_by_id(current_app.db_session, tenant_id, goal_id)
    if not goal:
        return jsonify({'error': 'Goal not found'}), 404
    
    # Get request data
    data = request.get_json()
    
    # Validate request data
    if not data.get('progress'):
        return jsonify({'error': 'Progress data is required'}), 400
    
    # Update goal progress
    assignment = update_goal_progress(
        current_app.db_session,
        goal_id,
        assignee_type,
        assignee_id,
        data.get('progress')
    )
    
    if not assignment:
        return jsonify({'error': 'Goal assignment not found'}), 404
    
    # Return goal assignment
    return jsonify(assignment.to_dict()), 200


@jwt_required()
@tenant_required
def get_goal_progress_handler(goal_id):
    """
    Get progress for a goal.
    """
    # Get tenant ID from JWT
    tenant_id = get_tenant_id_from_jwt()
    
    # Get goal progress
    progress = get_goal_progress(current_app.db_session, tenant_id, goal_id)
    if not progress:
        return jsonify({'error': 'Goal not found'}), 404
    
    # Return goal progress
    return jsonify(progress), 200