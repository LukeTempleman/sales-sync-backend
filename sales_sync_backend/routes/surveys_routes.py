from flask import Blueprint

from controllers.surveys_controller import (
    get_surveys_handler,
    get_survey_handler,
    create_survey_handler,
    update_survey_handler,
    delete_survey_handler,
    get_survey_questions_handler,
    create_question_handler,
    update_question_handler,
    delete_question_handler
)

# Create blueprint
surveys_bp = Blueprint('surveys', __name__, url_prefix='/api/surveys')
questions_bp = Blueprint('questions', __name__, url_prefix='/api/questions')

# Register survey routes
surveys_bp.route('', methods=['GET'])(get_surveys_handler)
surveys_bp.route('', methods=['POST'])(create_survey_handler)
surveys_bp.route('/<uuid:survey_id>', methods=['GET'])(get_survey_handler)
surveys_bp.route('/<uuid:survey_id>', methods=['PUT'])(update_survey_handler)
surveys_bp.route('/<uuid:survey_id>', methods=['DELETE'])(delete_survey_handler)
surveys_bp.route('/<uuid:survey_id>/questions', methods=['GET'])(get_survey_questions_handler)
surveys_bp.route('/<uuid:survey_id>/questions', methods=['POST'])(create_question_handler)

# Register question routes
questions_bp.route('/<uuid:question_id>', methods=['PUT'])(update_question_handler)
questions_bp.route('/<uuid:question_id>', methods=['DELETE'])(delete_question_handler)