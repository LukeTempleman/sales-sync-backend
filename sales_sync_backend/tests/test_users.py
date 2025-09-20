import pytest
import uuid


def test_get_users_as_admin(client, admin_headers, tenant, admin_user, agent_user):
    """Test getting users as admin."""
    # Get users as admin
    response = client.get('/api/users', headers=admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'users' in response.json
    assert len(response.json['users']) >= 2  # At least admin and agent users
    
    # Check that users belong to the correct tenant
    for user in response.json['users']:
        assert user['tenant_id'] == str(tenant.id)


def test_get_users_as_agent(client, agent_headers):
    """Test getting users as agent (should be forbidden)."""
    # Get users as agent
    response = client.get('/api/users', headers=agent_headers)
    
    # Check response
    assert response.status_code == 403
    assert 'error' in response.json


def test_get_user_by_id_as_admin(client, admin_headers, admin_user):
    """Test getting a user by ID as admin."""
    # Get user by ID
    response = client.get(f'/api/users/{admin_user.id}', headers=admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'id' in response.json
    assert response.json['id'] == str(admin_user.id)
    assert response.json['email'] == admin_user.email


def test_get_user_by_id_as_agent_self(client, agent_headers, agent_user):
    """Test getting own user profile as agent."""
    # Get own user profile
    response = client.get(f'/api/users/{agent_user.id}', headers=agent_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'id' in response.json
    assert response.json['id'] == str(agent_user.id)
    assert response.json['email'] == agent_user.email


def test_get_user_by_id_as_agent_other(client, agent_headers, admin_user):
    """Test getting another user's profile as agent (should be forbidden)."""
    # Get another user's profile
    response = client.get(f'/api/users/{admin_user.id}', headers=agent_headers)
    
    # Check response
    assert response.status_code == 403
    assert 'error' in response.json


def test_get_user_by_id_not_found(client, admin_headers):
    """Test getting a non-existent user."""
    # Get non-existent user
    random_id = uuid.uuid4()
    response = client.get(f'/api/users/{random_id}', headers=admin_headers)
    
    # Check response
    assert response.status_code == 404
    assert 'error' in response.json


def test_create_user_as_admin(client, admin_headers, tenant):
    """Test creating a user as admin."""
    # Create user
    response = client.post('/api/users', json={
        'email': 'newuser@example.com',
        'password': 'Password123',
        'first_name': 'New',
        'last_name': 'User',
        'phone': '+1234567890',
        'roles': ['agent']
    }, headers=admin_headers)
    
    # Check response
    assert response.status_code == 201
    assert 'id' in response.json
    assert response.json['email'] == 'newuser@example.com'
    assert response.json['first_name'] == 'New'
    assert response.json['last_name'] == 'User'
    assert response.json['tenant_id'] == str(tenant.id)
    
    # Check that user can be retrieved
    user_id = response.json['id']
    get_response = client.get(f'/api/users/{user_id}', headers=admin_headers)
    assert get_response.status_code == 200
    assert get_response.json['email'] == 'newuser@example.com'


def test_create_user_as_agent(client, agent_headers):
    """Test creating a user as agent (should be forbidden)."""
    # Create user as agent
    response = client.post('/api/users', json={
        'email': 'anotheruser@example.com',
        'password': 'Password123',
        'first_name': 'Another',
        'last_name': 'User',
        'phone': '+1234567890',
        'roles': ['agent']
    }, headers=agent_headers)
    
    # Check response
    assert response.status_code == 403
    assert 'error' in response.json


def test_update_user_as_admin(client, admin_headers, agent_user):
    """Test updating a user as admin."""
    # Update user
    response = client.put(f'/api/users/{agent_user.id}', json={
        'first_name': 'Updated',
        'last_name': 'Agent',
        'phone': '+9876543210'
    }, headers=admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert response.json['first_name'] == 'Updated'
    assert response.json['last_name'] == 'Agent'
    assert response.json['phone'] == '+9876543210'
    
    # Check that user was updated
    get_response = client.get(f'/api/users/{agent_user.id}', headers=admin_headers)
    assert get_response.status_code == 200
    assert get_response.json['first_name'] == 'Updated'
    assert get_response.json['last_name'] == 'Agent'
    assert get_response.json['phone'] == '+9876543210'


def test_update_user_as_agent_self(client, agent_headers, agent_user):
    """Test updating own user profile as agent."""
    # Update own profile
    response = client.put(f'/api/users/{agent_user.id}', json={
        'first_name': 'Self',
        'last_name': 'Updated',
        'phone': '+1122334455'
    }, headers=agent_headers)
    
    # Check response
    assert response.status_code == 200
    assert response.json['first_name'] == 'Self'
    assert response.json['last_name'] == 'Updated'
    assert response.json['phone'] == '+1122334455'


def test_update_user_as_agent_other(client, agent_headers, admin_user):
    """Test updating another user's profile as agent (should be forbidden)."""
    # Update another user's profile
    response = client.put(f'/api/users/{admin_user.id}', json={
        'first_name': 'Hacked',
        'last_name': 'Admin'
    }, headers=agent_headers)
    
    # Check response
    assert response.status_code == 403
    assert 'error' in response.json


def test_delete_user_as_admin(client, admin_headers, db_session, tenant):
    """Test deleting a user as admin."""
    # Create a user to delete
    from services.auth_service import create_user
    user_to_delete = create_user(
        db_session,
        tenant.id,
        'todelete@example.com',
        'Password123',
        'To',
        'Delete',
        '+1234567890',
        ['agent']
    )
    
    # Delete user
    response = client.delete(f'/api/users/{user_to_delete.id}', headers=admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'message' in response.json
    
    # Check that user is deleted or deactivated
    get_response = client.get(f'/api/users/{user_to_delete.id}', headers=admin_headers)
    if get_response.status_code == 200:
        # If soft delete, user should be marked as inactive
        assert get_response.json['is_active'] is False
    else:
        # If hard delete, user should not be found
        assert get_response.status_code == 404


def test_delete_user_as_agent(client, agent_headers, admin_user):
    """Test deleting a user as agent (should be forbidden)."""
    # Delete user as agent
    response = client.delete(f'/api/users/{admin_user.id}', headers=agent_headers)
    
    # Check response
    assert response.status_code == 403
    assert 'error' in response.json


def test_get_current_user(client, admin_headers, admin_user):
    """Test getting current user profile."""
    # Get current user
    response = client.get('/api/users/me', headers=admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'id' in response.json
    assert response.json['id'] == str(admin_user.id)
    assert response.json['email'] == admin_user.email


def test_assign_roles_as_admin(client, admin_headers, agent_user):
    """Test assigning roles to a user as admin."""
    # Assign roles
    response = client.post(f'/api/users/{agent_user.id}/roles', json={
        'roles': ['agent', 'team_leader']
    }, headers=admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'roles' in response.json
    assert set(response.json['roles']) == {'agent', 'team_leader'}
    
    # Check that roles were assigned
    get_response = client.get(f'/api/users/{agent_user.id}', headers=admin_headers)
    assert get_response.status_code == 200
    assert 'roles' in get_response.json
    assert set(get_response.json['roles']) == {'agent', 'team_leader'}


def test_assign_roles_as_agent(client, agent_headers, admin_user):
    """Test assigning roles as agent (should be forbidden)."""
    # Assign roles as agent
    response = client.post(f'/api/users/{admin_user.id}/roles', json={
        'roles': ['agent']
    }, headers=agent_headers)
    
    # Check response
    assert response.status_code == 403
    assert 'error' in response.json