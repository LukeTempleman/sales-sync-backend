from sqlalchemy import Column, String, UniqueConstraint
from models.base import UUID

from models.base import BaseModel


class Tenant(BaseModel):
    """Tenant model for multi-tenancy."""
    __tablename__ = 'tenants'
    
    name = Column(String, nullable=False)
    subdomain = Column(String, nullable=True, unique=True)
    
    __table_args__ = (
        UniqueConstraint('name', name='uq_tenant_name'),
    )
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': str(self.id),
            'name': self.name,
            'subdomain': self.subdomain,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }