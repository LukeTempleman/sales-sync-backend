from sqlalchemy import Column, String, ForeignKey, Numeric
from models.base import UUID, JSONB
from sqlalchemy.orm import relationship

from models.base import BaseModel, TenantScopedMixin


class Photo(BaseModel, TenantScopedMixin):
    """Photo model."""
    __tablename__ = 'photos'
    
    visit_id = Column(UUID(as_uuid=True), ForeignKey('visits.id', ondelete='CASCADE'), nullable=False)
    file_url = Column(String, nullable=False)
    purpose = Column(String, nullable=True)  # 'id', 'shelf', 'outside', 'board'
    image_metadata = Column(JSONB, nullable=True)  # width/height/orientation etc
    
    # Relationships
    visit = relationship('Visit', back_populates='photos')
    shelf_quadrants = relationship('ShelfQuadrant', back_populates='photo', cascade='all, delete-orphan')
    
    def to_dict(self, include_quadrants=False):
        """Convert model to dictionary."""
        result = {
            'id': str(self.id),
            'tenant_id': str(self.tenant_id),
            'visit_id': str(self.visit_id),
            'file_url': self.file_url,
            'purpose': self.purpose,
            'metadata': self.image_metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_quadrants:
            result['shelf_quadrants'] = [quadrant.to_dict() for quadrant in self.shelf_quadrants]
        
        return result


class ShelfQuadrant(BaseModel, TenantScopedMixin):
    """Shelf quadrant model."""
    __tablename__ = 'shelf_quadrants'
    
    photo_id = Column(UUID(as_uuid=True), ForeignKey('photos.id', ondelete='CASCADE'), nullable=False)
    brand_id = Column(UUID(as_uuid=True), ForeignKey('brands.id'), nullable=False)
    quadrant_coords = Column(JSONB, nullable=True)  # list of marked quadrants / polygons
    area_percentage = Column(Numeric, nullable=True)  # calculated share %
    
    # Relationships
    photo = relationship('Photo', back_populates='shelf_quadrants')
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': str(self.id),
            'tenant_id': str(self.tenant_id),
            'photo_id': str(self.photo_id),
            'brand_id': str(self.brand_id),
            'quadrant_coords': self.quadrant_coords,
            'area_percentage': float(self.area_percentage) if self.area_percentage is not None else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }