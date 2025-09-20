from models.brand import Brand, BrandInfographic


def get_brands(session, tenant_id, filters=None):
    """
    Get brands for a tenant.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        filters: Optional filters
    
    Returns:
        list: List of brands
    """
    query = session.query(Brand).filter(Brand.tenant_id == tenant_id)
    
    # Apply filters
    if filters:
        if 'name' in filters:
            query = query.filter(Brand.name.ilike(f"%{filters['name']}%"))
        if 'active' in filters:
            query = query.filter(Brand.active == filters['active'])
    
    return query.all()


def get_brand_by_id(session, tenant_id, brand_id):
    """
    Get brand by ID.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        brand_id: Brand ID
    
    Returns:
        Brand: Brand object or None
    """
    return session.query(Brand).filter(
        Brand.tenant_id == tenant_id,
        Brand.id == brand_id
    ).first()


def create_brand(session, tenant_id, name, slug=None, active=True):
    """
    Create a new brand.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        name: Brand name
        slug: Brand slug
        active: Brand active status
    
    Returns:
        Brand: Created brand
    """
    brand = Brand(
        tenant_id=tenant_id,
        name=name,
        slug=slug,
        active=active
    )
    session.add(brand)
    session.commit()
    return brand


def update_brand(session, tenant_id, brand_id, data):
    """
    Update a brand.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        brand_id: Brand ID
        data: Brand data to update
    
    Returns:
        Brand: Updated brand or None
    """
    brand = get_brand_by_id(session, tenant_id, brand_id)
    if not brand:
        return None
    
    # Update brand fields
    if 'name' in data:
        brand.name = data['name']
    if 'slug' in data:
        brand.slug = data['slug']
    if 'active' in data:
        brand.active = data['active']
    
    session.commit()
    return brand


def delete_brand(session, tenant_id, brand_id):
    """
    Delete a brand.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        brand_id: Brand ID
    
    Returns:
        bool: True if brand was deleted, False otherwise
    """
    brand = get_brand_by_id(session, tenant_id, brand_id)
    if not brand:
        return False
    
    session.delete(brand)
    session.commit()
    return True


def get_brand_infographics(session, tenant_id, brand_id):
    """
    Get infographics for a brand.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        brand_id: Brand ID
    
    Returns:
        list: List of infographics
    """
    return session.query(BrandInfographic).filter(
        BrandInfographic.tenant_id == tenant_id,
        BrandInfographic.brand_id == brand_id
    ).all()


def create_brand_infographic(session, tenant_id, brand_id, file_url, caption=None):
    """
    Create a new brand infographic.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        brand_id: Brand ID
        file_url: Infographic file URL
        caption: Infographic caption
    
    Returns:
        BrandInfographic: Created infographic
    """
    infographic = BrandInfographic(
        tenant_id=tenant_id,
        brand_id=brand_id,
        file_url=file_url,
        caption=caption
    )
    session.add(infographic)
    session.commit()
    return infographic