pleasimport pytest
import uuid


def test_get_brands(client, admin_headers, db_session, tenant):
    """Test getting brands."""
    # Create some brands
    from models.brand import Brand
    brand1 = Brand(tenant_id=tenant.id, name='Brand 1', slug='brand-1')
    brand2 = Brand(tenant_id=tenant.id, name='Brand 2', slug='brand-2')
    db_session.add(brand1)
    db_session.add(brand2)
    db_session.commit()
    
    # Get brands
    response = client.get('/api/brands', headers=admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'brands' in response.json
    assert len(response.json['brands']) >= 2
    
    # Check that brands belong to the correct tenant
    for brand in response.json['brands']:
        assert brand['tenant_id'] == str(tenant.id)
    
    # Check that created brands are in the list
    brand_names = [b['name'] for b in response.json['brands']]
    assert 'Brand 1' in brand_names
    assert 'Brand 2' in brand_names


def test_get_brands_as_agent(client, agent_headers, db_session, tenant):
    """Test getting brands as agent."""
    # Create some brands
    from models.brand import Brand
    brand1 = Brand(tenant_id=tenant.id, name='Brand 3', slug='brand-3')
    brand2 = Brand(tenant_id=tenant.id, name='Brand 4', slug='brand-4')
    db_session.add(brand1)
    db_session.add(brand2)
    db_session.commit()
    
    # Get brands as agent
    response = client.get('/api/brands', headers=agent_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'brands' in response.json
    
    # Check that brands belong to the correct tenant
    for brand in response.json['brands']:
        assert brand['tenant_id'] == str(tenant.id)


def test_get_brand_by_id(client, admin_headers, db_session, tenant):
    """Test getting a brand by ID."""
    # Create a brand
    from models.brand import Brand
    brand = Brand(tenant_id=tenant.id, name='Test Brand', slug='test-brand')
    db_session.add(brand)
    db_session.commit()
    
    # Get brand by ID
    response = client.get(f'/api/brands/{brand.id}', headers=admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'id' in response.json
    assert response.json['id'] == str(brand.id)
    assert response.json['name'] == 'Test Brand'
    assert response.json['slug'] == 'test-brand'
    assert response.json['tenant_id'] == str(tenant.id)


def test_get_brand_by_id_not_found(client, admin_headers):
    """Test getting a non-existent brand."""
    # Get non-existent brand
    random_id = uuid.uuid4()
    response = client.get(f'/api/brands/{random_id}', headers=admin_headers)
    
    # Check response
    assert response.status_code == 404
    assert 'error' in response.json


def test_create_brand_as_admin(client, admin_headers, tenant):
    """Test creating a brand as admin."""
    # Create brand
    response = client.post('/api/brands', json={
        'name': 'New Brand',
        'slug': 'new-brand'
    }, headers=admin_headers)
    
    # Check response
    assert response.status_code == 201
    assert 'id' in response.json
    assert response.json['name'] == 'New Brand'
    assert response.json['slug'] == 'new-brand'
    assert response.json['tenant_id'] == str(tenant.id)
    
    # Check that brand can be retrieved
    brand_id = response.json['id']
    get_response = client.get(f'/api/brands/{brand_id}', headers=admin_headers)
    assert get_response.status_code == 200
    assert get_response.json['name'] == 'New Brand'


def test_create_brand_as_agent(client, agent_headers):
    """Test creating a brand as agent (should be forbidden)."""
    # Create brand as agent
    response = client.post('/api/brands', json={
        'name': 'Agent Brand',
        'slug': 'agent-brand'
    }, headers=agent_headers)
    
    # Check response
    assert response.status_code == 403
    assert 'error' in response.json


def test_update_brand_as_admin(client, admin_headers, db_session, tenant):
    """Test updating a brand as admin."""
    # Create a brand
    from models.brand import Brand
    brand = Brand(tenant_id=tenant.id, name='Brand to Update', slug='brand-to-update')
    db_session.add(brand)
    db_session.commit()
    
    # Update brand
    response = client.put(f'/api/brands/{brand.id}', json={
        'name': 'Updated Brand',
        'slug': 'updated-brand'
    }, headers=admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert response.json['name'] == 'Updated Brand'
    assert response.json['slug'] == 'updated-brand'
    
    # Check that brand was updated
    get_response = client.get(f'/api/brands/{brand.id}', headers=admin_headers)
    assert get_response.status_code == 200
    assert get_response.json['name'] == 'Updated Brand'
    assert get_response.json['slug'] == 'updated-brand'


def test_update_brand_as_agent(client, agent_headers, db_session, tenant):
    """Test updating a brand as agent (should be forbidden)."""
    # Create a brand
    from models.brand import Brand
    brand = Brand(tenant_id=tenant.id, name='Brand for Agent Test', slug='brand-agent-test')
    db_session.add(brand)
    db_session.commit()
    
    # Update brand as agent
    response = client.put(f'/api/brands/{brand.id}', json={
        'name': 'Agent Updated Brand',
        'slug': 'agent-updated-brand'
    }, headers=agent_headers)
    
    # Check response
    assert response.status_code == 403
    assert 'error' in response.json


def test_delete_brand_as_admin(client, admin_headers, db_session, tenant):
    """Test deleting a brand as admin."""
    # Create a brand
    from models.brand import Brand
    brand = Brand(tenant_id=tenant.id, name='Brand to Delete', slug='brand-to-delete')
    db_session.add(brand)
    db_session.commit()
    
    # Delete brand
    response = client.delete(f'/api/brands/{brand.id}', headers=admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'message' in response.json
    
    # Check that brand is deleted
    get_response = client.get(f'/api/brands/{brand.id}', headers=admin_headers)
    assert get_response.status_code == 404


def test_delete_brand_as_agent(client, agent_headers, db_session, tenant):
    """Test deleting a brand as agent (should be forbidden)."""
    # Create a brand
    from models.brand import Brand
    brand = Brand(tenant_id=tenant.id, name='Brand for Agent Delete Test', slug='brand-agent-delete')
    db_session.add(brand)
    db_session.commit()
    
    # Delete brand as agent
    response = client.delete(f'/api/brands/{brand.id}', headers=agent_headers)
    
    # Check response
    assert response.status_code == 403
    assert 'error' in response.json


def test_upload_infographic(client, admin_headers, db_session, tenant):
    """Test uploading an infographic for a brand."""
    # Create a brand
    from models.brand import Brand
    brand = Brand(tenant_id=tenant.id, name='Brand with Infographic', slug='brand-infographic')
    db_session.add(brand)
    db_session.commit()
    
    # Upload infographic
    response = client.post(f'/api/brands/{brand.id}/infographics', json={
        'file_url': 'https://example.com/image.jpg',
        'caption': 'Test Infographic'
    }, headers=admin_headers)
    
    # Check response
    assert response.status_code == 201
    assert 'id' in response.json
    assert response.json['file_url'] == 'https://example.com/image.jpg'
    assert response.json['caption'] == 'Test Infographic'
    assert response.json['brand_id'] == str(brand.id)
    
    # Get infographics for brand
    get_response = client.get(f'/api/brands/{brand.id}/infographics', headers=admin_headers)
    assert get_response.status_code == 200
    assert 'infographics' in get_response.json
    assert len(get_response.json['infographics']) >= 1
    
    # Check that uploaded infographic is in the list
    infographic_captions = [i['caption'] for i in get_response.json['infographics']]
    assert 'Test Infographic' in infographic_captions


def test_upload_infographic_as_agent(client, agent_headers, db_session, tenant):
    """Test uploading an infographic as agent (should be forbidden)."""
    # Create a brand
    from models.brand import Brand
    brand = Brand(tenant_id=tenant.id, name='Brand for Agent Infographic', slug='brand-agent-infographic')
    db_session.add(brand)
    db_session.commit()
    
    # Upload infographic as agent
    response = client.post(f'/api/brands/{brand.id}/infographics', json={
        'file_url': 'https://example.com/agent-image.jpg',
        'caption': 'Agent Infographic'
    }, headers=agent_headers)
    
    # Check response
    assert response.status_code == 403
    assert 'error' in response.json