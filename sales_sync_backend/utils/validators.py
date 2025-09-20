import re
from marshmallow import Schema, fields, validate, ValidationError

# Email validation regex
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# Password validation regex (min 8 chars, at least 1 letter and 1 number)
PASSWORD_REGEX = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$'

def validate_email(email):
    """Validate email format."""
    if not re.match(EMAIL_REGEX, email):
        raise ValidationError('Invalid email format')
    return email

def validate_password(password):
    """Validate password strength."""
    if not re.match(PASSWORD_REGEX, password):
        raise ValidationError('Password must be at least 8 characters and contain at least one letter and one number')
    return password

# Common schema fields
class UUIDField(fields.UUID):
    """UUID field with validation."""
    def _deserialize(self, value, attr, data, **kwargs):
        try:
            return super()._deserialize(value, attr, data, **kwargs)
        except ValidationError:
            raise ValidationError('Invalid UUID format')

# Auth schemas
class RegisterSchema(Schema):
    """Schema for user registration."""
    email = fields.Email(required=True, validate=validate_email)
    password = fields.Str(required=True, validate=validate_password)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    phone = fields.Str(required=False)
    tenant_name = fields.Str(required=True)
    subdomain = fields.Str(required=False)

class LoginSchema(Schema):
    """Schema for user login."""
    email = fields.Email(required=True, validate=validate_email)
    password = fields.Str(required=True)

class ForgotPasswordSchema(Schema):
    """Schema for forgot password."""
    email = fields.Email(required=True, validate=validate_email)

class ResetPasswordSchema(Schema):
    """Schema for reset password."""
    token = fields.Str(required=True)
    password = fields.Str(required=True, validate=validate_password)

# User schemas
class UserCreateSchema(Schema):
    """Schema for creating a user."""
    email = fields.Email(required=True, validate=validate_email)
    password = fields.Str(required=True, validate=validate_password)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    phone = fields.Str(required=False)
    roles = fields.List(fields.Str(), required=False)

class UserUpdateSchema(Schema):
    """Schema for updating a user."""
    email = fields.Email(required=False, validate=validate_email)
    first_name = fields.Str(required=False)
    last_name = fields.Str(required=False)
    phone = fields.Str(required=False)
    is_active = fields.Boolean(required=False)

# Brand schemas
class BrandSchema(Schema):
    """Schema for brand operations."""
    name = fields.Str(required=True)
    slug = fields.Str(required=False)
    active = fields.Boolean(required=False)
    
class BrandCreateSchema(BrandSchema):
    """Schema for creating a brand."""
    pass
    
class BrandUpdateSchema(BrandSchema):
    """Schema for updating a brand."""
    pass
    
class BrandInfographicSchema(Schema):
    """Schema for brand infographics."""
    file_url = fields.Str(required=True)
    caption = fields.Str(required=False)

# Survey schemas
class SurveyQuestionSchema(Schema):
    """Schema for survey question."""
    question_text = fields.Str(required=True)
    input_type = fields.Str(required=True, validate=validate.OneOf(['text', 'select', 'boolean', 'photo', 'number']))
    meta = fields.Dict(required=False)
    order_num = fields.Int(required=False)

class SurveySchema(Schema):
    """Schema for survey operations."""
    name = fields.Str(required=True)
    type = fields.Str(required=True, validate=validate.OneOf(['individual', 'shop']))
    brand_id = UUIDField(required=False, allow_none=True)
    active = fields.Boolean(required=False)
    questions = fields.List(fields.Nested(SurveyQuestionSchema), required=False)

# Visit schemas
class VisitCreateSchema(Schema):
    """Schema for creating a visit."""
    survey_id = UUIDField(required=True)
    visit_type = fields.Str(required=True, validate=validate.OneOf(['individual', 'shop']))
    geocode = fields.Dict(required=False)
    shop_id = UUIDField(required=False, allow_none=True)

class VisitAnswerSchema(Schema):
    """Schema for visit answer."""
    question_id = UUIDField(required=True)
    answer_text = fields.Str(required=False, allow_none=True)
    answer_json = fields.Dict(required=False, allow_none=True)

class VisitCompleteSchema(Schema):
    """Schema for completing a visit."""
    answers = fields.List(fields.Nested(VisitAnswerSchema), required=False)
    photos = fields.List(fields.Dict(), required=False)

# Photo schemas
class PhotoSchema(Schema):
    """Schema for photo operations."""
    visit_id = UUIDField(required=True)
    purpose = fields.Str(required=False)
    metadata = fields.Dict(required=False)

class ShelfQuadrantSchema(Schema):
    """Schema for shelf quadrant operations."""
    brand_id = UUIDField(required=True)
    quadrant_coords = fields.Dict(required=True)
    area_percentage = fields.Float(required=False)

# Goal schemas
class GoalSchema(Schema):
    """Schema for goal operations."""
    name = fields.Str(required=True)
    metric = fields.Str(required=True)
    target_value = fields.Float(required=False)
    period = fields.Str(required=True, validate=validate.OneOf(['daily', 'weekly', 'monthly', 'quarterly']))
    start_date = fields.Date(required=False)
    end_date = fields.Date(required=False)

class GoalAssignmentSchema(Schema):
    """Schema for goal assignment operations."""
    assignee_type = fields.Str(required=True, validate=validate.OneOf(['user', 'team']))
    assignee_id = UUIDField(required=True)

# Call cycle schemas
class CallCycleSchema(Schema):
    """Schema for call cycle operations."""
    name = fields.Str(required=True)
    frequency = fields.Str(required=True, validate=validate.OneOf(['daily', 'weekly', 'monthly']))

class CallCycleLocationSchema(Schema):
    """Schema for call cycle location operations."""
    location = fields.Dict(required=False)
    shop_id = UUIDField(required=False, allow_none=True)
    order_num = fields.Int(required=False)

# Team schemas
class TeamSchema(Schema):
    """Schema for team operations."""
    name = fields.Str(required=True)
    manager_id = UUIDField(required=False, allow_none=True)

class TeamMemberSchema(Schema):
    """Schema for team member operations."""
    user_id = UUIDField(required=True)
    
# Tenant schemas
class TenantSchema(Schema):
    """Schema for tenant operations."""
    name = fields.Str(required=True)
    subdomain = fields.Str(required=False, allow_none=True)
    
# User schemas
class UserSchema(Schema):
    """Schema for user operations."""
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    phone = fields.Str(required=False, allow_none=True)
    is_active = fields.Bool(required=False, default=True)
    tenant_id = UUIDField(required=False, allow_none=True)
    roles = fields.List(fields.Str(), required=False, default=[])
    
# Role schemas
class RoleSchema(Schema):
    """Schema for role operations."""
    name = fields.Str(required=True)
    
# Brand schemas
class BrandSchema(Schema):
    """Schema for brand operations."""
    name = fields.Str(required=True)
    slug = fields.Str(required=False, allow_none=True)
    active = fields.Bool(required=False, default=True)
    
class BrandInfographicSchema(Schema):
    """Schema for brand infographic operations."""
    brand_id = UUIDField(required=True)
    file_url = fields.Str(required=True)
    caption = fields.Str(required=False, allow_none=True)
    
# Survey schemas
class SurveySchema(Schema):
    """Schema for survey operations."""
    name = fields.Str(required=True)
    type = fields.Str(required=True)
    brand_id = UUIDField(required=False, allow_none=True)
    active = fields.Bool(required=False, default=True)
    
class SurveyQuestionSchema(Schema):
    """Schema for survey question operations."""
    survey_id = UUIDField(required=True)
    question_text = fields.Str(required=True)
    input_type = fields.Str(required=True)
    meta = fields.Dict(required=False, allow_none=True)
    order_num = fields.Int(required=False, default=0)
    
# Visit schemas
class VisitSchema(Schema):
    """Schema for visit operations."""
    survey_id = UUIDField(required=True)
    visit_type = fields.Str(required=True)
    geocode = fields.Dict(required=False, allow_none=True)
    shop_id = UUIDField(required=False, allow_none=True)
    
class VisitAnswerSchema(Schema):
    """Schema for visit answer operations."""
    visit_id = UUIDField(required=True)
    question_id = UUIDField(required=True)
    answer_text = fields.Str(required=False, allow_none=True)
    answer_json = fields.Dict(required=False, allow_none=True)
    
# Photo schemas
class PhotoSchema(Schema):
    """Schema for photo operations."""
    visit_id = UUIDField(required=True)
    file_url = fields.Str(required=True)
    purpose = fields.Str(required=False, allow_none=True)
    image_metadata = fields.Dict(required=False, allow_none=True)
    
class ShelfQuadrantSchema(Schema):
    """Schema for shelf quadrant operations."""
    photo_id = UUIDField(required=True)
    brand_id = UUIDField(required=True)
    quadrant_coords = fields.Dict(required=True)
    area_percentage = fields.Float(required=False, allow_none=True)
    
# Goal schemas
class GoalSchema(Schema):
    """Schema for goal operations."""
    name = fields.Str(required=True)
    metric = fields.Str(required=True)
    target_value = fields.Float(required=True)
    period = fields.Str(required=True)
    start_date = fields.Date(required=False, allow_none=True)
    end_date = fields.Date(required=False, allow_none=True)
    
class GoalAssignmentSchema(Schema):
    """Schema for goal assignment operations."""
    goal_id = UUIDField(required=True)
    assignee_type = fields.Str(required=True)
    assignee_id = UUIDField(required=True)
    progress = fields.Dict(required=False, allow_none=True)
    
# Call cycle schemas
class CallCycleSchema(Schema):
    """Schema for call cycle operations."""
    name = fields.Str(required=True)
    frequency = fields.Str(required=True)
    
class CallCycleLocationSchema(Schema):
    """Schema for call cycle location operations."""
    call_cycle_id = UUIDField(required=True)
    location = fields.Dict(required=True)
    shop_id = UUIDField(required=False, allow_none=True)
    order_num = fields.Int(required=False, default=0)
    
# Team schemas
class TeamSchema(Schema):
    """Schema for team operations."""
    name = fields.Str(required=True)
    manager_id = UUIDField(required=False, allow_none=True)
    
class UserTeamSchema(Schema):
    """Schema for user team operations."""
    user_id = UUIDField(required=True)
    team_id = UUIDField(required=True)
    
# Audit schemas
class AuditLogSchema(Schema):
    """Schema for audit log operations."""
    tenant_id = UUIDField(required=False, allow_none=True)
    user_id = UUIDField(required=False, allow_none=True)
    action = fields.Str(required=True)
    object_type = fields.Str(required=False, allow_none=True)
    object_id = UUIDField(required=False, allow_none=True)
    metadata = fields.Dict(required=False, allow_none=True)