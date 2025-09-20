from sqlalchemy import Column, String, ForeignKey, Numeric, Date
from models.base import UUID, JSONB
from sqlalchemy.orm import relationship

from models.base import BaseModel, TenantScopedMixin


class Goal(BaseModel, TenantScopedMixin):
    """Goal model."""
    __tablename__ = 'goals'
    
    name = Column(String, nullable=False)
    metric = Column(String, nullable=False)  # 'visits', 'conversions', 'shelf_share', etc
    target_value = Column(Numeric, nullable=True)
    period = Column(String, nullable=False)  # 'daily', 'weekly', 'monthly', 'quarterly'
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    
    # Relationships
    assignments = relationship('GoalAssignment', back_populates='goal', cascade='all, delete-orphan')
    
    def to_dict(self, include_assignments=False):
        """Convert model to dictionary."""
        result = {
            'id': str(self.id),
            'tenant_id': str(self.tenant_id),
            'name': self.name,
            'metric': self.metric,
            'target_value': float(self.target_value) if self.target_value is not None else None,
            'period': self.period,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_assignments:
            result['assignments'] = [assignment.to_dict() for assignment in self.assignments]
        
        return result


class GoalAssignment(BaseModel):
    """Goal assignment model."""
    __tablename__ = 'goals_assignments'
    
    goal_id = Column(UUID(as_uuid=True), ForeignKey('goals.id', ondelete='CASCADE'), nullable=False)
    assignee_type = Column(String, nullable=False)  # 'user' or 'team'
    assignee_id = Column(UUID(as_uuid=True), nullable=False)  # user.id or team.id
    progress = Column(JSONB, nullable=True)
    
    # Relationships
    goal = relationship('Goal', back_populates='assignments')
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': str(self.id),
            'goal_id': str(self.goal_id),
            'assignee_type': self.assignee_type,
            'assignee_id': str(self.assignee_id),
            'progress': self.progress,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }