import pytest
import uuid
import json


def test_create_visit(client, agent_headers, db_session, tenant, agent_user):
    """Test creating a visit."""
    # Create a survey
    from models.survey import Survey
    survey = Survey(tenant_id=tenant.id, name='Visit Survey', type='individual', active=True)
    db_session.add(survey)
    db_session.commit()
    
    # Create visit
    response = client.post('/api/visits', json={
        'survey_id': str(survey.id),
        'visit_type': 'individual',
        'geocode': {'type': 'Point', 'coordinates': [10.0, 20.0]}
    }, headers=agent_headers)
    
    # Check response
    assert response.status_code == 201
    assert 'id' in response.json
    assert response.json['survey_id'] == str(survey.id)
    assert response.json['visit_type'] == 'individual'
    assert response.json['user_id'] == str(agent_user.id)
    assert response.json['tenant_id'] == str(tenant.id)
    assert 'started_at' in response.json
    assert response.json['completed_at'] is None


def test_complete_visit(client, agent_headers, db_session, tenant, agent_user):
    """Test completing a visit."""
    # Create a survey and question
    from models.survey import Survey
    from models.question import SurveyQuestion
    survey = Survey(tenant_id=tenant.id, name='Complete Visit Survey', type='individual', active=True)
    db_session.add(survey)
    db_session.commit()
    
    question = SurveyQuestion(
        tenant_id=tenant.id,
        survey_id=survey.id,
        question_text='Test Question',
        input_type='text',
        meta={'help_text': 'Help text'},
        order_num=1
    )
    db_session.add(question)
    db_session.commit()
    
    # Create a visit
    from models.visit import Visit
    visit = Visit(
        tenant_id=tenant.id,
        survey_id=survey.id,
        user_id=agent_user.id,
        visit_type='individual',
        geocode='POINT(10 20)'
    )
    db_session.add(visit)
    db_session.commit()
    
    # Complete visit
    response = client.put(f'/api/visits/{visit.id}/complete', json={
        'answers': [
            {
                'question_id': str(question.id),
                'answer_text': 'Test Answer'
            }
        ],
        'photos': []
    }, headers=agent_headers)
    
    # Check response
    assert response.status_code == 200
    assert response.json['id'] == str(visit.id)
    assert response.json['completed_at'] is not None
    
    # Check that visit is marked as completed
    get_response = client.get(f'/api/visits/{visit.id}', headers=agent_headers)
    assert get_response.status_code == 200
    assert get_response.json['completed_at'] is not None
    
    # Check that answers were saved
    assert 'answers' in get_response.json
    assert len(get_response.json['answers']) == 1
    assert get_response.json['answers'][0]['question_id'] == str(question.id)
    assert get_response.json['answers'][0]['answer_text'] == 'Test Answer'


def test_complete_visit_as_other_user(client, admin_headers, db_session, tenant, agent_user):
    """Test completing a visit as another user (should be forbidden)."""
    # Create a survey
    from models.survey import Survey
    survey = Survey(tenant_id=tenant.id, name='Other User Visit Survey', type='individual', active=True)
    db_session.add(survey)
    db_session.commit()
    
    # Create a visit for agent
    from models.visit import Visit
    visit = Visit(
        tenant_id=tenant.id,
        survey_id=survey.id,
        user_id=agent_user.id,
        visit_type='individual',
        geocode='POINT(10 20)'
    )
    db_session.add(visit)
    db_session.commit()
    
    # Complete visit as admin
    response = client.put(f'/api/visits/{visit.id}/complete', json={
        'answers': [],
        'photos': []
    }, headers=admin_headers)
    
    # Check response
    assert response.status_code == 403
    assert 'error' in response.json


def test_get_visits_as_agent(client, agent_headers, db_session, tenant, agent_user):
    """Test getting visits as agent."""
    # Create some visits
    from models.visit import Visit
    visit1 = Visit(
        tenant_id=tenant.id,
        survey_id=uuid.uuid4(),  # Dummy ID
        user_id=agent_user.id,
        visit_type='individual',
        geocode='POINT(10 20)'
    )
    visit2 = Visit(
        tenant_id=tenant.id,
        survey_id=uuid.uuid4(),  # Dummy ID
        user_id=agent_user.id,
        visit_type='shop',
        geocode='POINT(30 40)'
    )
    db_session.add(visit1)
    db_session.add(visit2)
    db_session.commit()
    
    # Get visits as agent
    response = client.get('/api/visits', headers=agent_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'visits' in response.json
    assert len(response.json['visits']) >= 2
    
    # Check that visits belong to the agent
    for visit in response.json['visits']:
        assert visit['user_id'] == str(agent_user.id)
        assert visit['tenant_id'] == str(tenant.id)


def test_get_visits_as_admin(client, admin_headers, db_session, tenant, agent_user, admin_user):
    """Test getting visits as admin."""
    # Create some visits for agent
    from models.visit import Visit
    visit1 = Visit(
        tenant_id=tenant.id,
        survey_id=uuid.uuid4(),  # Dummy ID
        user_id=agent_user.id,
        visit_type='individual',
        geocode='POINT(10 20)'
    )
    visit2 = Visit(
        tenant_id=tenant.id,
        survey_id=uuid.uuid4(),  # Dummy ID
        user_id=admin_user.id,
        visit_type='shop',
        geocode='POINT(30 40)'
    )
    db_session.add(visit1)
    db_session.add(visit2)
    db_session.commit()
    
    # Get visits as admin
    response = client.get('/api/visits', headers=admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'visits' in response.json
    assert len(response.json['visits']) >= 2
    
    # Check that visits belong to the tenant
    for visit in response.json['visits']:
        assert visit['tenant_id'] == str(tenant.id)
    
    # Admin should see visits from all users in the tenant
    user_ids = [visit['user_id'] for visit in response.json['visits']]
    assert str(agent_user.id) in user_ids
    assert str(admin_user.id) in user_ids


def test_get_visit_by_id(client, agent_headers, db_session, tenant, agent_user):
    """Test getting a visit by ID."""
    # Create a survey
    from models.survey import Survey
    survey = Survey(tenant_id=tenant.id, name='Get Visit Survey', type='individual', active=True)
    db_session.add(survey)
    db_session.commit()
    
    # Create a visit
    from models.visit import Visit
    visit = Visit(
        tenant_id=tenant.id,
        survey_id=survey.id,
        user_id=agent_user.id,
        visit_type='individual',
        geocode='POINT(10 20)'
    )
    db_session.add(visit)
    db_session.commit()
    
    # Get visit by ID
    response = client.get(f'/api/visits/{visit.id}', headers=agent_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'id' in response.json
    assert response.json['id'] == str(visit.id)
    assert response.json['survey_id'] == str(survey.id)
    assert response.json['user_id'] == str(agent_user.id)
    assert response.json['visit_type'] == 'individual'
    assert response.json['tenant_id'] == str(tenant.id)


def test_get_visit_by_id_as_other_user(client, admin_headers, db_session, tenant, agent_user):
    """Test getting a visit by ID as another user."""
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
    
    # Get visit by ID as admin
    response = client.get(f'/api/visits/{visit.id}', headers=admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'id' in response.json
    assert response.json['id'] == str(visit.id)
    
    # Admin should be able to see agent's visit
    assert response.json['user_id'] == str(agent_user.id)


def test_get_visit_by_id_not_found(client, agent_headers):
    """Test getting a non-existent visit."""
    # Get non-existent visit
    random_id = uuid.uuid4()
    response = client.get(f'/api/visits/{random_id}', headers=agent_headers)
    
    # Check response
    assert response.status_code == 404
    assert 'error' in response.json


def test_get_visit_photos(client, agent_headers, db_session, tenant, agent_user):
    """Test getting photos for a visit."""
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
    
    # Create some photos for the visit
    from models.photo import Photo
    photo1 = Photo(
        tenant_id=tenant.id,
        visit_id=visit.id,
        file_url='https://example.com/photo1.jpg',
        purpose='id'
    )
    photo2 = Photo(
        tenant_id=tenant.id,
        visit_id=visit.id,
        file_url='https://example.com/photo2.jpg',
        purpose='shelf'
    )
    db_session.add(photo1)
    db_session.add(photo2)
    db_session.commit()
    
    # Get photos for visit
    response = client.get(f'/api/visits/{visit.id}/photos', headers=agent_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'photos' in response.json
    assert len(response.json['photos']) == 2
    
    # Check that photos belong to the visit
    for photo in response.json['photos']:
        assert photo['visit_id'] == str(visit.id)
        assert photo['tenant_id'] == str(tenant.id)
    
    # Check that created photos are in the list
    photo_urls = [p['file_url'] for p in response.json['photos']]
    assert 'https://example.com/photo1.jpg' in photo_urls
    assert 'https://example.com/photo2.jpg' in photo_urls