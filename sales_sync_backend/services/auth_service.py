import uuid
from datetime import datetime
from passlib.hash import bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token

from models.tenant import Tenant
from models.user import User
from models.role import Role, UserRole


def hash_password(password):
    """
    Hash password using bcrypt.
    
    Args:
        password: Plain text password
    
    Returns:
        str: Hashed password
    """
    return bcrypt.hash(password)


def verify_password(password, password_hash):
    """
    Verify password against hash.
    
    Args:
        password: Plain text password
        password_hash: Hashed password
    
    Returns:
        bool: True if password matches hash
    """
    return bcrypt.verify(password, password_hash)


def create_tenant(session, name, subdomain=None):
    """
    Create a new tenant.
    
    Args:
        session: SQLAlchemy session
        name: Tenant name
        subdomain: Tenant subdomain
    
    Returns:
        Tenant: Created tenant
    """
    tenant = Tenant(name=name, subdomain=subdomain)
    session.add(tenant)
    session.commit()
    return tenant


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


def create_superadmin(session, email, password, first_name, last_name, phone=None):
    """
    Create a super admin user.
    
    Args:
        session: SQLAlchemy session
        email: User email
        password: User password
        first_name: User first name
        last_name: User last name
        phone: User phone
    
    Returns:
        User: Created super admin user
    """
    # Get or create system tenant
    system_tenant = session.query(Tenant).filter_by(name='System').first()
    if not system_tenant:
        system_tenant = create_tenant(session, 'System', 'system')
    
    # Create super admin user
    return create_user(
        session,
        system_tenant.id,
        email,
        password,
        first_name,
        last_name,
        phone,
        ['super_admin']
    )


def authenticate_user(session, email, password):
    """
    Authenticate user with email and password.
    
    Args:
        session: SQLAlchemy session
        email: User email
        password: User password
    
    Returns:
        User: Authenticated user or None
    """
    user = session.query(User).filter_by(email=email).first()
    if user and verify_password(password, user.password_hash):
        # Update last login
        user.last_login_at = datetime.utcnow()
        session.commit()
        return user
    return None


def generate_tokens(user):
    """
    Generate JWT access and refresh tokens for user.
    
    Args:
        user: User object
    
    Returns:
        dict: Access and refresh tokens
    """
    # Get user roles
    roles = [role.name for role in user.roles]
    
    # Create JWT claims
    claims = {
        'user_id': str(user.id),
        'tenant_id': str(user.tenant_id),
        'roles': roles,
        'email': user.email
    }
    
    # Generate tokens
    access_token = create_access_token(identity=str(user.id), additional_claims=claims)
    refresh_token = create_refresh_token(identity=str(user.id), additional_claims=claims)
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }


def register_tenant_and_admin(session, tenant_name, subdomain, email, password, first_name, last_name, phone=None):
    """
    Register a new tenant and admin user.
    
    Args:
        session: SQLAlchemy session
        tenant_name: Tenant name
        subdomain: Tenant subdomain
        email: Admin email
        password: Admin password
        first_name: Admin first name
        last_name: Admin last name
        phone: Admin phone
    
    Returns:
        dict: Tenant and admin user
    """
    # Create tenant
    tenant = create_tenant(session, tenant_name, subdomain)
    
    # Create admin user
    admin = create_user(
        session,
        tenant.id,
        email,
        password,
        first_name,
        last_name,
        phone,
        ['admin']
    )
    
    return {
        'tenant': tenant,
        'admin': admin
    }