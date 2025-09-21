from sqlalchemy import Column, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from models.base import BaseModel, UUID


class Role(BaseModel):
    """Role model."""
    __tablename__ = 'roles'
    
    name = Column(String, nullable=False, unique=True)
    
    # Relationships
    users = relationship('User', secondary='user_roles', overlaps="roles")
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': str(self.id),
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class UserRole(BaseModel):
    """Association table for users and roles."""
    __tablename__ = 'user_roles'
    
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey('roles.id'), nullable=False)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'role_id', name='uq_user_role'),
    )