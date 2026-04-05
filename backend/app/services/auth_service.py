"""
Auth service - authentication business logic.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from ..models import User
from ..utils.security import hash_password, verify_password, create_access_token
from ..utils.avatar import generate_avatar


class AuthService:
    """Authentication business logic."""

    @staticmethod
    async def register_user(db: AsyncSession, username: str, email: str, password: str) -> User:
        """Register a new user."""
        # Check existing
        result = await db.execute(select(User).where(User.email == email))
        if result.scalar_one_or_none():
            raise ValueError("Email already registered")
        
        result = await db.execute(select(User).where(User.username == username))
        if result.scalar_one_or_none():
            raise ValueError("Username taken")
        
        # Create
        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            display_name=username,
            avatar=await generate_avatar(username, username),
            status="offline"
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def login_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
        """Login user by email/password."""
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user or not verify_password(password, user.password_hash):
            return None
        
        user.status = "online"
        await db.commit()
        return user

    @staticmethod
    def generate_token(user: User) -> str:
        """Generate JWT token for user."""
        return create_access_token({"sub": user.id, "username": user.username})

    @staticmethod
    async def logout_user(db: AsyncSession, user_id: str) -> bool:
        """Logout user."""
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if user:
            user.status = "offline"
            await db.commit()
            return True
        return False