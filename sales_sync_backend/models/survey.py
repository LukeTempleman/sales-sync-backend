from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Text
from models.base import UUID, JSONB
from sqlalchemy.orm import relationship

from models.base import BaseModel, TenantScopedMixin


class Survey(BaseModel, TenantScopedMixin):
    """Survey model."""
    __tablename__ = 'surveys'
    
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # 'individual' or 'shop'
    brand_id = Column(UUID(as_uuid=True), ForeignKey('brands.id'), nullable=True)
    active = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    # Relationships
    questions = relationship('SurveyQuestion', back_populates='survey', cascade='all, delete-orphan')
    
    def to_dict(self, include_questions=False):
        """Convert model to dictionary."""
        result = {
            'id': str(self.id),
            'tenant_id': str(self.tenant_id),
            'name': self.name,
            'type': self.type,
            'brand_id': str(self.brand_id) if self.brand_id else None,
            'active': self.active,
            'created_by': str(self.created_by) if self.created_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_questions:
            result['questions'] = [question.to_dict() for question in sorted(self.questions, key=lambda q: q.order_num)]
        
        return result


class SurveyQuestion(BaseModel, TenantScopedMixin):
    """Survey question model."""
    __tablename__ = 'survey_questions'
    
    survey_id = Column(UUID(as_uuid=True), ForeignKey('surveys.id', ondelete='CASCADE'), nullable=False)
    question_text = Column(Text, nullable=False)
    input_type = Column(String, nullable=False)  # 'text', 'select', 'boolean', 'photo', 'number'
    meta = Column(JSONB, nullable=True)  # Store choices, validation rules, help_text
    order_num = Column(Integer, default=0)
    
    # Relationships
    survey = relationship('Survey', back_populates='questions')
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': str(self.id),
            'tenant_id': str(self.tenant_id),
            'survey_id': str(self.survey_id),
            'question_text': self.question_text,
            'input_type': self.input_type,
            'meta': self.meta,
            'order_num': self.order_num,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }