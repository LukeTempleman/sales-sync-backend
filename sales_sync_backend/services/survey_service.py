from models.survey import Survey, SurveyQuestion


def get_surveys(session, tenant_id, filters=None):
    """
    Get surveys for a tenant.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        filters: Optional filters
    
    Returns:
        list: List of surveys
    """
    query = session.query(Survey).filter(Survey.tenant_id == tenant_id)
    
    # Apply filters
    if filters:
        if 'name' in filters:
            query = query.filter(Survey.name.ilike(f"%{filters['name']}%"))
        if 'type' in filters:
            query = query.filter(Survey.type == filters['type'])
        if 'active' in filters:
            query = query.filter(Survey.active == filters['active'])
        if 'brand_id' in filters:
            query = query.filter(Survey.brand_id == filters['brand_id'])
    
    return query.all()


def get_survey_by_id(session, tenant_id, survey_id):
    """
    Get survey by ID.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        survey_id: Survey ID
    
    Returns:
        Survey: Survey object or None
    """
    return session.query(Survey).filter(
        Survey.tenant_id == tenant_id,
        Survey.id == survey_id
    ).first()


def create_survey(session, tenant_id, name, survey_type, brand_id=None, active=True, created_by=None):
    """
    Create a new survey.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        name: Survey name
        survey_type: Survey type ('individual' or 'shop')
        brand_id: Brand ID (optional)
        active: Survey active status
        created_by: User ID who created the survey
    
    Returns:
        Survey: Created survey
    """
    survey = Survey(
        tenant_id=tenant_id,
        name=name,
        type=survey_type,
        brand_id=brand_id,
        active=active,
        created_by=created_by
    )
    session.add(survey)
    session.commit()
    return survey


def update_survey(session, tenant_id, survey_id, data):
    """
    Update a survey.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        survey_id: Survey ID
        data: Survey data to update
    
    Returns:
        Survey: Updated survey or None
    """
    survey = get_survey_by_id(session, tenant_id, survey_id)
    if not survey:
        return None
    
    # Update survey fields
    if 'name' in data:
        survey.name = data['name']
    if 'type' in data:
        survey.type = data['type']
    if 'brand_id' in data:
        survey.brand_id = data['brand_id']
    if 'active' in data:
        survey.active = data['active']
    
    session.commit()
    return survey


def delete_survey(session, tenant_id, survey_id):
    """
    Delete a survey.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        survey_id: Survey ID
    
    Returns:
        bool: True if survey was deleted, False otherwise
    """
    survey = get_survey_by_id(session, tenant_id, survey_id)
    if not survey:
        return False
    
    session.delete(survey)
    session.commit()
    return True


def get_survey_questions(session, tenant_id, survey_id):
    """
    Get questions for a survey.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        survey_id: Survey ID
    
    Returns:
        list: List of questions
    """
    return session.query(SurveyQuestion).filter(
        SurveyQuestion.tenant_id == tenant_id,
        SurveyQuestion.survey_id == survey_id
    ).order_by(SurveyQuestion.order_num).all()


def get_question_by_id(session, tenant_id, question_id):
    """
    Get question by ID.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        question_id: Question ID
    
    Returns:
        SurveyQuestion: Question object or None
    """
    return session.query(SurveyQuestion).filter(
        SurveyQuestion.tenant_id == tenant_id,
        SurveyQuestion.id == question_id
    ).first()


def create_question(session, tenant_id, survey_id, question_text, input_type, meta=None, order_num=0):
    """
    Create a new question.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        survey_id: Survey ID
        question_text: Question text
        input_type: Input type ('text', 'select', 'boolean', 'photo', 'number')
        meta: Question metadata (choices, validation rules, help text)
        order_num: Question order number
    
    Returns:
        SurveyQuestion: Created question
    """
    question = SurveyQuestion(
        tenant_id=tenant_id,
        survey_id=survey_id,
        question_text=question_text,
        input_type=input_type,
        meta=meta,
        order_num=order_num
    )
    session.add(question)
    session.commit()
    return question


def update_question(session, tenant_id, question_id, data):
    """
    Update a question.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        question_id: Question ID
        data: Question data to update
    
    Returns:
        SurveyQuestion: Updated question or None
    """
    question = get_question_by_id(session, tenant_id, question_id)
    if not question:
        return None
    
    # Update question fields
    if 'question_text' in data:
        question.question_text = data['question_text']
    if 'input_type' in data:
        question.input_type = data['input_type']
    if 'meta' in data:
        question.meta = data['meta']
    if 'order_num' in data:
        question.order_num = data['order_num']
    
    session.commit()
    return question


def delete_question(session, tenant_id, question_id):
    """
    Delete a question.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        question_id: Question ID
    
    Returns:
        bool: True if question was deleted, False otherwise
    """
    question = get_question_by_id(session, tenant_id, question_id)
    if not question:
        return False
    
    session.delete(question)
    session.commit()
    return True