from flask import Blueprint

from controllers.tenants_controller import (
    get_tenants_handler,
    create_tenant_handler,
    get_tenant_handler,
    update_tenant_handler
)

# Create blueprint
tenants_bp = Blueprint('tenants', __name__, url_prefix='/api/tenants')

# Register routes
tenants_bp.route('', methods=['GET'])(get_tenants_handler)
tenants_bp.route('', methods=['POST'])(create_tenant_handler)
tenants_bp.route('/<uuid:tenant_id>', methods=['GET'])(get_tenant_handler)
tenants_bp.route('/<uuid:tenant_id>', methods=['PUT'])(update_tenant_handler)