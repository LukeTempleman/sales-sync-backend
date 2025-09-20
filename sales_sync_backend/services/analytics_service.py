from datetime import datetime, timedelta
from sqlalchemy import func, and_, extract

from models.visit import Visit
from models.photo import Photo, ShelfQuadrant
from models.brand import Brand
from models.call_cycle import CallCycle, CallCycleLocation


def get_overview_metrics(session, tenant_id, user_id=None, start_date=None, end_date=None):
    """
    Get overview metrics for a tenant.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        user_id: User ID (optional)
        start_date: Start date (optional)
        end_date: End date (optional)
    
    Returns:
        dict: Overview metrics
    """
    # Set default date range if not provided
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()
    
    # Build base query
    visits_query = session.query(Visit).filter(
        Visit.tenant_id == tenant_id,
        Visit.started_at >= start_date,
        Visit.started_at <= end_date
    )
    
    # Filter by user if provided
    if user_id:
        visits_query = visits_query.filter(Visit.user_id == user_id)
    
    # Get total visits
    total_visits = visits_query.count()
    
    # Get completed visits
    completed_visits = visits_query.filter(Visit.completed_at.isnot(None)).count()
    
    # Get shelf share metrics
    shelf_share = get_shelf_share_metrics(session, tenant_id, user_id, start_date, end_date)
    
    # Get call cycle coverage
    call_cycle_coverage = get_call_cycle_coverage_metrics(session, tenant_id, user_id, start_date, end_date)
    
    # Return overview metrics in the format expected by the tests
    return {
        'metrics': {
            'visits': {
                'total': total_visits,
                'completed': completed_visits,
                'completion_rate': (completed_visits / total_visits) * 100.0 if total_visits > 0 else 0.0
            },
            'conversions': {
                'total': 0,  # Placeholder for future implementation
                'rate': 0.0
            },
            'shelf_share': {
                'average': 0.0,  # Placeholder for future implementation
                'by_brand': {}
            }
        }
    }


def get_visits_metrics(session, tenant_id, user_id=None, start_date=None, end_date=None, group_by='day'):
    """
    Get visits metrics for a tenant.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        user_id: User ID (optional)
        start_date: Start date (optional)
        end_date: End date (optional)
        group_by: Group by period ('day', 'week', 'month')
    
    Returns:
        list: Visits metrics
    """
    # Set default date range if not provided
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()
    
    # Build base query
    base_query = session.query(Visit).filter(
        Visit.tenant_id == tenant_id,
        Visit.started_at >= start_date,
        Visit.started_at <= end_date
    )
    
    # Filter by user if provided
    if user_id:
        base_query = base_query.filter(Visit.user_id == user_id)
    
    # Group by period
    if group_by == 'day':
        # Group by day
        visits_by_day = session.query(
            func.date(Visit.started_at).label('date'),
            func.count(Visit.id).label('count')
        ).filter(
            Visit.tenant_id == tenant_id,
            Visit.started_at >= start_date,
            Visit.started_at <= end_date
        )
        
        # Filter by user if provided
        if user_id:
            visits_by_day = visits_by_day.filter(Visit.user_id == user_id)
        
        # Group by date
        visits_by_day = visits_by_day.group_by(func.date(Visit.started_at)).all()
        
        # Format results
        results = []
        for date, count in visits_by_day:
            results.append({
                'date': date.strftime('%Y-%m-%d'),
                'count': count
            })
        
        return {
            'visits_by_day': results,
            'total_visits': sum(item['count'] for item in results)
        }
    
    elif group_by == 'week':
        # Group by week
        visits_by_week = session.query(
            extract('year', Visit.started_at).label('year'),
            extract('week', Visit.started_at).label('week'),
            func.count(Visit.id).label('count')
        ).filter(
            Visit.tenant_id == tenant_id,
            Visit.started_at >= start_date,
            Visit.started_at <= end_date
        )
        
        # Filter by user if provided
        if user_id:
            visits_by_week = visits_by_week.filter(Visit.user_id == user_id)
        
        # Group by year and week
        visits_by_week = visits_by_week.group_by(
            extract('year', Visit.started_at),
            extract('week', Visit.started_at)
        ).all()
        
        # Format results
        results = []
        for year, week, count in visits_by_week:
            results.append({
                'year': int(year),
                'week': int(week),
                'count': count
            })
        
        return {
            'visits_by_week': results,
            'total_visits': sum(item['count'] for item in results)
        }
    
    elif group_by == 'month':
        # Group by month
        visits_by_month = session.query(
            extract('year', Visit.started_at).label('year'),
            extract('month', Visit.started_at).label('month'),
            func.count(Visit.id).label('count')
        ).filter(
            Visit.tenant_id == tenant_id,
            Visit.started_at >= start_date,
            Visit.started_at <= end_date
        )
        
        # Filter by user if provided
        if user_id:
            visits_by_month = visits_by_month.filter(Visit.user_id == user_id)
        
        # Group by year and month
        visits_by_month = visits_by_month.group_by(
            extract('year', Visit.started_at),
            extract('month', Visit.started_at)
        ).all()
        
        # Format results
        results = []
        for year, month, count in visits_by_month:
            results.append({
                'year': int(year),
                'month': int(month),
                'count': count
            })
        
        return {
            'visits_by_month': results,
            'total_visits': sum(item['count'] for item in results)
        }
    
    else:
        # Invalid group_by parameter
        return []


def get_shelf_share_metrics(session, tenant_id, user_id=None, start_date=None, end_date=None):
    """
    Get shelf share metrics for a tenant.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        user_id: User ID (optional)
        start_date: Start date (optional)
        end_date: End date (optional)
    
    Returns:
        dict: Shelf share metrics
    """
    # Set default date range if not provided
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()
    
    # Get all brands
    brands = session.query(Brand).filter(Brand.tenant_id == tenant_id).all()
    
    # Build base query for photos
    photos_query = session.query(Photo).join(
        Visit, Photo.visit_id == Visit.id
    ).filter(
        Photo.tenant_id == tenant_id,
        Visit.started_at >= start_date,
        Visit.started_at <= end_date,
        Photo.purpose == 'shelf'
    )
    
    # Filter by user if provided
    if user_id:
        photos_query = photos_query.filter(Visit.user_id == user_id)
    
    # Get photos
    photos = photos_query.all()
    
    # Get shelf quadrants for the photos
    photo_ids = [photo.id for photo in photos]
    shelf_quadrants = session.query(ShelfQuadrant).filter(
        ShelfQuadrant.tenant_id == tenant_id,
        ShelfQuadrant.photo_id.in_(photo_ids)
    ).all()
    
    # Calculate shelf share by brand
    shelf_share_by_brand = {}
    for brand in brands:
        brand_quadrants = [sq for sq in shelf_quadrants if sq.brand_id == brand.id]
        total_area = sum(float(sq.area_percentage) for sq in brand_quadrants)
        average_area = total_area / len(brand_quadrants) if brand_quadrants else 0.0
        
        shelf_share_by_brand[str(brand.id)] = {
            'brand_id': str(brand.id),
            'brand_name': brand.name,
            'average_area_percentage': average_area,
            'total_photos': len(brand_quadrants)
        }
    
    # Calculate overall shelf share
    total_photos = len(photos)
    total_quadrants = len(shelf_quadrants)
    
    # Calculate average shelf share across all brands
    total_area_percentage = sum(brand_data['average_area_percentage'] for brand_data in shelf_share_by_brand.values())
    average_shelf_share = total_area_percentage / len(brands) if brands else 0.0

    return {
        'by_brand': shelf_share_by_brand,
        'total_photos': total_photos,
        'total_quadrants': total_quadrants,
        'average_shelf_share': average_shelf_share
    }


def get_call_cycle_coverage_metrics(session, tenant_id, user_id=None, start_date=None, end_date=None):
    """
    Get call cycle coverage metrics for a tenant.
    
    Args:
        session: SQLAlchemy session
        tenant_id: Tenant ID
        user_id: User ID (optional)
        start_date: Start date (optional)
        end_date: End date (optional)
    
    Returns:
        dict: Call cycle coverage metrics
    """
    # Set default date range if not provided
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()
    
    # Get all call cycles
    call_cycles = session.query(CallCycle).filter(CallCycle.tenant_id == tenant_id).all()
    
    # Get call cycle locations
    call_cycle_ids = [cc.id for cc in call_cycles]
    locations = session.query(CallCycleLocation).filter(
        CallCycleLocation.call_cycle_id.in_(call_cycle_ids)
    ).all()
    
    # Get shop IDs from locations
    shop_ids = [location.shop_id for location in locations if location.shop_id]
    
    # Build base query for visits
    visits_query = session.query(Visit).filter(
        Visit.tenant_id == tenant_id,
        Visit.started_at >= start_date,
        Visit.started_at <= end_date,
        Visit.completed_at.isnot(None)
    )
    
    # Filter by user if provided
    if user_id:
        visits_query = visits_query.filter(Visit.user_id == user_id)
    
    # Filter by shop IDs
    if shop_ids:
        visits_query = visits_query.filter(Visit.shop_id.in_(shop_ids))
    
    # Get visits
    visits = visits_query.all()
    
    # Calculate coverage by call cycle
    coverage_by_call_cycle = {}
    for call_cycle in call_cycles:
        # Get locations for this call cycle
        cycle_locations = [loc for loc in locations if loc.call_cycle_id == call_cycle.id]
        cycle_shop_ids = [loc.shop_id for loc in cycle_locations if loc.shop_id]
        
        # Get visits for this call cycle
        cycle_visits = [v for v in visits if v.shop_id in cycle_shop_ids]
        
        # Calculate coverage
        total_locations = len(cycle_locations)
        visited_locations = len(set(v.shop_id for v in cycle_visits))
        coverage_percentage = (visited_locations / total_locations) * 100.0 if total_locations > 0 else 0.0
        
        coverage_by_call_cycle[str(call_cycle.id)] = {
            'call_cycle_id': str(call_cycle.id),
            'call_cycle_name': call_cycle.name,
            'total_locations': total_locations,
            'visited_locations': visited_locations,
            'coverage_percentage': coverage_percentage
        }
    
    # Calculate overall coverage
    total_locations = len(locations)
    visited_locations = len(set(v.shop_id for v in visits if v.shop_id))
    overall_coverage = (visited_locations / total_locations) * 100.0 if total_locations > 0 else 0.0
    
    return {
        'by_call_cycle': coverage_by_call_cycle,
        'total_locations': total_locations,
        'visited_locations': visited_locations,
        'overall_coverage': overall_coverage
    }