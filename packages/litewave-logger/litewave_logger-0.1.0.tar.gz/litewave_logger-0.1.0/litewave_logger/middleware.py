import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from . import request_id_var

# This middleware is used to handle the request ID.
# It checks for a 'X-Request-ID' header in the incoming request.
# If the header is present, its value is used as the request ID.
# If not, a new UUID is generated.
# The request ID is then stored in a context variable.
class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware to handle the request ID.
    It checks for a 'X-Request-ID' header in the incoming request.
    If the header is present, its value is used as the request ID.
    If not, a new UUID is generated.
    The request ID is then stored in a context variable.
    """
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid.uuid4())
        
        request_id_var.set(request_id)
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id_var.get()
        return response

__all__ = ["RequestIdMiddleware"]
