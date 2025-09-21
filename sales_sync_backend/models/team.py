from sqlalchemy import Column, String, ForeignKey, UniqueConstraint
from models.base import UUID
from sqlalchemy.orm import relationship

from models.base import BaseModel, TenantScopedMixin


class Team(BaseModel, TenantScopedMixin):
    """Team model."""
    __tablename__ = 'teams'
    
    name = Column(String, nullable=False)
    manager_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    # Relationships
    users = relationship('User', secondary='user_teams', overlaps="teams")
    
    __table_args__ = (
        UniqueConstraint('tenant_id', 'name', name='uq_team_tenant_name'),
    )
    
    def to_dict(self, include_users=False):
        """Convert model to dictionary."""
        result = {
            'id': str(self.id),
            'tenant_id': str(self.tenant_id),
            'name': self.name,
            'manager_id': str(self.manager_id) if self.manager_id else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_users:
            result['users'] = [user.to_dict(include_roles=False) for user in self.users]
        
        return result


class UserTeam(BaseModel):
    """Association table for users and teams."""
    __tablename__ = 'user_teams'
    
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    team_id = Column(UUID(as_uuid=True), ForeignKey('teams.id', ondelete='CASCADE'), nullable=False)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'team_id', name='uq_user_team'),
    )