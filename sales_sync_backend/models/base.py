import uuid
from datetime import datetime
import os
import json
from sqlalchemy import Column, DateTime, String, TypeDecorator, Text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID, JSONB as PostgresJSONB
from sqlalchemy.ext.declarative import declared_attr

from models import Base

# Custom JSONB type that works with both PostgreSQL and SQLite
class JSONB(TypeDecorator):
    impl = Text
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return json.dumps(value)
    
    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return json.loads(value)

# Custom Geography type that works with both PostgreSQL and SQLite
class Geography(TypeDecorator):
    impl = Text
    
    def __init__(self, geometry_type='POINT', srid=4326, **kwargs):
        self.geometry_type = geometry_type
        self.srid = srid
        super().__init__(**kwargs)
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return json.dumps(value)
    
    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return json.loads(value)

# Custom UUID type that works with both PostgreSQL and SQLite
class UUID(TypeDecorator):
    impl = String
    
    def __init__(self, as_uuid=False):
        self.as_uuid = as_uuid
        super().__init__(36)
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return str(value)
        return value
    
    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if self.as_uuid:
            return uuid.UUID(value)
        return value


class TenantScopedMixin:
    """Mixin for tenant-scoped models."""
    
    @declared_attr
    def tenant_id(cls):
        return Column(UUID(as_uuid=True), nullable=False, index=True)


class BaseModel(Base):
    """Base model for all tables."""
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)


class TimestampMixin:
    """Mixin for models with created_at and updated_at."""
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)