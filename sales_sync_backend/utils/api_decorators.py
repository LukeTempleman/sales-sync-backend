"""
Decorators for API routes to document them with OpenAPI.
"""
import functools
from flask import request
from utils.api_docs import spec


def document_api(
    tags=None,
    summary=None,
    description=None,
    request_schema=None,
    response_schema=None,
    responses=None,
    security=None,
    deprecated=False,
):
    """
    Decorator to document API routes with OpenAPI.
    
    Args:
        tags: List of tags for the operation
        summary: Summary of the operation
        description: Description of the operation
        request_schema: Schema for the request body
        response_schema: Schema for the response body
        responses: Dictionary of responses
        security: List of security requirements
        deprecated: Whether the operation is deprecated
    
    Returns:
        Decorated function
    """
    if tags is None:
        tags = []
    if responses is None:
        responses = {}
    if security is None:
        security = [{"bearerAuth": []}]
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # Get the route path and method
        path = request.url_rule.rule
        method = request.method.lower()
        
        # Create operation object
        operation = {
            "tags": tags,
            "summary": summary,
            "description": description,
            "deprecated": deprecated,
        }
        
        # Add request body if provided
        if request_schema:
            operation["requestBody"] = {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": request_schema,
                    }
                },
            }
        
        # Add responses
        operation["responses"] = responses
        if response_schema and "200" not in responses and "201" not in responses:
            operation["responses"]["200"] = {
                "description": "Successful response",
                "content": {
                    "application/json": {
                        "schema": response_schema,
                    }
                },
            }
        
        # Add security
        operation["security"] = security
        
        # Register the operation with APISpec
        spec.path(path=path, operations={method: operation})
        
        return wrapper
    
    return decorator