from flask import g
from sqlalchemy.orm.query import Query

def tenant_scoped_query(query, model):
    """
    Apply tenant_id filter to query if model has tenant_id attribute.
    
    Args:
        query: SQLAlchemy query object
        model: SQLAlchemy model class
    
    Returns:
        SQLAlchemy query with tenant_id filter applied
    """
    if hasattr(model, 'tenant_id') and g.tenant_id:
        return query.filter(model.tenant_id == g.tenant_id)
    return query


def get_tenant_id():
    """
    Get tenant_id from Flask g object.
    
    Returns:
        tenant_id: UUID or None
    """
    return g.tenant_id if hasattr(g, 'tenant_id') else None


class TenantScopedQuery(Query):
    """
    Custom SQLAlchemy Query class that automatically applies tenant_id filter.
    """
    def get(self, ident):
        """
        Override get method to apply tenant_id filter.
        
        Args:
            ident: Primary key value
        
        Returns:
            Model instance or None
        """
        # Get model class from query
        model = self._mapper_zero().class_
        
        # Apply tenant_id filter if model has tenant_id attribute
        if hasattr(model, 'tenant_id') and g.tenant_id:
            return self.filter(model.tenant_id == g.tenant_id).filter(model.id == ident).first()
        
        return super().get(ident)
    
    def __iter__(self):
        """
        Override __iter__ method to apply tenant_id filter.
        
        Returns:
            Iterator over query results
        """
        # Get model class from query
        model = self._mapper_zero().class_
        
        # Apply tenant_id filter if model has tenant_id attribute
        if hasattr(model, 'tenant_id') and g.tenant_id:
            return super(TenantScopedQuery, self).filter(model.tenant_id == g.tenant_id).__iter__()
        
        return super().__iter__()