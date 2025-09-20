from models.call_cycle import CallCycle, CallCycleLocation


def get_call_cycles(session, tenant_id, filters=None):
    """
    Get call cycles for a tenant.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        filters: Optional filters
    
    Returns:
        list: List of call cycles
    """
    query = session.query(CallCycle).filter(CallCycle.tenant_id == tenant_id)
    
    # Apply filters
    if filters:
        if 'name' in filters:
            query = query.filter(CallCycle.name.ilike(f"%{filters['name']}%"))
        if 'frequency' in filters:
            query = query.filter(CallCycle.frequency == filters['frequency'])
        if 'created_by' in filters:
            query = query.filter(CallCycle.created_by == filters['created_by'])
    
    return query.all()


def get_call_cycle_by_id(session, tenant_id, call_cycle_id):
    """
    Get call cycle by ID.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        call_cycle_id: Call cycle ID
    
    Returns:
        CallCycle: Call cycle object or None
    """
    return session.query(CallCycle).filter(
        CallCycle.tenant_id == tenant_id,
        CallCycle.id == call_cycle_id
    ).first()


def create_call_cycle(session, tenant_id, name, frequency, created_by=None):
    """
    Create a new call cycle.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        name: Call cycle name
        frequency: Call cycle frequency ('daily', 'weekly', 'monthly')
        created_by: User ID who created the call cycle
    
    Returns:
        CallCycle: Created call cycle
    """
    call_cycle = CallCycle(
        tenant_id=tenant_id,
        name=name,
        frequency=frequency,
        created_by=created_by
    )
    session.add(call_cycle)
    session.commit()
    return call_cycle


def update_call_cycle(session, tenant_id, call_cycle_id, data):
    """
    Update a call cycle.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        call_cycle_id: Call cycle ID
        data: Call cycle data to update
    
    Returns:
        CallCycle: Updated call cycle or None
    """
    call_cycle = get_call_cycle_by_id(session, tenant_id, call_cycle_id)
    if not call_cycle:
        return None
    
    # Update call cycle fields
    if 'name' in data:
        call_cycle.name = data['name']
    if 'frequency' in data:
        call_cycle.frequency = data['frequency']
    
    session.commit()
    return call_cycle


def delete_call_cycle(session, tenant_id, call_cycle_id):
    """
    Delete a call cycle.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        call_cycle_id: Call cycle ID
    
    Returns:
        bool: True if call cycle was deleted, False otherwise
    """
    call_cycle = get_call_cycle_by_id(session, tenant_id, call_cycle_id)
    if not call_cycle:
        return False
    
    session.delete(call_cycle)
    session.commit()
    return True


def get_call_cycle_locations(session, tenant_id, call_cycle_id):
    """
    Get locations for a call cycle.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        call_cycle_id: Call cycle ID
    
    Returns:
        list: List of call cycle locations
    """
    # Get call cycle
    call_cycle = get_call_cycle_by_id(session, tenant_id, call_cycle_id)
    if not call_cycle:
        return []
    
    # Get call cycle locations
    return session.query(CallCycleLocation).filter(
        CallCycleLocation.call_cycle_id == call_cycle_id
    ).order_by(CallCycleLocation.order_num).all()


def add_call_cycle_location(session, call_cycle_id, location, shop_id=None, order_num=0):
    """
    Add a location to a call cycle.
    
    Args:
        session: SQLAlchemy session
        call_cycle_id: Call cycle ID
        location: Location (geography point)
        shop_id: Shop ID (optional)
        order_num: Order number (optional)
    
    Returns:
        CallCycleLocation: Created call cycle location
    """
    call_cycle_location = CallCycleLocation(
        call_cycle_id=call_cycle_id,
        location=location,
        shop_id=shop_id,
        order_num=order_num
    )
    session.add(call_cycle_location)
    session.commit()
    return call_cycle_location


def remove_call_cycle_location(session, call_cycle_id, location_id):
    """
    Remove a location from a call cycle.
    
    Args:
        session: SQLAlchemy session
        call_cycle_id: Call cycle ID
        location_id: Call cycle location ID
    
    Returns:
        bool: True if location was removed, False otherwise
    """
    # Get call cycle location
    call_cycle_location = session.query(CallCycleLocation).filter(
        CallCycleLocation.call_cycle_id == call_cycle_id,
        CallCycleLocation.id == location_id
    ).first()
    
    if not call_cycle_location:
        return False
    
    # Remove location
    session.delete(call_cycle_location)
    session.commit()
    return True


def update_call_cycle_location_order(session, call_cycle_id, location_id, order_num):
    """
    Update the order of a call cycle location.
    
    Args:
        session: SQLAlchemy session
        call_cycle_id: Call cycle ID
        location_id: Call cycle location ID
        order_num: New order number
    
    Returns:
        CallCycleLocation: Updated call cycle location or None
    """
    # Get call cycle location
    call_cycle_location = session.query(CallCycleLocation).filter(
        CallCycleLocation.call_cycle_id == call_cycle_id,
        CallCycleLocation.id == location_id
    ).first()
    
    if not call_cycle_location:
        return None
    
    # Update order
    call_cycle_location.order_num = order_num
    session.commit()
    return call_cycle_location


def get_call_cycle_status(session, tenant_id, call_cycle_id):
    """
    Get status for a call cycle.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        call_cycle_id: Call cycle ID
    
    Returns:
        dict: Call cycle status data
    """
    # Get call cycle
    call_cycle = get_call_cycle_by_id(session, tenant_id, call_cycle_id)
    if not call_cycle:
        return None
    
    # Get call cycle locations
    locations = get_call_cycle_locations(session, tenant_id, call_cycle_id)
    
    # Calculate adherence
    adherence_data = calculate_adherence(session, tenant_id, call_cycle, locations)
    
    # Get upcoming schedule
    upcoming_schedule = generate_upcoming_schedule(call_cycle, locations)
    
    # Return status data
    status_data = {
        'call_cycle': call_cycle.to_dict(),
        'locations': [location.to_dict() for location in locations],
        'adherence': adherence_data,
        'upcoming_schedule': upcoming_schedule
    }
    
    return status_data


def calculate_adherence(session, tenant_id, call_cycle, locations):
    """
    Calculate adherence for a call cycle.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        call_cycle: Call cycle object
        locations: List of call cycle locations
    
    Returns:
        dict: Adherence data
    """
    # This is a simplified implementation
    # In a real application, this would be more complex
    
    # Get visits for the call cycle locations
    from models.visit import Visit
    from sqlalchemy import func
    
    # If there are no locations, adherence is 0
    if not locations:
        return {
            'percentage': 0.0,
            'visited_locations': 0,
            'total_locations': 0
        }
    
    # Get shop IDs from locations
    shop_ids = [location.shop_id for location in locations if location.shop_id]
    
    # Get visits for the shops
    visits_count = 0
    if shop_ids:
        visits_count = session.query(func.count(Visit.id)).filter(
            Visit.tenant_id == tenant_id,
            Visit.shop_id.in_(shop_ids),
            Visit.completed_at.isnot(None)
        ).scalar()
    
    # Calculate adherence percentage
    total_locations = len(locations)
    adherence_percentage = (visits_count / total_locations) * 100.0 if total_locations > 0 else 0.0
    
    return {
        'percentage': adherence_percentage,
        'visited_locations': visits_count,
        'total_locations': total_locations
    }


def generate_upcoming_schedule(call_cycle, locations):
    """
    Generate upcoming schedule for a call cycle.
    
    Args:
        call_cycle: Call cycle object
        locations: List of call cycle locations
    
    Returns:
        list: Upcoming schedule data
    """
    # This is a simplified implementation
    # In a real application, this would be more complex
    
    # If there are no locations, return empty schedule
    if not locations:
        return []
    
    # Generate schedule based on frequency
    schedule = []
    for location in locations:
        schedule.append({
            'location': location.to_dict(),
            'scheduled_date': None  # In a real implementation, this would be calculated
        })
    
    return schedule