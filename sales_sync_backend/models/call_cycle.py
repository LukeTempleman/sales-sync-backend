from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship

from models.base import BaseModel, TenantScopedMixin, UUID, Geography


class CallCycle(BaseModel, TenantScopedMixin):
    """Call cycle model."""
    __tablename__ = 'call_cycles'
    
    name = Column(String, nullable=False)
    frequency = Column(String, nullable=False)  # 'daily', 'weekly', 'monthly'
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    # Relationships
    locations = relationship('CallCycleLocation', back_populates='call_cycle', cascade='all, delete-orphan')
    
    def to_dict(self, include_locations=False):
        """Convert model to dictionary."""
        result = {
            'id': str(self.id),
            'tenant_id': str(self.tenant_id),
            'name': self.name,
            'frequency': self.frequency,
            'created_by': str(self.created_by) if self.created_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_locations:
            result['locations'] = [location.to_dict() for location in sorted(self.locations, key=lambda l: l.order_num)]
        
        return result


class CallCycleLocation(BaseModel):
    """Call cycle location model."""
    __tablename__ = 'call_cycle_locations'
    
    call_cycle_id = Column(UUID(as_uuid=True), ForeignKey('call_cycles.id', ondelete='CASCADE'), nullable=False)
    location = Column(Geography('POINT', srid=4326), nullable=True)
    shop_id = Column(UUID(as_uuid=True), nullable=True)  # Optional reference to shop
    order_num = Column(Integer, default=0)
    
    # Relationships
    call_cycle = relationship('CallCycle', back_populates='locations')
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': str(self.id),
            'call_cycle_id': str(self.call_cycle_id),
            'shop_id': str(self.shop_id) if self.shop_id else None,
            'order_num': self.order_num,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }