import pytest
import uuid


def test_get_surveys(client, admin_headers, db_session, tenant):
    """Test getting surveys."""
    # Create some surveys
    from models.survey import Survey
    survey1 = Survey(tenant_id=tenant.id, name='Survey 1', type='individual', active=True)
    survey2 = Survey(tenant_id=tenant.id, name='Survey 2', type='shop', active=True)
    db_session.add(survey1)
    db_session.add(survey2)
    db_session.commit()
    
    # Get surveys
    response = client.get('/api/surveys', headers=admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'surveys' in response.json
    assert len(response.json['surveys']) >= 2
    
    # Check that surveys belong to the correct tenant
    for survey in response.json['surveys']:
        assert survey['tenant_id'] == str(tenant.id)
    
    # Check that created surveys are in the list
    survey_names = [s['name'] for s in response.json['surveys']]
    assert 'Survey 1' in survey_names
    assert 'Survey 2' in survey_names


def test_get_surveys_as_agent(client, agent_headers, db_session, tenant):
    """Test getting surveys as agent."""
    # Create some surveys
    from models.survey import Survey
    survey1 = Survey(tenant_id=tenant.id, name='Survey 3', type='individual', active=True)
    survey2 = Survey(tenant_id=tenant.id, name='Survey 4', type='shop', active=True)
    db_session.add(survey1)
    db_session.add(survey2)
    db_session.commit()
    
    # Get surveys as agent
    response = client.get('/api/surveys', headers=agent_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'surveys' in response.json
    
    # Check that surveys belong to the correct tenant
    for survey in response.json['surveys']:
        assert survey['tenant_id'] == str(tenant.id)


def test_get_survey_by_id(client, admin_headers, db_session, tenant):
    """Test getting a survey by ID."""
    # Create a survey
    from models.survey import Survey
    survey = Survey(tenant_id=tenant.id, name='Test Survey', type='individual', active=True)
    db_session.add(survey)
    db_session.commit()
    
    # Get survey by ID
    response = client.get(f'/api/surveys/{survey.id}', headers=admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'id' in response.json
    assert response.json['id'] == str(survey.id)
    assert response.json['name'] == 'Test Survey'
    assert response.json['type'] == 'individual'
    assert response.json['active'] is True
    assert response.json['tenant_id'] == str(tenant.id)


def test_get_survey_by_id_not_found(client, admin_headers):
    """Test getting a non-existent survey."""
    # Get non-existent survey
    random_id = uuid.uuid4()
    response = client.get(f'/api/surveys/{random_id}', headers=admin_headers)
    
    # Check response
    assert response.status_code == 404
    assert 'error' in response.json


def test_create_survey_as_admin(client, admin_headers, tenant):
    """Test creating a survey as admin."""
    # Create survey
    response = client.post('/api/surveys', json={
        'name': 'New Survey',
        'type': 'shop',
        'active': True
    }, headers=admin_headers)
    
    # Check response
    assert response.status_code == 201
    assert 'id' in response.json
    assert response.json['name'] == 'New Survey'
    assert response.json['type'] == 'shop'
    assert response.json['active'] is True
    assert response.json['tenant_id'] == str(tenant.id)
    
    # Check that survey can be retrieved
    survey_id = response.json['id']
    get_response = client.get(f'/api/surveys/{survey_id}', headers=admin_headers)
    assert get_response.status_code == 200
    assert get_response.json['name'] == 'New Survey'


def test_create_survey_as_agent(client, agent_headers):
    """Test creating a survey as agent (should be forbidden)."""
    # Create survey as agent
    response = client.post('/api/surveys', json={
        'name': 'Agent Survey',
        'type': 'individual',
        'active': True
    }, headers=agent_headers)
    
    # Check response
    assert response.status_code == 403
    assert 'error' in response.json


def test_update_survey_as_admin(client, admin_headers, db_session, tenant):
    """Test updating a survey as admin."""
    # Create a survey
    from models.survey import Survey
    survey = Survey(tenant_id=tenant.id, name='Survey to Update', type='individual', active=True)
    db_session.add(survey)
    db_session.commit()
    
    # Update survey
    response = client.put(f'/api/surveys/{survey.id}', json={
        'name': 'Updated Survey',
        'type': 'shop',
        'active': False
    }, headers=admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert response.json['name'] == 'Updated Survey'
    assert response.json['type'] == 'shop'
    assert response.json['active'] is False
    
    # Check that survey was updated
    get_response = client.get(f'/api/surveys/{survey.id}', headers=admin_headers)
    assert get_response.status_code == 200
    assert get_response.json['name'] == 'Updated Survey'
    assert get_response.json['type'] == 'shop'
    assert get_response.json['active'] is False


def test_update_survey_as_agent(client, agent_headers, db_session, tenant):
    """Test updating a survey as agent (should be forbidden)."""
    # Create a survey
    from models.survey import Survey
    survey = Survey(tenant_id=tenant.id, name='Survey for Agent Test', type='individual', active=True)
    db_session.add(survey)
    db_session.commit()
    
    # Update survey as agent
    response = client.put(f'/api/surveys/{survey.id}', json={
        'name': 'Agent Updated Survey',
        'type': 'shop',
        'active': False
    }, headers=agent_headers)
    
    # Check response
    assert response.status_code == 403
    assert 'error' in response.json


def test_delete_survey_as_admin(client, admin_headers, db_session, tenant):
    """Test deleting a survey as admin."""
    # Create a survey
    from models.survey import Survey
    survey = Survey(tenant_id=tenant.id, name='Survey to Delete', type='individual', active=True)
    db_session.add(survey)
    db_session.commit()
    
    # Delete survey
    response = client.delete(f'/api/surveys/{survey.id}', headers=admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'message' in response.json
    
    # Check that survey is deleted
    get_response = client.get(f'/api/surveys/{survey.id}', headers=admin_headers)
    assert get_response.status_code == 404


def test_delete_survey_as_agent(client, agent_headers, db_session, tenant):
    """Test deleting a survey as agent (should be forbidden)."""
    # Create a survey
    from models.survey import Survey
    survey = Survey(tenant_id=tenant.id, name='Survey for Agent Delete Test', type='individual', active=True)
    db_session.add(survey)
    db_session.commit()
    
    # Delete survey as agent
    response = client.delete(f'/api/surveys/{survey.id}', headers=agent_headers)
    
    # Check response
    assert response.status_code == 403
    assert 'error' in response.json


def test_add_question_to_survey(client, admin_headers, db_session, tenant):
    """Test adding a question to a survey."""
    # Create a survey
    from models.survey import Survey
    survey = Survey(tenant_id=tenant.id, name='Survey with Questions', type='individual', active=True)
    db_session.add(survey)
    db_session.commit()
    
    # Add question to survey
    response = client.post(f'/api/surveys/{survey.id}/questions', json={
        'question_text': 'Test Question',
        'input_type': 'text',
        'meta': {'help_text': 'Enter your answer'},
        'order_num': 1
    }, headers=admin_headers)
    
    # Check response
    assert response.status_code == 201
    assert 'id' in response.json
    assert response.json['question_text'] == 'Test Question'
    assert response.json['input_type'] == 'text'
    assert response.json['meta'] == {'help_text': 'Enter your answer'}
    assert response.json['order_num'] == 1
    assert response.json['survey_id'] == str(survey.id)
    assert response.json['tenant_id'] == str(tenant.id)
    
    # Get survey with questions
    get_response = client.get(f'/api/surveys/{survey.id}', headers=admin_headers)
    assert get_response.status_code == 200
    assert 'questions' in get_response.json
    assert len(get_response.json['questions']) >= 1
    
    # Check that added question is in the list
    question_texts = [q['question_text'] for q in get_response.json['questions']]
    assert 'Test Question' in question_texts


def test_add_question_to_survey_as_agent(client, agent_headers, db_session, tenant):
    """Test adding a question to a survey as agent (should be forbidden)."""
    # Create a survey
    from models.survey import Survey
    survey = Survey(tenant_id=tenant.id, name='Survey for Agent Question Test', type='individual', active=True)
    db_session.add(survey)
    db_session.commit()
    
    # Add question to survey as agent
    response = client.post(f'/api/surveys/{survey.id}/questions', json={
        'question_text': 'Agent Question',
        'input_type': 'text',
        'meta': {'help_text': 'Agent help text'},
        'order_num': 1
    }, headers=agent_headers)
    
    # Check response
    assert response.status_code == 403
    assert 'error' in response.json


def test_update_question(client, admin_headers, db_session, tenant):
    """Test updating a question."""
    # Create a survey and question
    from models.survey import Survey
    from models.question import SurveyQuestion
    survey = Survey(tenant_id=tenant.id, name='Survey for Question Update', type='individual', active=True)
    db_session.add(survey)
    db_session.commit()
    
    question = SurveyQuestion(
        tenant_id=tenant.id,
        survey_id=survey.id,
        question_text='Question to Update',
        input_type='text',
        meta={'help_text': 'Original help text'},
        order_num=1
    )
    db_session.add(question)
    db_session.commit()
    
    # Update question
    response = client.put(f'/api/questions/{question.id}', json={
        'question_text': 'Updated Question',
        'input_type': 'select',
        'meta': {'help_text': 'Updated help text', 'options': ['Option 1', 'Option 2']},
        'order_num': 2
    }, headers=admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert response.json['question_text'] == 'Updated Question'
    assert response.json['input_type'] == 'select'
    assert response.json['meta'] == {'help_text': 'Updated help text', 'options': ['Option 1', 'Option 2']}
    assert response.json['order_num'] == 2
    
    # Check that question was updated
    get_response = client.get(f'/api/surveys/{survey.id}', headers=admin_headers)
    assert get_response.status_code == 200
    assert 'questions' in get_response.json
    
    # Find the updated question in the list
    updated_question = None
    for q in get_response.json['questions']:
        if q['id'] == str(question.id):
            updated_question = q
            break
    
    assert updated_question is not None
    assert updated_question['question_text'] == 'Updated Question'
    assert updated_question['input_type'] == 'select'
    assert updated_question['meta'] == {'help_text': 'Updated help text', 'options': ['Option 1', 'Option 2']}
    assert updated_question['order_num'] == 2


def test_update_question_as_agent(client, agent_headers, db_session, tenant):
    """Test updating a question as agent (should be forbidden)."""
    # Create a survey and question
    from models.survey import Survey
    from models.question import SurveyQuestion
    survey = Survey(tenant_id=tenant.id, name='Survey for Agent Question Update', type='individual', active=True)
    db_session.add(survey)
    db_session.commit()
    
    question = SurveyQuestion(
        tenant_id=tenant.id,
        survey_id=survey.id,
        question_text='Question for Agent Update',
        input_type='text',
        meta={'help_text': 'Original help text'},
        order_num=1
    )
    db_session.add(question)
    db_session.commit()
    
    # Update question as agent
    response = client.put(f'/api/questions/{question.id}', json={
        'question_text': 'Agent Updated Question',
        'input_type': 'select',
        'meta': {'help_text': 'Agent updated help text'},
        'order_num': 2
    }, headers=agent_headers)
    
    # Check response
    assert response.status_code == 403
    assert 'error' in response.json


def test_delete_question(client, admin_headers, db_session, tenant):
    """Test deleting a question."""
    # Create a survey and question
    from models.survey import Survey
    from models.question import SurveyQuestion
    survey = Survey(tenant_id=tenant.id, name='Survey for Question Delete', type='individual', active=True)
    db_session.add(survey)
    db_session.commit()
    
    question = SurveyQuestion(
        tenant_id=tenant.id,
        survey_id=survey.id,
        question_text='Question to Delete',
        input_type='text',
        meta={'help_text': 'Help text'},
        order_num=1
    )
    db_session.add(question)
    db_session.commit()
    
    # Delete question
    response = client.delete(f'/api/questions/{question.id}', headers=admin_headers)
    
    # Check response
    assert response.status_code == 200
    assert 'message' in response.json
    
    # Check that question is deleted
    get_response = client.get(f'/api/surveys/{survey.id}', headers=admin_headers)
    assert get_response.status_code == 200
    assert 'questions' in get_response.json
    
    # Check that deleted question is not in the list
    question_ids = [q['id'] for q in get_response.json['questions']]
    assert str(question.id) not in question_ids


def test_delete_question_as_agent(client, agent_headers, db_session, tenant):
    """Test deleting a question as agent (should be forbidden)."""
    # Create a survey and question
    from models.survey import Survey
    from models.question import SurveyQuestion
    survey = Survey(tenant_id=tenant.id, name='Survey for Agent Question Delete', type='individual', active=True)
    db_session.add(survey)
    db_session.commit()
    
    question = SurveyQuestion(
        tenant_id=tenant.id,
        survey_id=survey.id,
        question_text='Question for Agent Delete',
        input_type='text',
        meta={'help_text': 'Help text'},
        order_num=1
    )
    db_session.add(question)
    db_session.commit()
    
    # Delete question as agent
    response = client.delete(f'/api/questions/{question.id}', headers=agent_headers)
    
    # Check response
    assert response.status_code == 403
    assert 'error' in response.json