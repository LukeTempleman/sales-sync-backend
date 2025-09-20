import pytest
import uuid


def test_create_team_as_admin(client, admin_headers, tenant, admin_user):
    """Test creating a team as admin."""
    # Create team
    response = client.post('/api/teams', json={
        'name': 'Test Team',
        'manager_id': str(admin_user.id)
    }, headers=admin_headers)
    
    # Check response
    assert response.status_code == 201
    assert 'id' in response.json
    assert response.json['name'] == 'Test Team'
    assert response.json['manager_id'] == str(admin_user.id)
    assert response.json['tenant_id'] == str(tenant.id)
    
    # Check that team can be retrieved
    team_id = response.json['id']
    get_response = client.get(f'/api/teams/{team_id}', headers=admin_headers)
    assert get_response.status_code == 200
    assert get_response.json['name'] == 'Test Team'


def test_create_team_as_area_manager(client, db_session, tenant):
    """Test creating a team as area_manager."""
    # Create an area_manager user
    from services.auth_service import create_user
    area_manager = create_user(
        db_session,
        tenant.id,
        'areamanager@example.com',
        'Password123',
        'Area',
        'Manager',
        '+1234567890',
        ['area_manager']
    )
    
    # Login as area_manager
    login_response = client.post('/api/auth/login', json={
        'email': 'areamanager@example.com',
        'password': 'Password123'
    })
    area_manager_headers = {
        'Authorization': f"Bearer {login_response.json['access_token']}"
    }
    
    # Create team as area_manager
    response = client.post('/api/teams', json={
        'name': 'Area Manager Team',
        'manager_id': str(area_manager.id)
    }, headers=area_manager_headers)
    
    # Check response
    assert response.status_code == 201
    assert 'id' in response.json
    assert response.json['name'] == 'Area Manager Team'
    assert response.json['manager_id'] == str(area_manager.id)
    assert response.json['tenant_id'] == str(tenant.id)


def test_create_team_as_agent(client, agent_headers):
    """Test creating a team as agent (should be forbidden)."""
    # Create team as agent
    response = client.post('/api/teams', json={
        'name': 'Agent Team'
    }, headers=agent_headers)
    
    # Check response
    assert response.status_code == 403
    assert 'error' in response.json


def test_get_teams(client, admin_headers, db_session, tenant, admin_user):
    """Test getting teams."""
    # Create some teams
    from models.team import Team
    team1 = Team(tenant_id=tenant.id, name='Team 1', manager_id=admin_user.id)
    team2 = Team(tenant_id=tenant.id, name='Team 2', manager_id=admin_user.id)
    db_session.add(team1)
    db_session.add(team2)
    db_session.commit()
    
    # Get teams
    response = client.get('/api/teams', headers=admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'teams' in response.json
    assert len(response.json['teams']) >= 2
    
    # Check that teams belong to the correct tenant
    for team in response.json['teams']:
        assert team['tenant_id'] == str(tenant.id)
    
    # Check that created teams are in the list
    team_names = [t['name'] for t in response.json['teams']]
    assert 'Team 1' in team_names
    assert 'Team 2' in team_names


def test_get_teams_as_agent(client, agent_headers, db_session, tenant, admin_user):
    """Test getting teams as agent."""
    # Create some teams
    from models.team import Team
    team1 = Team(tenant_id=tenant.id, name='Team 3', manager_id=admin_user.id)
    team2 = Team(tenant_id=tenant.id, name='Team 4', manager_id=admin_user.id)
    db_session.add(team1)
    db_session.add(team2)
    db_session.commit()
    
    # Get teams as agent
    response = client.get('/api/teams', headers=agent_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'teams' in response.json
    
    # Check that teams belong to the correct tenant
    for team in response.json['teams']:
        assert team['tenant_id'] == str(tenant.id)


def test_get_team_by_id(client, admin_headers, db_session, tenant, admin_user):
    """Test getting a team by ID."""
    # Create a team
    from models.team import Team
    team = Team(tenant_id=tenant.id, name='Test Team Get', manager_id=admin_user.id)
    db_session.add(team)
    db_session.commit()
    
    # Get team by ID
    response = client.get(f'/api/teams/{team.id}', headers=admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'id' in response.json
    assert response.json['id'] == str(team.id)
    assert response.json['name'] == 'Test Team Get'
    assert response.json['manager_id'] == str(admin_user.id)
    assert response.json['tenant_id'] == str(tenant.id)


def test_get_team_by_id_not_found(client, admin_headers):
    """Test getting a non-existent team."""
    # Get non-existent team
    random_id = uuid.uuid4()
    response = client.get(f'/api/teams/{random_id}', headers=admin_headers)
    
    # Check response
    assert response.status_code == 404
    assert 'error' in response.json


def test_update_team_as_admin(client, admin_headers, db_session, tenant, admin_user):
    """Test updating a team as admin."""
    # Create a team
    from models.team import Team
    team = Team(tenant_id=tenant.id, name='Team to Update', manager_id=admin_user.id)
    db_session.add(team)
    db_session.commit()
    
    # Update team
    response = client.put(f'/api/teams/{team.id}', json={
        'name': 'Updated Team',
        'manager_id': str(admin_user.id)
    }, headers=admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert response.json['name'] == 'Updated Team'
    assert response.json['manager_id'] == str(admin_user.id)
    
    # Check that team was updated
    get_response = client.get(f'/api/teams/{team.id}', headers=admin_headers)
    assert get_response.status_code == 200
    assert get_response.json['name'] == 'Updated Team'


def test_update_team_as_area_manager(client, db_session, tenant, admin_user):
    """Test updating a team as area_manager."""
    # Create an area_manager user
    from services.auth_service import create_user
    area_manager = create_user(
        db_session,
        tenant.id,
        'areamanager2@example.com',
        'Password123',
        'Area',
        'Manager',
        '+1234567890',
        ['area_manager']
    )
    
    # Login as area_manager
    login_response = client.post('/api/auth/login', json={
        'email': 'areamanager2@example.com',
        'password': 'Password123'
    })
    area_manager_headers = {
        'Authorization': f"Bearer {login_response.json['access_token']}"
    }
    
    # Create a team
    from models.team import Team
    team = Team(tenant_id=tenant.id, name='Area Manager Team to Update', manager_id=area_manager.id)
    db_session.add(team)
    db_session.commit()
    
    # Update team as area_manager
    response = client.put(f'/api/teams/{team.id}', json={
        'name': 'Area Manager Updated Team',
        'manager_id': str(area_manager.id)
    }, headers=area_manager_headers)
    
    # Check response
    assert response.status_code == 200
    assert response.json['name'] == 'Area Manager Updated Team'
    assert response.json['manager_id'] == str(area_manager.id)


def test_update_team_as_agent(client, agent_headers, db_session, tenant, admin_user):
    """Test updating a team as agent (should be forbidden)."""
    # Create a team
    from models.team import Team
    team = Team(tenant_id=tenant.id, name='Team for Agent Update Test', manager_id=admin_user.id)
    db_session.add(team)
    db_session.commit()
    
    # Update team as agent
    response = client.put(f'/api/teams/{team.id}', json={
        'name': 'Agent Updated Team'
    }, headers=agent_headers)
    
    # Check response
    assert response.status_code == 403
    assert 'error' in response.json


def test_add_member_to_team_as_admin(client, admin_headers, db_session, tenant, admin_user, agent_user):
    """Test adding a member to a team as admin."""
    # Create a team
    from models.team import Team
    team = Team(tenant_id=tenant.id, name='Team for Member Test', manager_id=admin_user.id)
    db_session.add(team)
    db_session.commit()
    
    # Add member to team
    response = client.post(f'/api/teams/{team.id}/members', json={
        'user_id': str(agent_user.id)
    }, headers=admin_headers)
    
    # Check response
    assert response.status_code == 201
    assert 'id' in response.json
    assert response.json['user_id'] == str(agent_user.id)
    assert response.json['team_id'] == str(team.id)
    
    # Get team members
    get_response = client.get(f'/api/teams/{team.id}/members', headers=admin_headers)
    assert get_response.status_code == 200
    assert 'members' in get_response.json
    assert len(get_response.json['members']) >= 1
    
    # Check that added member is in the list
    member_ids = [m['user_id'] for m in get_response.json['members']]
    assert str(agent_user.id) in member_ids


def test_add_member_to_team_as_team_leader(client, db_session, tenant, admin_user, agent_user):
    """Test adding a member to a team as team_leader."""
    # Create a team_leader user
    from services.auth_service import create_user
    team_leader = create_user(
        db_session,
        tenant.id,
        'teamleader@example.com',
        'Password123',
        'Team',
        'Leader',
        '+1234567890',
        ['team_leader']
    )
    
    # Login as team_leader
    login_response = client.post('/api/auth/login', json={
        'email': 'teamleader@example.com',
        'password': 'Password123'
    })
    team_leader_headers = {
        'Authorization': f"Bearer {login_response.json['access_token']}"
    }
    
    # Create a team
    from models.team import Team
    team = Team(tenant_id=tenant.id, name='Team Leader Team', manager_id=team_leader.id)
    db_session.add(team)
    db_session.commit()
    
    # Add member to team as team_leader
    response = client.post(f'/api/teams/{team.id}/members', json={
        'user_id': str(agent_user.id)
    }, headers=team_leader_headers)
    
    # Check response
    assert response.status_code == 201
    assert 'id' in response.json
    assert response.json['user_id'] == str(agent_user.id)
    assert response.json['team_id'] == str(team.id)


def test_add_member_to_team_as_agent(client, agent_headers, db_session, tenant, admin_user):
    """Test adding a member to a team as agent (should be forbidden)."""
    # Create a team
    from models.team import Team
    team = Team(tenant_id=tenant.id, name='Team for Agent Member Test', manager_id=admin_user.id)
    db_session.add(team)
    db_session.commit()
    
    # Create another agent
    from services.auth_service import create_user
    another_agent = create_user(
        db_session,
        tenant.id,
        'anotheragent@example.com',
        'Password123',
        'Another',
        'Agent',
        '+1234567890',
        ['agent']
    )
    
    # Add member to team as agent
    response = client.post(f'/api/teams/{team.id}/members', json={
        'user_id': str(another_agent.id)
    }, headers=agent_headers)
    
    # Check response
    assert response.status_code == 403
    assert 'error' in response.json