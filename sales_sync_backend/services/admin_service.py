from datetime import datetime, timedelta
from sqlalchemy import func, and_, extract

from models.user import User
from models.visit import Visit
from models.survey import Survey
from models.audit import AuditLog


def get_user_activity(session, tenant_id, start_date=None, end_date=None):
    """
    Get user activity for a tenant.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        start_date: Start date (optional)
        end_date: End date (optional)
    
    Returns:
        dict: User activity data
    """
    # Set default date range if not provided
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()
    
    # Get all users
    users = session.query(User).filter(User.tenant_id == tenant_id).all()
    
    # Get visits by user
    visits_by_user = session.query(
        Visit.user_id,
        func.count(Visit.id).label('total_visits'),
        func.count(Visit.completed_at).label('completed_visits')
    ).filter(
        Visit.tenant_id == tenant_id,
        Visit.started_at >= start_date,
        Visit.started_at <= end_date
    ).group_by(Visit.user_id).all()
    
    # Get last login for each user
    last_logins = {}
    for user in users:
        # In a real implementation, this would be fetched from the database
        # For now, we'll just use a placeholder
        last_logins[str(user.id)] = user.last_login_at
    
    # Format results
    user_activity = {}
    for user in users:
        # Find visits for this user
        user_visits = next((v for v in visits_by_user if v.user_id == user.id), None)
        
        user_activity[str(user.id)] = {
            'user_id': str(user.id),
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'total_visits': user_visits.total_visits if user_visits else 0,
            'completed_visits': user_visits.completed_visits if user_visits else 0,
            'last_login': last_logins.get(str(user.id))
        }
    
    # Format the response as expected by the tests
    return {
        'activity': {
            'users': [user_data for user_data in user_activity.values()],
            'total_users': len(users),
            'active_users': len([u for u in user_activity.values() if u['total_visits'] > 0])
        }
    }


def get_survey_completion_rates(session, tenant_id, start_date=None, end_date=None):
    """
    Get survey completion rates for a tenant.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        start_date: Start date (optional)
        end_date: End date (optional)
    
    Returns:
        dict: Survey completion rates
    """
    # Set default date range if not provided
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()
    
    # Get all surveys
    surveys = session.query(Survey).filter(Survey.tenant_id == tenant_id).all()
    
    # Get visits by survey
    visits_by_survey = session.query(
        Visit.survey_id,
        func.count(Visit.id).label('total_visits'),
        func.count(Visit.completed_at).label('completed_visits')
    ).filter(
        Visit.tenant_id == tenant_id,
        Visit.started_at >= start_date,
        Visit.started_at <= end_date
    ).group_by(Visit.survey_id).all()
    
    # Format results
    survey_completion_rates = {}
    for survey in surveys:
        # Find visits for this survey
        survey_visits = next((v for v in visits_by_survey if v.survey_id == survey.id), None)
        
        total_visits = survey_visits.total_visits if survey_visits else 0
        completed_visits = survey_visits.completed_visits if survey_visits else 0
        completion_rate = (completed_visits / total_visits) * 100.0 if total_visits > 0 else 0.0
        
        survey_completion_rates[str(survey.id)] = {
            'survey_id': str(survey.id),
            'name': survey.name,
            'total_visits': total_visits,
            'completed_visits': completed_visits,
            'completion_rate': completion_rate
        }
    
    # Format the response as expected by the tests
    return {
        'completion_rates': {
            'surveys': [survey_data for survey_data in survey_completion_rates.values()],
            'total_surveys': len(surveys),
            'average_completion_rate': sum(s['completion_rate'] for s in survey_completion_rates.values()) / len(surveys) if surveys else 0.0
        }
    }


def get_audit_logs(session, tenant_id=None, user_id=None, action=None, object_type=None, object_id=None, start_date=None, end_date=None, limit=100, offset=0):
    """
    Get audit logs.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID (optional)
        user_id: User ID (optional)
        action: Action (optional)
        object_type: Object type (optional)
        object_id: Object ID (optional)
        start_date: Start date (optional)
        end_date: End date (optional)
        limit: Limit (optional)
        offset: Offset (optional)
    
    Returns:
        list: Audit logs
    """
    # Build base query
    query = session.query(AuditLog)
    
    # Apply filters
    if tenant_id:
        query = query.filter(AuditLog.tenant_id == tenant_id)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if object_type:
        query = query.filter(AuditLog.object_type == object_type)
    if object_id:
        query = query.filter(AuditLog.object_id == object_id)
    if start_date:
        query = query.filter(AuditLog.created_at >= start_date)
    if end_date:
        query = query.filter(AuditLog.created_at <= end_date)
    
    # Apply pagination
    query = query.order_by(AuditLog.created_at.desc()).limit(limit).offset(offset)
    
    # Get audit logs
    audit_logs = query.all()
    
    # Format logs
    formatted_logs = [log.to_dict() for log in audit_logs]
    
    # Get total count (without pagination)
    total_count_query = session.query(func.count(AuditLog.id))
    if tenant_id:
        total_count_query = total_count_query.filter(AuditLog.tenant_id == tenant_id)
    if user_id:
        total_count_query = total_count_query.filter(AuditLog.user_id == user_id)
    if action:
        total_count_query = total_count_query.filter(AuditLog.action == action)
    if object_type:
        total_count_query = total_count_query.filter(AuditLog.object_type == object_type)
    if object_id:
        total_count_query = total_count_query.filter(AuditLog.object_id == object_id)
    if start_date:
        total_count_query = total_count_query.filter(AuditLog.created_at >= start_date)
    if end_date:
        total_count_query = total_count_query.filter(AuditLog.created_at <= end_date)
    
    total_count = total_count_query.scalar()
    
    # Return audit logs with pagination info
    return {
        'logs': formatted_logs,
        'pagination': {
            'total': total_count,
            'limit': limit,
            'offset': offset,
            'has_more': (offset + limit) < total_count
        }
    }