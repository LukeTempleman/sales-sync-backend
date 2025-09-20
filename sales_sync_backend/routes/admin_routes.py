from flask import Blueprint

from controllers.admin_controller import (
    get_user_activity_handler,
    get_survey_completion_rates_handler,
    get_tenant_audit_logs_handler,
    get_all_audit_logs_handler
)

# Create blueprints
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')
audit_bp = Blueprint('audit', __name__, url_prefix='/api/audit')

# Register admin routes
admin_bp.route('/users/activity', methods=['GET'])(get_user_activity_handler)
admin_bp.route('/surveys/completion', methods=['GET'])(get_survey_completion_rates_handler)

# Register audit routes
audit_bp.route('', methods=['GET'])(get_tenant_audit_logs_handler)
audit_bp.route('/all', methods=['GET'])(get_all_audit_logs_handler)