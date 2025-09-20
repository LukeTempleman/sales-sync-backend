from sqlalchemy import Column, String, Boolean, ForeignKey, UniqueConstraint
from models.base import UUID
from sqlalchemy.orm import relationship

from models.base import BaseModel, TenantScopedMixin


class Brand(BaseModel, TenantScopedMixin):
    """Brand model."""
    __tablename__ = 'brands'
    
    name = Column(String, nullable=False)
    slug = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    
    # Relationships
    infographics = relationship('BrandInfographic', back_populates='brand', cascade='all, delete-orphan')
    
    __table_args__ = (
        UniqueConstraint('tenant_id', 'name', name='uq_brand_tenant_name'),
    )
    
    def to_dict(self, include_infographics=False):
        """Convert model to dictionary."""
        result = {
            'id': str(self.id),
            'tenant_id': str(self.tenant_id),
            'name': self.name,
            'slug': self.slug,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_infographics:
            result['infographics'] = [infographic.to_dict() for infographic in self.infographics]
        
        return result


class BrandInfographic(BaseModel, TenantScopedMixin):
    """Brand infographic model."""
    __tablename__ = 'brand_infographics'
    
    brand_id = Column(UUID(as_uuid=True), ForeignKey('brands.id', ondelete='CASCADE'), nullable=False)
    file_url = Column(String, nullable=False)
    caption = Column(String, nullable=True)
    
    # Relationships
    brand = relationship('Brand', back_populates='infographics')
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': str(self.id),
            'tenant_id': str(self.tenant_id),
            'brand_id': str(self.brand_id),
            'file_url': self.file_url,
            'caption': self.caption,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }