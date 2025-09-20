import pytest
import uuid
from datetime import date


def test_create_goal_as_admin(client, admin_headers, tenant):
    """Test creating a goal as admin."""
    # Create goal
    response = client.post('/api/goals', json={
        'name': 'Test Goal',
        'metric': 'visits',
        'target_value': 100,
        'period': 'weekly',
        'start_date': str(date.today()),
        'end_date': str(date.today().replace(day=date.today().day + 7))
    }, headers=admin_headers)
    
    # Check response
    assert response.status_code == 201
    assert 'id' in response.json
    assert response.json['name'] == 'Test Goal'
    assert response.json['metric'] == 'visits'
    assert response.json['target_value'] == 100
    assert response.json['period'] == 'weekly'
    assert response.json['tenant_id'] == str(tenant.id)
    
    # Check that goal can be retrieved
    goal_id = response.json['id']
    get_response = client.get(f'/api/goals/{goal_id}', headers=admin_headers)
    assert get_response.status_code == 200
    assert get_response.json['name'] == 'Test Goal'


def test_create_goal_as_manager(client, db_session, tenant):
    """Test creating a goal as manager."""
    # Create a manager user
    from services.auth_service import create_user
    manager = create_user(
        db_session,
        tenant.id,
        'manager@example.com',
        'Password123',
        'Regional',
        'Manager',
        '+1234567890',
        ['regional_manager']
    )
    
    # Login as manager
    login_response = client.post('/api/auth/login', json={
        'email': 'manager@example.com',
        'password': 'Password123'
    })
    manager_headers = {
        'Authorization': f"Bearer {login_response.json['access_token']}"
    }
    
    # Create goal as manager
    response = client.post('/api/goals', json={
        'name': 'Manager Goal',
        'metric': 'shelf_share',
        'target_value': 25.5,
        'period': 'monthly',
        'start_date': str(date.today()),
        'end_date': str(date.today().replace(month=date.today().month + 1))
    }, headers=manager_headers)
    
    # Check response
    assert response.status_code == 201
    assert 'id' in response.json
    assert response.json['name'] == 'Manager Goal'
    assert response.json['metric'] == 'shelf_share'
    assert response.json['target_value'] == 25.5
    assert response.json['period'] == 'monthly'
    assert response.json['tenant_id'] == str(tenant.id)


def test_create_goal_as_agent(client, agent_headers):
    """Test creating a goal as agent (should be forbidden)."""
    # Create goal as agent
    response = client.post('/api/goals', json={
        'name': 'Agent Goal',
        'metric': 'visits',
        'target_value': 50,
        'period': 'daily'
    }, headers=agent_headers)
    
    # Check response
    assert response.status_code == 403
    assert 'error' in response.json


def test_get_goals(client, admin_headers, db_session, tenant):
    """Test getting goals."""
    # Create some goals
    from models.goal import Goal
    goal1 = Goal(
        tenant_id=tenant.id,
        name='Goal 1',
        metric='visits',
        target_value=100,
        period='weekly',
        start_date=date.today(),
        end_date=date.today().replace(day=date.today().day + 7)
    )
    goal2 = Goal(
        tenant_id=tenant.id,
        name='Goal 2',
        metric='conversions',
        target_value=50,
        period='monthly',
        start_date=date.today(),
        end_date=date.today().replace(month=date.today().month + 1)
    )
    db_session.add(goal1)
    db_session.add(goal2)
    db_session.commit()
    
    # Get goals
    response = client.get('/api/goals', headers=admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'goals' in response.json
    assert len(response.json['goals']) >= 2
    
    # Check that goals belong to the correct tenant
    for goal in response.json['goals']:
        assert goal['tenant_id'] == str(tenant.id)
    
    # Check that created goals are in the list
    goal_names = [g['name'] for g in response.json['goals']]
    assert 'Goal 1' in goal_names
    assert 'Goal 2' in goal_names


def test_get_goals_as_agent(client, agent_headers, db_session, tenant):
    """Test getting goals as agent."""
    # Create some goals
    from models.goal import Goal
    goal1 = Goal(
        tenant_id=tenant.id,
        name='Goal 3',
        metric='visits',
        target_value=100,
        period='weekly',
        start_date=date.today(),
        end_date=date.today().replace(day=date.today().day + 7)
    )
    goal2 = Goal(
        tenant_id=tenant.id,
        name='Goal 4',
        metric='conversions',
        target_value=50,
        period='monthly',
        start_date=date.today(),
        end_date=date.today().replace(month=date.today().month + 1)
    )
    db_session.add(goal1)
    db_session.add(goal2)
    db_session.commit()
    
    # Get goals as agent
    response = client.get('/api/goals', headers=agent_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'goals' in response.json
    
    # Check that goals belong to the correct tenant
    for goal in response.json['goals']:
        assert goal['tenant_id'] == str(tenant.id)


def test_get_goal_by_id(client, admin_headers, db_session, tenant):
    """Test getting a goal by ID."""
    # Create a goal
    from models.goal import Goal
    goal = Goal(
        tenant_id=tenant.id,
        name='Test Goal Get',
        metric='visits',
        target_value=100,
        period='weekly',
        start_date=date.today(),
        end_date=date.today().replace(day=date.today().day + 7)
    )
    db_session.add(goal)
    db_session.commit()
    
    # Get goal by ID
    response = client.get(f'/api/goals/{goal.id}', headers=admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'id' in response.json
    assert response.json['id'] == str(goal.id)
    assert response.json['name'] == 'Test Goal Get'
    assert response.json['metric'] == 'visits'
    assert response.json['target_value'] == 100
    assert response.json['period'] == 'weekly'
    assert response.json['tenant_id'] == str(tenant.id)


def test_get_goal_by_id_not_found(client, admin_headers):
    """Test getting a non-existent goal."""
    # Get non-existent goal
    random_id = uuid.uuid4()
    response = client.get(f'/api/goals/{random_id}', headers=admin_headers)
    
    # Check response
    assert response.status_code == 404
    assert 'error' in response.json


def test_update_goal_as_admin(client, admin_headers, db_session, tenant):
    """Test updating a goal as admin."""
    # Create a goal
    from models.goal import Goal
    goal = Goal(
        tenant_id=tenant.id,
        name='Goal to Update',
        metric='visits',
        target_value=100,
        period='weekly',
        start_date=date.today(),
        end_date=date.today().replace(day=date.today().day + 7)
    )
    db_session.add(goal)
    db_session.commit()
    
    # Update goal
    response = client.put(f'/api/goals/{goal.id}', json={
        'name': 'Updated Goal',
        'metric': 'conversions',
        'target_value': 50,
        'period': 'monthly',
        'start_date': str(date.today()),
        'end_date': str(date.today().replace(month=date.today().month + 1))
    }, headers=admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert response.json['name'] == 'Updated Goal'
    assert response.json['metric'] == 'conversions'
    assert response.json['target_value'] == 50
    assert response.json['period'] == 'monthly'
    
    # Check that goal was updated
    get_response = client.get(f'/api/goals/{goal.id}', headers=admin_headers)
    assert get_response.status_code == 200
    assert get_response.json['name'] == 'Updated Goal'
    assert get_response.json['metric'] == 'conversions'
    assert get_response.json['target_value'] == 50
    assert get_response.json['period'] == 'monthly'


def test_update_goal_as_agent(client, agent_headers, db_session, tenant):
    """Test updating a goal as agent (should be forbidden)."""
    # Create a goal
    from models.goal import Goal
    goal = Goal(
        tenant_id=tenant.id,
        name='Goal for Agent Update Test',
        metric='visits',
        target_value=100,
        period='weekly',
        start_date=date.today(),
        end_date=date.today().replace(day=date.today().day + 7)
    )
    db_session.add(goal)
    db_session.commit()
    
    # Update goal as agent
    response = client.put(f'/api/goals/{goal.id}', json={
        'name': 'Agent Updated Goal',
        'target_value': 50
    }, headers=agent_headers)
    
    # Check response
    assert response.status_code == 403
    assert 'error' in response.json


def test_assign_goal_to_user(client, admin_headers, db_session, tenant, agent_user):
    """Test assigning a goal to a user."""
    # Create a goal
    from models.goal import Goal
    goal = Goal(
        tenant_id=tenant.id,
        name='Goal for User Assignment',
        metric='visits',
        target_value=100,
        period='weekly',
        start_date=date.today(),
        end_date=date.today().replace(day=date.today().day + 7)
    )
    db_session.add(goal)
    db_session.commit()
    
    # Assign goal to user
    response = client.post(f'/api/goals/{goal.id}/assign', json={
        'assignee_type': 'user',
        'assignee_id': str(agent_user.id)
    }, headers=admin_headers)
    
    # Check response
    assert response.status_code == 201
    assert 'id' in response.json
    assert response.json['goal_id'] == str(goal.id)
    assert response.json['assignee_type'] == 'user'
    assert response.json['assignee_id'] == str(agent_user.id)
    
    # Get goal assignments
    get_response = client.get(f'/api/goals/{goal.id}/assignments', headers=admin_headers)
    assert get_response.status_code == 200
    assert 'assignments' in get_response.json
    assert len(get_response.json['assignments']) >= 1
    
    # Check that assignment is in the list
    assignment_ids = [a['assignee_id'] for a in get_response.json['assignments'] if a['assignee_type'] == 'user']
    assert str(agent_user.id) in assignment_ids


def test_assign_goal_to_team(client, admin_headers, db_session, tenant, admin_user):
    """Test assigning a goal to a team."""
    # Create a goal
    from models.goal import Goal
    goal = Goal(
        tenant_id=tenant.id,
        name='Goal for Team Assignment',
        metric='conversions',
        target_value=50,
        period='monthly',
        start_date=date.today(),
        end_date=date.today().replace(month=date.today().month + 1)
    )
    db_session.add(goal)
    db_session.commit()
    
    # Create a team
    from models.team import Team
    team = Team(tenant_id=tenant.id, name='Team for Goal Assignment', manager_id=admin_user.id)
    db_session.add(team)
    db_session.commit()
    
    # Assign goal to team
    response = client.post(f'/api/goals/{goal.id}/assign', json={
        'assignee_type': 'team',
        'assignee_id': str(team.id)
    }, headers=admin_headers)
    
    # Check response
    assert response.status_code == 201
    assert 'id' in response.json
    assert response.json['goal_id'] == str(goal.id)
    assert response.json['assignee_type'] == 'team'
    assert response.json['assignee_id'] == str(team.id)
    
    # Get goal assignments
    get_response = client.get(f'/api/goals/{goal.id}/assignments', headers=admin_headers)
    assert get_response.status_code == 200
    assert 'assignments' in get_response.json
    assert len(get_response.json['assignments']) >= 1
    
    # Check that assignment is in the list
    assignment_ids = [a['assignee_id'] for a in get_response.json['assignments'] if a['assignee_type'] == 'team']
    assert str(team.id) in assignment_ids


def test_assign_goal_as_agent(client, agent_headers, db_session, tenant, admin_user):
    """Test assigning a goal as agent (should be forbidden)."""
    # Create a goal
    from models.goal import Goal
    goal = Goal(
        tenant_id=tenant.id,
        name='Goal for Agent Assignment Test',
        metric='visits',
        target_value=100,
        period='weekly',
        start_date=date.today(),
        end_date=date.today().replace(day=date.today().day + 7)
    )
    db_session.add(goal)
    db_session.commit()
    
    # Create a team
    from models.team import Team
    team = Team(tenant_id=tenant.id, name='Team for Agent Goal Assignment', manager_id=admin_user.id)
    db_session.add(team)
    db_session.commit()
    
    # Assign goal to team as agent
    response = client.post(f'/api/goals/{goal.id}/assign', json={
        'assignee_type': 'team',
        'assignee_id': str(team.id)
    }, headers=agent_headers)
    
    # Check response
    assert response.status_code == 403
    assert 'error' in response.json


def test_get_goal_progress(client, admin_headers, db_session, tenant, agent_user):
    """Test getting goal progress."""
    # Create a goal
    from models.goal import Goal
    goal = Goal(
        tenant_id=tenant.id,
        name='Goal for Progress',
        metric='visits',
        target_value=100,
        period='weekly',
        start_date=date.today(),
        end_date=date.today().replace(day=date.today().day + 7)
    )
    db_session.add(goal)
    db_session.commit()
    
    # Create a goal assignment
    from models.goal import GoalAssignment
    assignment = GoalAssignment(
        goal_id=goal.id,
        assignee_type='user',
        assignee_id=agent_user.id,
        progress={'current_value': 25, 'percentage': 25.0}
    )
    db_session.add(assignment)
    db_session.commit()
    
    # Get goal progress
    response = client.get(f'/api/goals/{goal.id}/progress', headers=admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'progress' in response.json
    assert 'assignments' in response.json['progress']
    assert len(response.json['progress']['assignments']) >= 1
    
    # Check that assignment progress is in the response
    for assignment in response.json['progress']['assignments']:
        if assignment['assignee_type'] == 'user' and assignment['assignee_id'] == str(agent_user.id):
            assert assignment['progress']['current_value'] == 25
            assert assignment['progress']['percentage'] == 25.0
            break
    else:
        assert False, "Assignment progress not found in response"