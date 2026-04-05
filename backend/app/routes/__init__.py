"""
Routes package - API endpoints.
"""
from .auth import router as auth_router
from .user import router as user_router
from .chat import router as chat_router
from .group import router as group_router
from .system import router as system_router

__all__ = ["auth_router", "user_router", "chat_router", "group_router", "system_router"]