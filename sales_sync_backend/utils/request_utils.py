"""Request utilities for the API."""
import json
from flask import request, jsonify, g
from marshmallow import ValidationError
from flask_jwt_extended import get_jwt, get_jwt_identity


def get_request_data():
    """Get request data from JSON body."""
    if not request.is_json:
        return None
    return request.get_json()


def validate_request_data(schema):
    """Validate request data against schema."""
    data = get_request_data()
    if data is None:
        return None, jsonify({"error": "Invalid JSON or missing request body"}), 400
    
    try:
        validated_data = schema().load(data)
        return validated_data, None, None
    except ValidationError as err:
        return None, jsonify({"error": "Validation error", "details": err.messages}), 400


def get_pagination_params():
    """Get pagination parameters from request."""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        return page, per_page
    except ValueError:
        return 1, 20


def get_filter_params():
    """Get filter parameters from request."""
    filters = {}
    for key, value in request.args.items():
        if key not in ['page', 'per_page', 'sort', 'order']:
            filters[key] = value
    return filters


def get_sort_params():
    """Get sort parameters from request."""
    sort = request.args.get('sort', 'created_at')
    order = request.args.get('order', 'desc')
    return sort, order


def paginate_response(items, total, page, per_page):
    """Create a paginated response."""
    return {
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    }


def get_tenant_id_from_jwt():
    """Get tenant_id from JWT claims."""
    try:
        claims = get_jwt()
        return claims.get('tenant_id')
    except Exception:
        return None


def get_user_id_from_jwt():
    """Get user_id from JWT identity."""
    try:
        return get_jwt_identity()
    except Exception:
        return None


def get_roles_from_jwt():
    """Get roles from JWT claims."""
    try:
        claims = get_jwt()
        return claims.get('roles', [])
    except Exception:
        return []


def has_role(role):
    """Check if user has a specific role."""
    roles = get_roles_from_jwt()
    return role in roles