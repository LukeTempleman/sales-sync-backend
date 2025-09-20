import pytest
import uuid


def test_get_tenants_as_super_admin(client, db_session, tenant):
    """Test getting tenants as super_admin."""
    # Create a super_admin user
    from services.auth_service import create_user
    super_admin = create_user(
        db_session,
        None,  # No tenant for super_admin
        'superadmin@example.com',
        'Password123',
        'Super',
        'Admin',
        '+1234567890',
        ['super_admin']
    )
    
    # Login as super_admin
    login_response = client.post('/api/auth/login', json={
        'email': 'superadmin@example.com',
        'password': 'Password123'
    })
    super_admin_headers = {
        'Authorization': f"Bearer {login_response.json['access_token']}"
    }
    
    # Get tenants as super_admin
    response = client.get('/api/tenants', headers=super_admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'tenants' in response.json
    assert len(response.json['tenants']) >= 1  # At least one tenant
    
    # Check that the created tenant is in the list
    tenant_ids = [t['id'] for t in response.json['tenants']]
    assert str(tenant.id) in tenant_ids


def test_get_tenants_as_admin(client, admin_headers):
    """Test getting tenants as admin (should be forbidden)."""
    # Get tenants as admin
    response = client.get('/api/tenants', headers=admin_headers)
    
    # Check response
    assert response.status_code == 403
    assert 'error' in response.json


def test_get_tenant_by_id_as_super_admin(client, db_session, tenant):
    """Test getting a tenant by ID as super_admin."""
    # Create a super_admin user
    from services.auth_service import create_user
    super_admin = create_user(
        db_session,
        None,  # No tenant for super_admin
        'superadmin2@example.com',
        'Password123',
        'Super',
        'Admin',
        '+1234567890',
        ['super_admin']
    )
    
    # Login as super_admin
    login_response = client.post('/api/auth/login', json={
        'email': 'superadmin2@example.com',
        'password': 'Password123'
    })
    super_admin_headers = {
        'Authorization': f"Bearer {login_response.json['access_token']}"
    }
    
    # Get tenant by ID
    response = client.get(f'/api/tenants/{tenant.id}', headers=super_admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'id' in response.json
    assert response.json['id'] == str(tenant.id)
    assert response.json['name'] == tenant.name


def test_get_tenant_by_id_as_admin(client, admin_headers, tenant):
    """Test getting own tenant by ID as admin."""
    # Get own tenant by ID
    response = client.get(f'/api/tenants/{tenant.id}', headers=admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'id' in response.json
    assert response.json['id'] == str(tenant.id)
    assert response.json['name'] == tenant.name


def test_get_tenant_by_id_as_admin_other(client, admin_headers, db_session):
    """Test getting another tenant by ID as admin (should be forbidden)."""
    # Create another tenant
    from services.auth_service import create_tenant
    other_tenant = create_tenant(db_session, 'Other Tenant', 'other')
    
    # Get another tenant by ID
    response = client.get(f'/api/tenants/{other_tenant.id}', headers=admin_headers)
    
    # Check response
    assert response.status_code == 403
    assert 'error' in response.json


def test_get_tenant_by_id_not_found(client, db_session):
    """Test getting a non-existent tenant."""
    # Create a super_admin user
    from services.auth_service import create_user
    super_admin = create_user(
        db_session,
        None,  # No tenant for super_admin
        'superadmin3@example.com',
        'Password123',
        'Super',
        'Admin',
        '+1234567890',
        ['super_admin']
    )
    
    # Login as super_admin
    login_response = client.post('/api/auth/login', json={
        'email': 'superadmin3@example.com',
        'password': 'Password123'
    })
    super_admin_headers = {
        'Authorization': f"Bearer {login_response.json['access_token']}"
    }
    
    # Get non-existent tenant
    random_id = uuid.uuid4()
    response = client.get(f'/api/tenants/{random_id}', headers=super_admin_headers)
    
    # Check response
    assert response.status_code == 404
    assert 'error' in response.json


def test_create_tenant_as_super_admin(client, db_session):
    """Test creating a tenant as super_admin."""
    # Create a super_admin user
    from services.auth_service import create_user
    super_admin = create_user(
        db_session,
        None,  # No tenant for super_admin
        'superadmin4@example.com',
        'Password123',
        'Super',
        'Admin',
        '+1234567890',
        ['super_admin']
    )
    
    # Login as super_admin
    login_response = client.post('/api/auth/login', json={
        'email': 'superadmin4@example.com',
        'password': 'Password123'
    })
    super_admin_headers = {
        'Authorization': f"Bearer {login_response.json['access_token']}"
    }
    
    # Create tenant
    response = client.post('/api/tenants', json={
        'name': 'New Tenant',
        'subdomain': 'new'
    }, headers=super_admin_headers)
    
    # Check response
    assert response.status_code == 201
    assert 'id' in response.json
    assert response.json['name'] == 'New Tenant'
    assert response.json['subdomain'] == 'new'
    
    # Check that tenant can be retrieved
    tenant_id = response.json['id']
    get_response = client.get(f'/api/tenants/{tenant_id}', headers=super_admin_headers)
    assert get_response.status_code == 200
    assert get_response.json['name'] == 'New Tenant'


def test_create_tenant_as_admin(client, admin_headers):
    """Test creating a tenant as admin (should be forbidden)."""
    # Create tenant as admin
    response = client.post('/api/tenants', json={
        'name': 'Another Tenant',
        'subdomain': 'another'
    }, headers=admin_headers)
    
    # Check response
    assert response.status_code == 403
    assert 'error' in response.json


def test_update_tenant_as_super_admin(client, db_session, tenant):
    """Test updating a tenant as super_admin."""
    # Create a super_admin user
    from services.auth_service import create_user
    super_admin = create_user(
        db_session,
        None,  # No tenant for super_admin
        'superadmin5@example.com',
        'Password123',
        'Super',
        'Admin',
        '+1234567890',
        ['super_admin']
    )
    
    # Login as super_admin
    login_response = client.post('/api/auth/login', json={
        'email': 'superadmin5@example.com',
        'password': 'Password123'
    })
    super_admin_headers = {
        'Authorization': f"Bearer {login_response.json['access_token']}"
    }
    
    # Update tenant
    response = client.put(f'/api/tenants/{tenant.id}', json={
        'name': 'Updated Tenant',
        'subdomain': 'updated'
    }, headers=super_admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert response.json['name'] == 'Updated Tenant'
    assert response.json['subdomain'] == 'updated'
    
    # Check that tenant was updated
    get_response = client.get(f'/api/tenants/{tenant.id}', headers=super_admin_headers)
    assert get_response.status_code == 200
    assert get_response.json['name'] == 'Updated Tenant'
    assert get_response.json['subdomain'] == 'updated'


def test_update_tenant_as_admin(client, admin_headers, tenant):
    """Test updating own tenant as admin."""
    # Update own tenant
    response = client.put(f'/api/tenants/{tenant.id}', json={
        'name': 'Admin Updated Tenant',
        'subdomain': 'admin-updated'
    }, headers=admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert response.json['name'] == 'Admin Updated Tenant'
    assert response.json['subdomain'] == 'admin-updated'
    
    # Check that tenant was updated
    get_response = client.get(f'/api/tenants/{tenant.id}', headers=admin_headers)
    assert get_response.status_code == 200
    assert get_response.json['name'] == 'Admin Updated Tenant'
    assert get_response.json['subdomain'] == 'admin-updated'


def test_update_tenant_as_admin_other(client, admin_headers, db_session):
    """Test updating another tenant as admin (should be forbidden)."""
    # Create another tenant
    from services.auth_service import create_tenant
    other_tenant = create_tenant(db_session, 'Other Tenant', 'other')
    
    # Update another tenant
    response = client.put(f'/api/tenants/{other_tenant.id}', json={
        'name': 'Hacked Tenant',
        'subdomain': 'hacked'
    }, headers=admin_headers)
    
    # Check response
    assert response.status_code == 403
    assert 'error' in response.json