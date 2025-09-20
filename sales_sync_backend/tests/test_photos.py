import pytest
import uuid
import json


def test_upload_photo(client, agent_headers, db_session, tenant, agent_user):
    """Test uploading a photo."""
    # Create a visit
    from models.visit import Visit
    visit = Visit(
        tenant_id=tenant.id,
        survey_id=uuid.uuid4(),  # Dummy ID
        user_id=agent_user.id,
        visit_type='individual',
        geocode='POINT(10 20)'
    )
    db_session.add(visit)
    db_session.commit()
    
    # Upload photo
    response = client.post('/api/photos', json={
        'visit_id': str(visit.id),
        'file_url': 'https://example.com/photo.jpg',
        'purpose': 'shelf',
        'metadata': {'width': 800, 'height': 600}
    }, headers=agent_headers)
    
    # Check response
    assert response.status_code == 201
    assert 'id' in response.json
    assert response.json['visit_id'] == str(visit.id)
    assert response.json['file_url'] == 'https://example.com/photo.jpg'
    assert response.json['purpose'] == 'shelf'
    assert response.json['metadata'] == {'width': 800, 'height': 600}
    assert response.json['tenant_id'] == str(tenant.id)


def test_upload_photo_for_other_user_visit(client, admin_headers, db_session, tenant, agent_user):
    """Test uploading a photo for another user's visit (should be forbidden)."""
    # Create a visit for agent
    from models.visit import Visit
    visit = Visit(
        tenant_id=tenant.id,
        survey_id=uuid.uuid4(),  # Dummy ID
        user_id=agent_user.id,
        visit_type='individual',
        geocode='POINT(10 20)'
    )
    db_session.add(visit)
    db_session.commit()
    
    # Upload photo as admin
    response = client.post('/api/photos', json={
        'visit_id': str(visit.id),
        'file_url': 'https://example.com/admin-photo.jpg',
        'purpose': 'id'
    }, headers=admin_headers)
    
    # Check response
    assert response.status_code == 403
    assert 'error' in response.json


def test_get_photo_by_id(client, agent_headers, db_session, tenant, agent_user):
    """Test getting a photo by ID."""
    # Create a visit
    from models.visit import Visit
    visit = Visit(
        tenant_id=tenant.id,
        survey_id=uuid.uuid4(),  # Dummy ID
        user_id=agent_user.id,
        visit_type='individual',
        geocode='POINT(10 20)'
    )
    db_session.add(visit)
    db_session.commit()
    
    # Create a photo
    from models.photo import Photo
    photo = Photo(
        tenant_id=tenant.id,
        visit_id=visit.id,
        file_url='https://example.com/test-photo.jpg',
        purpose='shelf',
        metadata={'width': 800, 'height': 600}
    )
    db_session.add(photo)
    db_session.commit()
    
    # Get photo by ID
    response = client.get(f'/api/photos/{photo.id}', headers=agent_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'id' in response.json
    assert response.json['id'] == str(photo.id)
    assert response.json['visit_id'] == str(visit.id)
    assert response.json['file_url'] == 'https://example.com/test-photo.jpg'
    assert response.json['purpose'] == 'shelf'
    assert response.json['metadata'] == {'width': 800, 'height': 600}
    assert response.json['tenant_id'] == str(tenant.id)


def test_get_photo_by_id_as_admin(client, admin_headers, db_session, tenant, agent_user):
    """Test getting a photo by ID as admin."""
    # Create a visit for agent
    from models.visit import Visit
    visit = Visit(
        tenant_id=tenant.id,
        survey_id=uuid.uuid4(),  # Dummy ID
        user_id=agent_user.id,
        visit_type='individual',
        geocode='POINT(10 20)'
    )
    db_session.add(visit)
    db_session.commit()
    
    # Create a photo
    from models.photo import Photo
    photo = Photo(
        tenant_id=tenant.id,
        visit_id=visit.id,
        file_url='https://example.com/admin-test-photo.jpg',
        purpose='id'
    )
    db_session.add(photo)
    db_session.commit()
    
    # Get photo by ID as admin
    response = client.get(f'/api/photos/{photo.id}', headers=admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'id' in response.json
    assert response.json['id'] == str(photo.id)
    
    # Admin should be able to see agent's photo
    assert response.json['visit_id'] == str(visit.id)


def test_get_photo_by_id_not_found(client, agent_headers):
    """Test getting a non-existent photo."""
    # Get non-existent photo
    random_id = uuid.uuid4()
    response = client.get(f'/api/photos/{random_id}', headers=agent_headers)
    
    # Check response
    assert response.status_code == 404
    assert 'error' in response.json


def test_submit_shelf_quadrants(client, agent_headers, db_session, tenant, agent_user):
    """Test submitting shelf quadrants for a photo."""
    # Create a visit
    from models.visit import Visit
    visit = Visit(
        tenant_id=tenant.id,
        survey_id=uuid.uuid4(),  # Dummy ID
        user_id=agent_user.id,
        visit_type='individual',
        geocode='POINT(10 20)'
    )
    db_session.add(visit)
    db_session.commit()
    
    # Create a photo
    from models.photo import Photo
    photo = Photo(
        tenant_id=tenant.id,
        visit_id=visit.id,
        file_url='https://example.com/shelf-photo.jpg',
        purpose='shelf'
    )
    db_session.add(photo)
    db_session.commit()
    
    # Create a brand
    from models.brand import Brand
    brand = Brand(tenant_id=tenant.id, name='Test Brand', slug='test-brand')
    db_session.add(brand)
    db_session.commit()
    
    # Submit shelf quadrants
    response = client.post(f'/api/photos/{photo.id}/shelf_quadrants', json={
        'brand_id': str(brand.id),
        'quadrant_coords': [
            {'x': 10, 'y': 10, 'width': 100, 'height': 50},
            {'x': 200, 'y': 150, 'width': 80, 'height': 30}
        ],
        'area_percentage': 25.5
    }, headers=agent_headers)
    
    # Check response
    assert response.status_code == 201
    assert 'id' in response.json
    assert response.json['photo_id'] == str(photo.id)
    assert response.json['brand_id'] == str(brand.id)
    assert response.json['quadrant_coords'] == [
        {'x': 10, 'y': 10, 'width': 100, 'height': 50},
        {'x': 200, 'y': 150, 'width': 80, 'height': 30}
    ]
    assert response.json['area_percentage'] == 25.5
    assert response.json['tenant_id'] == str(tenant.id)


def test_submit_shelf_quadrants_for_other_user_photo(client, admin_headers, db_session, tenant, agent_user):
    """Test submitting shelf quadrants for another user's photo (should be forbidden)."""
    # Create a visit for agent
    from models.visit import Visit
    visit = Visit(
        tenant_id=tenant.id,
        survey_id=uuid.uuid4(),  # Dummy ID
        user_id=agent_user.id,
        visit_type='individual',
        geocode='POINT(10 20)'
    )
    db_session.add(visit)
    db_session.commit()
    
    # Create a photo
    from models.photo import Photo
    photo = Photo(
        tenant_id=tenant.id,
        visit_id=visit.id,
        file_url='https://example.com/agent-shelf-photo.jpg',
        purpose='shelf'
    )
    db_session.add(photo)
    db_session.commit()
    
    # Create a brand
    from models.brand import Brand
    brand = Brand(tenant_id=tenant.id, name='Another Brand', slug='another-brand')
    db_session.add(brand)
    db_session.commit()
    
    # Submit shelf quadrants as admin
    response = client.post(f'/api/photos/{photo.id}/shelf_quadrants', json={
        'brand_id': str(brand.id),
        'quadrant_coords': [{'x': 10, 'y': 10, 'width': 100, 'height': 50}],
        'area_percentage': 15.0
    }, headers=admin_headers)
    
    # Check response
    assert response.status_code == 403
    assert 'error' in response.json