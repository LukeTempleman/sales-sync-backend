from models.tenant import Tenant


def get_tenants(session):
    """
    Get all tenants.
    
    Args:
        session: SQLAlchemy session
    
    Returns:
        list: List of tenants
    """
    return session.query(Tenant).all()


def get_tenant_by_id(session, tenant_id):
    """
    Get tenant by ID.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
    
    Returns:
        Tenant: Tenant object or None
    """
    return session.query(Tenant).filter(Tenant.id == tenant_id).first()


def get_tenant_by_subdomain(session, subdomain):
    """
    Get tenant by subdomain.
    
    Args:
        session: SQLAlchemy session
        subdomain: Tenant subdomain
    
    Returns:
        Tenant: Tenant object or None
    """
    return session.query(Tenant).filter(Tenant.subdomain == subdomain).first()


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


def update_tenant(session, tenant_id, data):
    """
    Update a tenant.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        data: Tenant data to update
    
    Returns:
        Tenant: Updated tenant or None
    """
    tenant = get_tenant_by_id(session, tenant_id)
    if not tenant:
        return None
    
    # Update tenant fields
    if 'name' in data:
        tenant.name = data['name']
    if 'subdomain' in data:
        tenant.subdomain = data['subdomain']
    
    session.commit()
    return tenant