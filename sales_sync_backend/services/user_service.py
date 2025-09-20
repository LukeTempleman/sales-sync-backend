from models.user import User
from models.role import Role, UserRole
from services.auth_service import hash_password


def get_users(session, tenant_id, filters=None):
    """
    Get users for a tenant.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        filters: Optional filters
    
    Returns:
        list: List of users
    """
    query = session.query(User).filter(User.tenant_id == tenant_id)
    
    # Apply filters
    if filters:
        if 'email' in filters:
            query = query.filter(User.email.ilike(f"%{filters['email']}%"))
        if 'is_active' in filters:
            query = query.filter(User.is_active == filters['is_active'])
    
    return query.all()


def get_user_by_id(session, tenant_id, user_id):
    """
    Get user by ID.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        user_id: User ID
    
    Returns:
        User: User object or None
    """
    return session.query(User).filter(
        User.tenant_id == tenant_id,
        User.id == user_id
    ).first()


def create_user(session, tenant_id, email, password, first_name, last_name, phone=None, roles=None):
    """
    Create a new user.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        email: User email
        password: User password
        first_name: User first name
        last_name: User last name
        phone: User phone
        roles: List of role names
    
    Returns:
        User: Created user
    """
    # Hash password
    password_hash = hash_password(password)
    
    # Create user
    user = User(
        tenant_id=tenant_id,
        email=email,
        password_hash=password_hash,
        first_name=first_name,
        last_name=last_name,
        phone=phone
    )
    session.add(user)
    session.flush()
    
    # Add roles
    if roles:
        for role_name in roles:
            role = session.query(Role).filter_by(name=role_name).first()
            if role:
                user_role = UserRole(user_id=user.id, role_id=role.id)
                session.add(user_role)
    
    session.commit()
    return user


def update_user(session, tenant_id, user_id, data):
    """
    Update a user.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        user_id: User ID
        data: User data to update
    
    Returns:
        User: Updated user or None
    """
    user = get_user_by_id(session, tenant_id, user_id)
    if not user:
        return None
    
    # Update user fields
    if 'email' in data:
        user.email = data['email']
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'phone' in data:
        user.phone = data['phone']
    if 'is_active' in data:
        user.is_active = data['is_active']
    
    session.commit()
    return user


def update_user_password(session, tenant_id, user_id, password):
    """
    Update a user's password.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        user_id: User ID
        password: New password
    
    Returns:
        User: Updated user or None
    """
    user = get_user_by_id(session, tenant_id, user_id)
    if not user:
        return None
    
    # Update password
    user.password_hash = hash_password(password)
    
    session.commit()
    return user


def update_user_roles(session, tenant_id, user_id, roles):
    """
    Update a user's roles.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        user_id: User ID
        roles: List of role names
    
    Returns:
        User: Updated user or None
    """
    user = get_user_by_id(session, tenant_id, user_id)
    if not user:
        return None
    
    # Remove existing roles
    session.query(UserRole).filter(UserRole.user_id == user.id).delete()
    
    # Add new roles
    for role_name in roles:
        role = session.query(Role).filter_by(name=role_name).first()
        if role:
            user_role = UserRole(user_id=user.id, role_id=role.id)
            session.add(user_role)
    
    session.commit()
    return user


def delete_user(session, tenant_id, user_id):
    """
    Delete a user (soft delete by setting is_active=False).
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        user_id: User ID
    
    Returns:
        bool: True if user was deleted, False otherwise
    """
    user = get_user_by_id(session, tenant_id, user_id)
    if not user:
        return False
    
    # Soft delete
    user.is_active = False
    
    session.commit()
    return True