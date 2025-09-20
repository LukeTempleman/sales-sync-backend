from sqlalchemy import Column, String, Text
from models.base import UUID, JSONB

from models.base import BaseModel


class AuditLog(BaseModel):
    """Audit log model."""
    __tablename__ = 'audit_logs'
    
    tenant_id = Column(UUID(as_uuid=True), nullable=True)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    action = Column(String, nullable=False)
    object_type = Column(String, nullable=True)
    object_id = Column(UUID(as_uuid=True), nullable=True)
    audit_metadata = Column(JSONB, nullable=True)
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': str(self.id),
            'tenant_id': str(self.tenant_id) if self.tenant_id else None,
            'user_id': str(self.user_id) if self.user_id else None,
            'action': self.action,
            'object_type': self.object_type,
            'object_id': str(self.object_id) if self.object_id else None,
            'metadata': self.audit_metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }