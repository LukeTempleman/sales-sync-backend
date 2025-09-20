from models.goal import Goal, GoalAssignment


def get_goals(session, tenant_id, filters=None):
    """
    Get goals for a tenant.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        filters: Optional filters
    
    Returns:
        list: List of goals
    """
    query = session.query(Goal).filter(Goal.tenant_id == tenant_id)
    
    # Apply filters
    if filters:
        if 'name' in filters:
            query = query.filter(Goal.name.ilike(f"%{filters['name']}%"))
        if 'metric' in filters:
            query = query.filter(Goal.metric == filters['metric'])
        if 'period' in filters:
            query = query.filter(Goal.period == filters['period'])
        if 'start_date' in filters:
            query = query.filter(Goal.start_date >= filters['start_date'])
        if 'end_date' in filters:
            query = query.filter(Goal.end_date <= filters['end_date'])
    
    return query.all()


def get_goal_by_id(session, tenant_id, goal_id):
    """
    Get goal by ID.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        goal_id: Goal ID
    
    Returns:
        Goal: Goal object or None
    """
    return session.query(Goal).filter(
        Goal.tenant_id == tenant_id,
        Goal.id == goal_id
    ).first()


def create_goal(session, tenant_id, name, metric, target_value, period, start_date=None, end_date=None):
    """
    Create a new goal.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        name: Goal name
        metric: Goal metric ('visits', 'conversions', 'shelf_share', etc.)
        target_value: Target value
        period: Goal period ('daily', 'weekly', 'monthly', 'quarterly')
        start_date: Start date (optional)
        end_date: End date (optional)
    
    Returns:
        Goal: Created goal
    """
    goal = Goal(
        tenant_id=tenant_id,
        name=name,
        metric=metric,
        target_value=target_value,
        period=period,
        start_date=start_date,
        end_date=end_date
    )
    session.add(goal)
    session.commit()
    return goal


def update_goal(session, tenant_id, goal_id, data):
    """
    Update a goal.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        goal_id: Goal ID
        data: Goal data to update
    
    Returns:
        Goal: Updated goal or None
    """
    goal = get_goal_by_id(session, tenant_id, goal_id)
    if not goal:
        return None
    
    # Update goal fields
    if 'name' in data:
        goal.name = data['name']
    if 'metric' in data:
        goal.metric = data['metric']
    if 'target_value' in data:
        goal.target_value = data['target_value']
    if 'period' in data:
        goal.period = data['period']
    if 'start_date' in data:
        goal.start_date = data['start_date']
    if 'end_date' in data:
        goal.end_date = data['end_date']
    
    session.commit()
    return goal


def delete_goal(session, tenant_id, goal_id):
    """
    Delete a goal.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        goal_id: Goal ID
    
    Returns:
        bool: True if goal was deleted, False otherwise
    """
    goal = get_goal_by_id(session, tenant_id, goal_id)
    if not goal:
        return False
    
    session.delete(goal)
    session.commit()
    return True


def get_goal_assignments(session, tenant_id, goal_id):
    """
    Get assignments for a goal.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        goal_id: Goal ID
    
    Returns:
        list: List of goal assignments
    """
    # Get goal
    goal = get_goal_by_id(session, tenant_id, goal_id)
    if not goal:
        return []
    
    # Get goal assignments
    return session.query(GoalAssignment).filter(
        GoalAssignment.goal_id == goal_id
    ).all()


def assign_goal(session, goal_id, assignee_type, assignee_id, progress=None):
    """
    Assign a goal to a user or team.
    
    Args:
        session: SQLAlchemy session
        goal_id: Goal ID
        assignee_type: Assignee type ('user' or 'team')
        assignee_id: Assignee ID
        progress: Progress data (optional)
    
    Returns:
        GoalAssignment: Created goal assignment
    """
    # Check if goal is already assigned to the assignee
    goal_assignment = session.query(GoalAssignment).filter(
        GoalAssignment.goal_id == goal_id,
        GoalAssignment.assignee_type == assignee_type,
        GoalAssignment.assignee_id == assignee_id
    ).first()
    
    if goal_assignment:
        return goal_assignment
    
    # Assign goal
    goal_assignment = GoalAssignment(
        goal_id=goal_id,
        assignee_type=assignee_type,
        assignee_id=assignee_id,
        progress=progress
    )
    session.add(goal_assignment)
    session.commit()
    return goal_assignment


def unassign_goal(session, goal_id, assignee_type, assignee_id):
    """
    Unassign a goal from a user or team.
    
    Args:
        session: SQLAlchemy session
        goal_id: Goal ID
        assignee_type: Assignee type ('user' or 'team')
        assignee_id: Assignee ID
    
    Returns:
        bool: True if goal was unassigned, False otherwise
    """
    # Get goal assignment
    goal_assignment = session.query(GoalAssignment).filter(
        GoalAssignment.goal_id == goal_id,
        GoalAssignment.assignee_type == assignee_type,
        GoalAssignment.assignee_id == assignee_id
    ).first()
    
    if not goal_assignment:
        return False
    
    # Unassign goal
    session.delete(goal_assignment)
    session.commit()
    return True


def update_goal_progress(session, goal_id, assignee_type, assignee_id, progress):
    """
    Update goal progress.
    
    Args:
        session: SQLAlchemy session
        goal_id: Goal ID
        assignee_type: Assignee type ('user' or 'team')
        assignee_id: Assignee ID
        progress: Progress data
    
    Returns:
        GoalAssignment: Updated goal assignment or None
    """
    # Get goal assignment
    goal_assignment = session.query(GoalAssignment).filter(
        GoalAssignment.goal_id == goal_id,
        GoalAssignment.assignee_type == assignee_type,
        GoalAssignment.assignee_id == assignee_id
    ).first()
    
    if not goal_assignment:
        return None
    
    # Update progress
    goal_assignment.progress = progress
    session.commit()
    return goal_assignment


def get_goal_progress(session, tenant_id, goal_id):
    """
    Get progress for a goal.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        goal_id: Goal ID
    
    Returns:
        dict: Goal progress data
    """
    # Get goal
    goal = get_goal_by_id(session, tenant_id, goal_id)
    if not goal:
        return None
    
    # Get goal assignments
    assignments = get_goal_assignments(session, tenant_id, goal_id)
    
    # Calculate progress
    progress_data = {
        'goal': goal.to_dict(),
        'assignments': [assignment.to_dict() for assignment in assignments],
        'overall_progress': calculate_overall_progress(goal, assignments)
    }
    
    return progress_data


def calculate_overall_progress(goal, assignments):
    """
    Calculate overall progress for a goal.
    
    Args:
        goal: Goal object
        assignments: List of goal assignments
    
    Returns:
        float: Overall progress percentage
    """
    # This is a simplified implementation
    # In a real application, this would be more complex
    
    # If there are no assignments, progress is 0
    if not assignments:
        return 0.0
    
    # Calculate progress based on assignment progress
    total_progress = 0.0
    for assignment in assignments:
        if assignment.progress and 'value' in assignment.progress:
            total_progress += float(assignment.progress['value'])
    
    # Calculate average progress
    average_progress = total_progress / len(assignments)
    
    # Calculate percentage of target
    if goal.target_value:
        percentage = (average_progress / float(goal.target_value)) * 100.0
        return min(percentage, 100.0)  # Cap at 100%
    
    return 0.0