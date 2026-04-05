"""
Dependencies - shared FastAPI dependencies (auth, database, etc).
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import create_async_engine, select
from sqlalchemy.orm import sessionmaker, declarative_base

from .config import settings

# Security scheme
security = HTTPBearer()

# Database setup
engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


async def get_db() -> AsyncSession:
    """Database session dependency."""
    async with async_session() as session:
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Validate JWT token and return current user.
    In production, decode JWT and fetch user from DB.
    """
    # TODO: Implement actual JWT validation
    # For now, return a placeholder user
    token = credentials.credentials
    # This would decode the token and verify it
    return {"id": "user_placeholder", "username": "test_user"}


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[dict]:
    """Optional auth - returns None if not authenticated."""
    if not credentials:
        return None
    return await get_current_user(credentials)