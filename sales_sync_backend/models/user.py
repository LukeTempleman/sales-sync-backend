from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from models.base import UUID
from sqlalchemy.orm import relationship

from models.base import BaseModel, TenantScopedMixin, TimestampMixin


class User(BaseModel, TenantScopedMixin, TimestampMixin):
    """User model."""
    __tablename__ = 'users'
    
    email = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    last_login_at = Column(DateTime, nullable=True)
    
    # Relationships
    roles = relationship('Role', secondary='user_roles')
    teams = relationship('Team', secondary='user_teams')
    
    __table_args__ = (
        UniqueConstraint('tenant_id', 'email', name='uq_user_tenant_email'),
    )
    
    def to_dict(self, include_roles=True):
        """Convert model to dictionary."""
        result = {
            'id': str(self.id),
            'tenant_id': str(self.tenant_id),
            'email': self.email,
            'phone': self.phone,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None
        }
        
        if include_roles:
            result['roles'] = [role.name for role in self.roles]
        
        return result