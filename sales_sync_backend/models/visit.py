from sqlalchemy import Column, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship

from models.base import BaseModel, TenantScopedMixin, UUID, JSONB, Geography


class Visit(BaseModel, TenantScopedMixin):
    """Visit model."""
    __tablename__ = 'visits'
    
    survey_id = Column(UUID(as_uuid=True), ForeignKey('surveys.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    visit_type = Column(String, nullable=False)  # 'individual' or 'shop'
    geocode = Column(Geography('POINT', srid=4326), nullable=True)
    shop_id = Column(UUID(as_uuid=True), nullable=True)  # Optional reference to shop
    started_at = Column(DateTime, default=None, nullable=True)
    completed_at = Column(DateTime, default=None, nullable=True)
    
    # Relationships
    answers = relationship('VisitAnswer', back_populates='visit', cascade='all, delete-orphan')
    photos = relationship('Photo', back_populates='visit', cascade='all, delete-orphan')
    
    def to_dict(self, include_answers=False, include_photos=False):
        """Convert model to dictionary."""
        result = {
            'id': str(self.id),
            'tenant_id': str(self.tenant_id),
            'survey_id': str(self.survey_id),
            'user_id': str(self.user_id),
            'visit_type': self.visit_type,
            'shop_id': str(self.shop_id) if self.shop_id else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_answers:
            result['answers'] = [answer.to_dict() for answer in self.answers]
        
        if include_photos:
            result['photos'] = [photo.to_dict() for photo in self.photos]
        
        return result


class VisitAnswer(BaseModel, TenantScopedMixin):
    """Visit answer model."""
    __tablename__ = 'visit_answers'
    
    visit_id = Column(UUID(as_uuid=True), ForeignKey('visits.id', ondelete='CASCADE'), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey('survey_questions.id'), nullable=True)
    answer_text = Column(Text, nullable=True)
    answer_json = Column(JSONB, nullable=True)
    
    # Relationships
    visit = relationship('Visit', back_populates='answers')
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': str(self.id),
            'tenant_id': str(self.tenant_id),
            'visit_id': str(self.visit_id),
            'question_id': str(self.question_id) if self.question_id else None,
            'answer_text': self.answer_text,
            'answer_json': self.answer_json,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }