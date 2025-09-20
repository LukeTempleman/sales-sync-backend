import pytest
import uuid


def test_create_call_cycle_as_manager(client, db_session, tenant):
    """Test creating a call cycle as manager."""
    # Create a manager user
    from services.auth_service import create_user
    manager = create_user(
        db_session,
        tenant.id,
        'callcyclemanager@example.com',
        'Password123',
        'Call Cycle',
        'Manager',
        '+1234567890',
        ['regional_manager']
    )
    
    # Login as manager
    login_response = client.post('/api/auth/login', json={
        'email': 'callcyclemanager@example.com',
        'password': 'Password123'
    })
    manager_headers = {
        'Authorization': f"Bearer {login_response.json['access_token']}"
    }
    
    # Create call cycle
    response = client.post('/api/call_cycles', json={
        'name': 'Test Call Cycle',
        'frequency': 'weekly'
    }, headers=manager_headers)
    
    # Check response
    assert response.status_code == 201
    assert 'id' in response.json
    assert response.json['name'] == 'Test Call Cycle'
    assert response.json['frequency'] == 'weekly'
    assert response.json['tenant_id'] == str(tenant.id)
    assert response.json['created_by'] == str(manager.id)
    
    # Check that call cycle can be retrieved
    call_cycle_id = response.json['id']
    get_response = client.get(f'/api/call_cycles/{call_cycle_id}', headers=manager_headers)
    assert get_response.status_code == 200
    assert get_response.json['name'] == 'Test Call Cycle'


def test_create_call_cycle_as_admin(client, admin_headers, tenant, admin_user):
    """Test creating a call cycle as admin."""
    # Create call cycle
    response = client.post('/api/call_cycles', json={
        'name': 'Admin Call Cycle',
        'frequency': 'monthly'
    }, headers=admin_headers)
    
    # Check response
    assert response.status_code == 201
    assert 'id' in response.json
    assert response.json['name'] == 'Admin Call Cycle'
    assert response.json['frequency'] == 'monthly'
    assert response.json['tenant_id'] == str(tenant.id)
    assert response.json['created_by'] == str(admin_user.id)


def test_create_call_cycle_as_agent(client, agent_headers):
    """Test creating a call cycle as agent (should be forbidden)."""
    # Create call cycle as agent
    response = client.post('/api/call_cycles', json={
        'name': 'Agent Call Cycle',
        'frequency': 'daily'
    }, headers=agent_headers)
    
    # Check response
    assert response.status_code == 403
    assert 'error' in response.json


def test_get_call_cycles(client, admin_headers, db_session, tenant, admin_user):
    """Test getting call cycles."""
    # Create some call cycles
    from models.call_cycle import CallCycle
    call_cycle1 = CallCycle(
        tenant_id=tenant.id,
        name='Call Cycle 1',
        frequency='weekly',
        created_by=admin_user.id
    )
    call_cycle2 = CallCycle(
        tenant_id=tenant.id,
        name='Call Cycle 2',
        frequency='monthly',
        created_by=admin_user.id
    )
    db_session.add(call_cycle1)
    db_session.add(call_cycle2)
    db_session.commit()
    
    # Get call cycles
    response = client.get('/api/call_cycles', headers=admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'call_cycles' in response.json
    assert len(response.json['call_cycles']) >= 2
    
    # Check that call cycles belong to the correct tenant
    for call_cycle in response.json['call_cycles']:
        assert call_cycle['tenant_id'] == str(tenant.id)
    
    # Check that created call cycles are in the list
    call_cycle_names = [cc['name'] for cc in response.json['call_cycles']]
    assert 'Call Cycle 1' in call_cycle_names
    assert 'Call Cycle 2' in call_cycle_names


def test_get_call_cycles_as_agent(client, agent_headers, db_session, tenant, admin_user):
    """Test getting call cycles as agent."""
    # Create some call cycles
    from models.call_cycle import CallCycle
    call_cycle1 = CallCycle(
        tenant_id=tenant.id,
        name='Call Cycle 3',
        frequency='weekly',
        created_by=admin_user.id
    )
    call_cycle2 = CallCycle(
        tenant_id=tenant.id,
        name='Call Cycle 4',
        frequency='monthly',
        created_by=admin_user.id
    )
    db_session.add(call_cycle1)
    db_session.add(call_cycle2)
    db_session.commit()
    
    # Get call cycles as agent
    response = client.get('/api/call_cycles', headers=agent_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'call_cycles' in response.json
    
    # Check that call cycles belong to the correct tenant
    for call_cycle in response.json['call_cycles']:
        assert call_cycle['tenant_id'] == str(tenant.id)


def test_get_call_cycle_by_id(client, admin_headers, db_session, tenant, admin_user):
    """Test getting a call cycle by ID."""
    # Create a call cycle
    from models.call_cycle import CallCycle
    call_cycle = CallCycle(
        tenant_id=tenant.id,
        name='Test Call Cycle Get',
        frequency='weekly',
        created_by=admin_user.id
    )
    db_session.add(call_cycle)
    db_session.commit()
    
    # Get call cycle by ID
    response = client.get(f'/api/call_cycles/{call_cycle.id}', headers=admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'id' in response.json
    assert response.json['id'] == str(call_cycle.id)
    assert response.json['name'] == 'Test Call Cycle Get'
    assert response.json['frequency'] == 'weekly'
    assert response.json['tenant_id'] == str(tenant.id)
    assert response.json['created_by'] == str(admin_user.id)


def test_get_call_cycle_by_id_not_found(client, admin_headers):
    """Test getting a non-existent call cycle."""
    # Get non-existent call cycle
    random_id = uuid.uuid4()
    response = client.get(f'/api/call_cycles/{random_id}', headers=admin_headers)
    
    # Check response
    assert response.status_code == 404
    assert 'error' in response.json


def test_update_call_cycle_as_manager(client, db_session, tenant):
    """Test updating a call cycle as manager."""
    # Create a manager user
    from services.auth_service import create_user
    manager = create_user(
        db_session,
        tenant.id,
        'updatemanager@example.com',
        'Password123',
        'Update',
        'Manager',
        '+1234567890',
        ['regional_manager']
    )
    
    # Login as manager
    login_response = client.post('/api/auth/login', json={
        'email': 'updatemanager@example.com',
        'password': 'Password123'
    })
    manager_headers = {
        'Authorization': f"Bearer {login_response.json['access_token']}"
    }
    
    # Create a call cycle
    from models.call_cycle import CallCycle
    call_cycle = CallCycle(
        tenant_id=tenant.id,
        name='Call Cycle to Update',
        frequency='weekly',
        created_by=manager.id
    )
    db_session.add(call_cycle)
    db_session.commit()
    
    # Update call cycle
    response = client.put(f'/api/call_cycles/{call_cycle.id}', json={
        'name': 'Updated Call Cycle',
        'frequency': 'monthly'
    }, headers=manager_headers)
    
    # Check response
    assert response.status_code == 200
    assert response.json['name'] == 'Updated Call Cycle'
    assert response.json['frequency'] == 'monthly'
    
    # Check that call cycle was updated
    get_response = client.get(f'/api/call_cycles/{call_cycle.id}', headers=manager_headers)
    assert get_response.status_code == 200
    assert get_response.json['name'] == 'Updated Call Cycle'
    assert get_response.json['frequency'] == 'monthly'


def test_update_call_cycle_as_agent(client, agent_headers, db_session, tenant, admin_user):
    """Test updating a call cycle as agent (should be forbidden)."""
    # Create a call cycle
    from models.call_cycle import CallCycle
    call_cycle = CallCycle(
        tenant_id=tenant.id,
        name='Call Cycle for Agent Update Test',
        frequency='weekly',
        created_by=admin_user.id
    )
    db_session.add(call_cycle)
    db_session.commit()
    
    # Update call cycle as agent
    response = client.put(f'/api/call_cycles/{call_cycle.id}', json={
        'name': 'Agent Updated Call Cycle',
        'frequency': 'daily'
    }, headers=agent_headers)
    
    # Check response
    assert response.status_code == 403
    assert 'error' in response.json


def test_add_location_to_call_cycle(client, admin_headers, db_session, tenant, admin_user):
    """Test adding a location to a call cycle."""
    # Create a call cycle
    from models.call_cycle import CallCycle
    call_cycle = CallCycle(
        tenant_id=tenant.id,
        name='Call Cycle for Location',
        frequency='weekly',
        created_by=admin_user.id
    )
    db_session.add(call_cycle)
    db_session.commit()
    
    # Add location to call cycle
    response = client.post(f'/api/call_cycles/{call_cycle.id}/locations', json={
        'location': {'type': 'Point', 'coordinates': [10.0, 20.0]},
        'order_num': 1
    }, headers=admin_headers)
    
    # Check response
    assert response.status_code == 201
    assert 'id' in response.json
    assert response.json['call_cycle_id'] == str(call_cycle.id)
    assert response.json['order_num'] == 1
    
    # Get call cycle locations
    get_response = client.get(f'/api/call_cycles/{call_cycle.id}/locations', headers=admin_headers)
    assert get_response.status_code == 200
    assert 'locations' in get_response.json
    assert len(get_response.json['locations']) >= 1


def test_add_location_to_call_cycle_as_agent(client, agent_headers, db_session, tenant, admin_user):
    """Test adding a location to a call cycle as agent (should be forbidden)."""
    # Create a call cycle
    from models.call_cycle import CallCycle
    call_cycle = CallCycle(
        tenant_id=tenant.id,
        name='Call Cycle for Agent Location Test',
        frequency='weekly',
        created_by=admin_user.id
    )
    db_session.add(call_cycle)
    db_session.commit()
    
    # Add location to call cycle as agent
    response = client.post(f'/api/call_cycles/{call_cycle.id}/locations', json={
        'location': {'type': 'Point', 'coordinates': [30.0, 40.0]},
        'order_num': 1
    }, headers=agent_headers)
    
    # Check response
    assert response.status_code == 403
    assert 'error' in response.json


def test_get_call_cycle_status(client, admin_headers, db_session, tenant, admin_user, agent_user):
    """Test getting call cycle status."""
    # Create a call cycle
    from models.call_cycle import CallCycle
    call_cycle = CallCycle(
        tenant_id=tenant.id,
        name='Call Cycle for Status',
        frequency='weekly',
        created_by=admin_user.id
    )
    db_session.add(call_cycle)
    db_session.commit()
    
    # Create some locations
    from models.call_cycle import CallCycleLocation
    location1 = CallCycleLocation(
        call_cycle_id=call_cycle.id,
        location='POINT(10 20)',
        order_num=1
    )
    location2 = CallCycleLocation(
        call_cycle_id=call_cycle.id,
        location='POINT(30 40)',
        order_num=2
    )
    db_session.add(location1)
    db_session.add(location2)
    db_session.commit()
    
    # Create a visit for one of the locations
    from models.visit import Visit
    visit = Visit(
        tenant_id=tenant.id,
        survey_id=uuid.uuid4(),  # Dummy ID
        user_id=agent_user.id,
        visit_type='shop',
        geocode='POINT(10 20)'  # Same as location1
    )
    db_session.add(visit)
    db_session.commit()
    
    # Get call cycle status
    response = client.get(f'/api/call_cycles/{call_cycle.id}/status', headers=admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'status' in response.json
    assert 'adherence' in response.json['status']
    assert 'locations' in response.json['status']
    assert len(response.json['status']['locations']) == 2
    
    # Check that locations are in the response
    location_coords = [
        (float(l['location']['coordinates'][0]), float(l['location']['coordinates'][1]))
        for l in response.json['status']['locations']
    ]
    assert (10.0, 20.0) in location_coords
    assert (30.0, 40.0) in location_coords
    
    # Check that visited location is marked as visited
    for location in response.json['status']['locations']:
        if (float(location['location']['coordinates'][0]), float(location['location']['coordinates'][1])) == (10.0, 20.0):
            assert location['visited'] is True
        else:
            assert location['visited'] is False