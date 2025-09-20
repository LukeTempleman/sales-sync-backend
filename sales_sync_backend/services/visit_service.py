from datetime import datetime
from models.visit import Visit, VisitAnswer


def get_visits(session, tenant_id, filters=None):
    """
    Get visits for a tenant.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        filters: Optional filters
    
    Returns:
        list: List of visits
    """
    query = session.query(Visit).filter(Visit.tenant_id == tenant_id)
    
    # Apply filters
    if filters:
        if 'user_id' in filters:
            query = query.filter(Visit.user_id == filters['user_id'])
        if 'survey_id' in filters:
            query = query.filter(Visit.survey_id == filters['survey_id'])
        if 'visit_type' in filters:
            query = query.filter(Visit.visit_type == filters['visit_type'])
        if 'shop_id' in filters:
            query = query.filter(Visit.shop_id == filters['shop_id'])
        if 'start_date' in filters:
            query = query.filter(Visit.started_at >= filters['start_date'])
        if 'end_date' in filters:
            query = query.filter(Visit.started_at <= filters['end_date'])
        if 'completed' in filters:
            if filters['completed']:
                query = query.filter(Visit.completed_at.isnot(None))
            else:
                query = query.filter(Visit.completed_at.is_(None))
    
    return query.all()


def get_visit_by_id(session, tenant_id, visit_id):
    """
    Get visit by ID.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        visit_id: Visit ID
    
    Returns:
        Visit: Visit object or None
    """
    return session.query(Visit).filter(
        Visit.tenant_id == tenant_id,
        Visit.id == visit_id
    ).first()


def create_visit(session, tenant_id, user_id, survey_id, visit_type, geocode=None, shop_id=None):
    """
    Create a new visit.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        user_id: User ID
        survey_id: Survey ID
        visit_type: Visit type ('individual' or 'shop')
        geocode: Geocode (optional)
        shop_id: Shop ID (optional)
    
    Returns:
        Visit: Created visit
    """
    visit = Visit(
        tenant_id=tenant_id,
        user_id=user_id,
        survey_id=survey_id,
        visit_type=visit_type,
        geocode=geocode,
        shop_id=shop_id,
        started_at=datetime.utcnow()
    )
    session.add(visit)
    session.commit()
    return visit


def complete_visit(session, tenant_id, visit_id, answers=None):
    """
    Complete a visit.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        visit_id: Visit ID
        answers: List of answers (optional)
    
    Returns:
        Visit: Updated visit or None
    """
    visit = get_visit_by_id(session, tenant_id, visit_id)
    if not visit:
        return None
    
    # Update visit
    visit.completed_at = datetime.utcnow()
    
    # Add answers if provided
    if answers:
        for answer in answers:
            visit_answer = VisitAnswer(
                tenant_id=tenant_id,
                visit_id=visit_id,
                question_id=answer.get('question_id'),
                answer_text=answer.get('answer_text'),
                answer_json=answer.get('answer_json')
            )
            session.add(visit_answer)
    
    session.commit()
    return visit


def get_visit_answers(session, tenant_id, visit_id):
    """
    Get answers for a visit.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        visit_id: Visit ID
    
    Returns:
        list: List of answers
    """
    return session.query(VisitAnswer).filter(
        VisitAnswer.tenant_id == tenant_id,
        VisitAnswer.visit_id == visit_id
    ).all()


def get_visit_photos(session, tenant_id, visit_id):
    """
    Get photos for a visit.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        visit_id: Visit ID
    
    Returns:
        list: List of photos
    """
    from models.photo import Photo
    return session.query(Photo).filter(
        Photo.tenant_id == tenant_id,
        Photo.visit_id == visit_id
    ).all()