from models.team import Team, UserTeam


def get_teams(session, tenant_id, filters=None):
    """
    Get teams for a tenant.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        filters: Optional filters
    
    Returns:
        list: List of teams
    """
    query = session.query(Team).filter(Team.tenant_id == tenant_id)
    
    # Apply filters
    if filters:
        if 'name' in filters:
            query = query.filter(Team.name.ilike(f"%{filters['name']}%"))
        if 'manager_id' in filters:
            query = query.filter(Team.manager_id == filters['manager_id'])
    
    return query.all()


def get_team_by_id(session, tenant_id, team_id):
    """
    Get team by ID.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        team_id: Team ID
    
    Returns:
        Team: Team object or None
    """
    return session.query(Team).filter(
        Team.tenant_id == tenant_id,
        Team.id == team_id
    ).first()


def create_team(session, tenant_id, name, manager_id=None):
    """
    Create a new team.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        name: Team name
        manager_id: Manager ID (optional)
    
    Returns:
        Team: Created team
    """
    team = Team(
        tenant_id=tenant_id,
        name=name,
        manager_id=manager_id
    )
    session.add(team)
    session.commit()
    return team


def update_team(session, tenant_id, team_id, data):
    """
    Update a team.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        team_id: Team ID
        data: Team data to update
    
    Returns:
        Team: Updated team or None
    """
    team = get_team_by_id(session, tenant_id, team_id)
    if not team:
        return None
    
    # Update team fields
    if 'name' in data:
        team.name = data['name']
    if 'manager_id' in data:
        team.manager_id = data['manager_id']
    
    session.commit()
    return team


def get_team_members(session, tenant_id, team_id):
    """
    Get members of a team.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        team_id: Team ID
    
    Returns:
        list: List of users
    """
    from models.user import User
    
    # Get team
    team = get_team_by_id(session, tenant_id, team_id)
    if not team:
        return []
    
    # Get team members
    return session.query(User).join(
        UserTeam, User.id == UserTeam.user_id
    ).filter(
        User.tenant_id == tenant_id,
        UserTeam.team_id == team_id
    ).all()


def add_team_member(session, team_id, user_id):
    """
    Add a user to a team.
    
    Args:
        session: SQLAlchemy session
        team_id: Team ID
        user_id: User ID
    
    Returns:
        UserTeam: Created user-team association
    """
    # Check if user is already in team
    user_team = session.query(UserTeam).filter(
        UserTeam.team_id == team_id,
        UserTeam.user_id == user_id
    ).first()
    
    if user_team:
        return user_team
    
    # Add user to team
    user_team = UserTeam(
        team_id=team_id,
        user_id=user_id
    )
    session.add(user_team)
    session.commit()
    return user_team


def remove_team_member(session, team_id, user_id):
    """
    Remove a user from a team.
    
    Args:
        session: SQLAlchemy session
        team_id: Team ID
        user_id: User ID
    
    Returns:
        bool: True if user was removed, False otherwise
    """
    # Get user-team association
    user_team = session.query(UserTeam).filter(
        UserTeam.team_id == team_id,
        UserTeam.user_id == user_id
    ).first()
    
    if not user_team:
        return False
    
    # Remove user from team
    session.delete(user_team)
    session.commit()
    return True