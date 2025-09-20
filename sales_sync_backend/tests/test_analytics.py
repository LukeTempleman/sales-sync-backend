import pytest
import uuid
from datetime import datetime, timedelta


def test_get_analytics_overview_as_admin(client, admin_headers, db_session, tenant, admin_user, agent_user):
    """Test getting analytics overview as admin."""
    # Create some visits
    from models.visit import Visit
    visit1 = Visit(
        tenant_id=tenant.id,
        survey_id=uuid.uuid4(),  # Dummy ID
        user_id=agent_user.id,
        visit_type='individual',
        geocode='POINT(10 20)',
        started_at=datetime.now() - timedelta(days=1),
        completed_at=datetime.now() - timedelta(days=1) + timedelta(hours=1)
    )
    visit2 = Visit(
        tenant_id=tenant.id,
        survey_id=uuid.uuid4(),  # Dummy ID
        user_id=agent_user.id,
        visit_type='shop',
        geocode='POINT(30 40)',
        started_at=datetime.now() - timedelta(days=2),
        completed_at=datetime.now() - timedelta(days=2) + timedelta(hours=1)
    )
    db_session.add(visit1)
    db_session.add(visit2)
    db_session.commit()
    
    # Get analytics overview
    response = client.get('/api/analytics/overview', headers=admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'metrics' in response.json
    assert 'visits' in response.json['metrics']
    assert 'conversions' in response.json['metrics']
    assert 'shelf_share' in response.json['metrics']
    
    # Check that visits count is correct
    assert response.json['metrics']['visits']['total'] >= 2


def test_get_analytics_overview_as_agent(client, agent_headers, db_session, tenant, agent_user):
    """Test getting analytics overview as agent."""
    # Create some visits
    from models.visit import Visit
    visit1 = Visit(
        tenant_id=tenant.id,
        survey_id=uuid.uuid4(),  # Dummy ID
        user_id=agent_user.id,
        visit_type='individual',
        geocode='POINT(10 20)',
        started_at=datetime.now() - timedelta(days=1),
        completed_at=datetime.now() - timedelta(days=1) + timedelta(hours=1)
    )
    visit2 = Visit(
        tenant_id=tenant.id,
        survey_id=uuid.uuid4(),  # Dummy ID
        user_id=agent_user.id,
        visit_type='shop',
        geocode='POINT(30 40)',
        started_at=datetime.now() - timedelta(days=2),
        completed_at=datetime.now() - timedelta(days=2) + timedelta(hours=1)
    )
    db_session.add(visit1)
    db_session.add(visit2)
    db_session.commit()
    
    # Get analytics overview as agent
    response = client.get('/api/analytics/overview', headers=agent_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'metrics' in response.json
    assert 'visits' in response.json['metrics']
    
    # Agent should only see their own metrics
    assert response.json['metrics']['visits']['total'] >= 2


def test_get_visits_analytics(client, admin_headers, db_session, tenant, agent_user):
    """Test getting visits analytics."""
    # Create some visits on different days
    from models.visit import Visit
    visit1 = Visit(
        tenant_id=tenant.id,
        survey_id=uuid.uuid4(),  # Dummy ID
        user_id=agent_user.id,
        visit_type='individual',
        geocode='POINT(10 20)',
        started_at=datetime.now() - timedelta(days=1),
        completed_at=datetime.now() - timedelta(days=1) + timedelta(hours=1)
    )
    visit2 = Visit(
        tenant_id=tenant.id,
        survey_id=uuid.uuid4(),  # Dummy ID
        user_id=agent_user.id,
        visit_type='shop',
        geocode='POINT(30 40)',
        started_at=datetime.now() - timedelta(days=2),
        completed_at=datetime.now() - timedelta(days=2) + timedelta(hours=1)
    )
    visit3 = Visit(
        tenant_id=tenant.id,
        survey_id=uuid.uuid4(),  # Dummy ID
        user_id=agent_user.id,
        visit_type='individual',
        geocode='POINT(50 60)',
        started_at=datetime.now() - timedelta(days=3),
        completed_at=datetime.now() - timedelta(days=3) + timedelta(hours=1)
    )
    db_session.add(visit1)
    db_session.add(visit2)
    db_session.add(visit3)
    db_session.commit()
    
    # Get visits analytics
    response = client.get('/api/analytics/visits', headers=admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'data' in response.json
    assert 'time_series' in response.json['data']
    assert len(response.json['data']['time_series']) > 0
    
    # Check that time series has data for different days
    dates = [entry['date'] for entry in response.json['data']['time_series']]
    assert len(set(dates)) >= 3


def test_get_visits_analytics_with_filters(client, admin_headers, db_session, tenant, agent_user):
    """Test getting visits analytics with filters."""
    # Create some visits on different days with different types
    from models.visit import Visit
    visit1 = Visit(
        tenant_id=tenant.id,
        survey_id=uuid.uuid4(),  # Dummy ID
        user_id=agent_user.id,
        visit_type='individual',
        geocode='POINT(10 20)',
        started_at=datetime.now() - timedelta(days=1),
        completed_at=datetime.now() - timedelta(days=1) + timedelta(hours=1)
    )
    visit2 = Visit(
        tenant_id=tenant.id,
        survey_id=uuid.uuid4(),  # Dummy ID
        user_id=agent_user.id,
        visit_type='shop',
        geocode='POINT(30 40)',
        started_at=datetime.now() - timedelta(days=2),
        completed_at=datetime.now() - timedelta(days=2) + timedelta(hours=1)
    )
    db_session.add(visit1)
    db_session.add(visit2)
    db_session.commit()
    
    # Get visits analytics filtered by visit_type
    response = client.get('/api/analytics/visits?visit_type=individual', headers=admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'data' in response.json
    assert 'time_series' in response.json['data']
    
    # Check that only individual visits are included
    total_visits = sum(entry['count'] for entry in response.json['data']['time_series'])
    assert total_visits >= 1


def test_get_shelf_share_analytics(client, admin_headers, db_session, tenant, agent_user):
    """Test getting shelf share analytics."""
    # Create a visit
    from models.visit import Visit
    visit = Visit(
        tenant_id=tenant.id,
        survey_id=uuid.uuid4(),  # Dummy ID
        user_id=agent_user.id,
        visit_type='shop',
        geocode='POINT(10 20)',
        started_at=datetime.now() - timedelta(days=1),
        completed_at=datetime.now() - timedelta(days=1) + timedelta(hours=1)
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
    
    # Create some brands
    from models.brand import Brand
    brand1 = Brand(tenant_id=tenant.id, name='Brand 1', slug='brand-1')
    brand2 = Brand(tenant_id=tenant.id, name='Brand 2', slug='brand-2')
    db_session.add(brand1)
    db_session.add(brand2)
    db_session.commit()
    
    # Create shelf quadrants
    from models.shelf_quadrant import ShelfQuadrant
    quadrant1 = ShelfQuadrant(
        tenant_id=tenant.id,
        photo_id=photo.id,
        brand_id=brand1.id,
        quadrant_coords=[{'x': 10, 'y': 10, 'width': 100, 'height': 50}],
        area_percentage=60.0
    )
    quadrant2 = ShelfQuadrant(
        tenant_id=tenant.id,
        photo_id=photo.id,
        brand_id=brand2.id,
        quadrant_coords=[{'x': 200, 'y': 10, 'width': 100, 'height': 50}],
        area_percentage=40.0
    )
    db_session.add(quadrant1)
    db_session.add(quadrant2)
    db_session.commit()
    
    # Get shelf share analytics
    response = client.get('/api/analytics/shelf_share', headers=admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'data' in response.json
    assert 'brands' in response.json['data']
    assert len(response.json['data']['brands']) >= 2
    
    # Check that brands have correct percentages
    brand_percentages = {brand['name']: brand['percentage'] for brand in response.json['data']['brands']}
    assert brand_percentages.get('Brand 1') == 60.0
    assert brand_percentages.get('Brand 2') == 40.0


def test_get_call_cycle_coverage(client, admin_headers, db_session, tenant, admin_user, agent_user):
    """Test getting call cycle coverage."""
    # Create a call cycle
    from models.call_cycle import CallCycle
    call_cycle = CallCycle(
        tenant_id=tenant.id,
        name='Call Cycle for Coverage',
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
        geocode='POINT(10 20)',  # Same as location1
        started_at=datetime.now() - timedelta(days=1),
        completed_at=datetime.now() - timedelta(days=1) + timedelta(hours=1)
    )
    db_session.add(visit)
    db_session.commit()
    
    # Get call cycle coverage
    response = client.get('/api/analytics/call_cycle_coverage', headers=admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'data' in response.json
    assert 'heatmap' in response.json['data']
    assert 'coverage' in response.json['data']
    
    # Check that coverage percentage is correct (1 out of 2 locations visited)
    assert response.json['data']['coverage']['percentage'] == 50.0
    
    # Check that heatmap has data
    assert len(response.json['data']['heatmap']) >= 2
    
    # Check that visited location has higher weight
    for point in response.json['data']['heatmap']:
        if (float(point['lat']), float(point['lng'])) == (20.0, 10.0):  # Note: lat/lng are reversed from POINT(x y)
            assert point['weight'] > 0