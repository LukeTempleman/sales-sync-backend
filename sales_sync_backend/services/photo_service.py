from models.photo import Photo, ShelfQuadrant


def get_photos(session, tenant_id, filters=None):
    """
    Get photos for a tenant.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        filters: Optional filters
    
    Returns:
        list: List of photos
    """
    query = session.query(Photo).filter(Photo.tenant_id == tenant_id)
    
    # Apply filters
    if filters:
        if 'visit_id' in filters:
            query = query.filter(Photo.visit_id == filters['visit_id'])
        if 'purpose' in filters:
            query = query.filter(Photo.purpose == filters['purpose'])
    
    return query.all()


def get_photo_by_id(session, tenant_id, photo_id):
    """
    Get photo by ID.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        photo_id: Photo ID
    
    Returns:
        Photo: Photo object or None
    """
    return session.query(Photo).filter(
        Photo.tenant_id == tenant_id,
        Photo.id == photo_id
    ).first()


def create_photo(session, tenant_id, visit_id, file_url, purpose=None, metadata=None):
    """
    Create a new photo.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        visit_id: Visit ID
        file_url: File URL
        purpose: Photo purpose ('id', 'shelf', 'outside', 'board')
        metadata: Photo metadata (width, height, orientation, etc.)
    
    Returns:
        Photo: Created photo
    """
    photo = Photo(
        tenant_id=tenant_id,
        visit_id=visit_id,
        file_url=file_url,
        purpose=purpose,
        metadata=metadata
    )
    session.add(photo)
    session.commit()
    return photo


def get_shelf_quadrants(session, tenant_id, photo_id):
    """
    Get shelf quadrants for a photo.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        photo_id: Photo ID
    
    Returns:
        list: List of shelf quadrants
    """
    return session.query(ShelfQuadrant).filter(
        ShelfQuadrant.tenant_id == tenant_id,
        ShelfQuadrant.photo_id == photo_id
    ).all()


def create_shelf_quadrant(session, tenant_id, photo_id, brand_id, quadrant_coords, area_percentage=None):
    """
    Create a new shelf quadrant.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        photo_id: Photo ID
        brand_id: Brand ID
        quadrant_coords: Quadrant coordinates
        area_percentage: Area percentage
    
    Returns:
        ShelfQuadrant: Created shelf quadrant
    """
    # Calculate area percentage if not provided
    if area_percentage is None:
        # Simple calculation based on quadrant coordinates
        # In a real implementation, this would be more sophisticated
        area_percentage = 0.0
        if isinstance(quadrant_coords, list) and len(quadrant_coords) > 0:
            # Assuming quadrant_coords is a list of polygons
            # Each polygon is a list of points (x, y)
            # Calculate area percentage based on polygon area
            area_percentage = len(quadrant_coords) * 5.0  # Simplified calculation
    
    shelf_quadrant = ShelfQuadrant(
        tenant_id=tenant_id,
        photo_id=photo_id,
        brand_id=brand_id,
        quadrant_coords=quadrant_coords,
        area_percentage=area_percentage
    )
    session.add(shelf_quadrant)
    session.commit()
    return shelf_quadrant