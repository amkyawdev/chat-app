"""
User service - user profile management.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import Optional, List

from ..models import User, Friend
from ..utils.avatar import generate_avatar


class UserService:
    """User business logic."""

    @staticmethod
    async def get_user(db: AsyncSession, user_id: str) -> Optional[User]:
        """Get user by ID."""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email."""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """Get user by username."""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_profile(
        db: AsyncSession,
        user_id: str,
        display_name: Optional[str] = None,
        bio: Optional[str] = None,
        is_public: Optional[bool] = None
    ) -> Optional[User]:
        """Update user profile."""
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        if display_name is not None:
            user.display_name = display_name
        if bio is not None:
            user.bio = bio
        if is_public is not None:
            user.is_public = is_public
        
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def update_avatar(db: AsyncSession, user_id: str) -> Optional[str]:
        """Generate and update avatar."""
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        user.avatar = await generate_avatar(user.id, user.username)
        await db.commit()
        return user.avatar

    @staticmethod
    async def search_users(db: AsyncSession, query: str, limit: int = 20) -> List[User]:
        """Search users by username or display name."""
        result = await db.execute(
            select(User).where(
                or_(
                    User.username.ilike(f"%{query}%"),
                    User.display_name.ilike(f"%{query}%")
                )
            ).limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def add_friend(db: AsyncSession, user_id: str, friend_id: str) -> Friend:
        """Send friend request."""
        # Check not already friends
        result = await db.execute(
            select(Friend).where(
                or_(
                    and_(Friend.user_id == user_id, Friend.friend_id == friend_id),
                    and_(Friend.user_id == friend_id, Friend.friend_id == user_id)
                )
            )
        )
        if result.scalar_one_or_none():
            raise ValueError("Already friends or request pending")
        
        friend = Friend(
            user_id=user_id,
            friend_id=friend_id,
            status="pending"
        )
        db.add(friend)
        await db.commit()
        await db.refresh(friend)
        return friend

    @staticmethod
    async def accept_friend(db: AsyncSession, user_id: str, friend_id: str) -> bool:
        """Accept friend request."""
        result = await db.execute(
            select(Friend).where(
                and_(Friend.user_id == friend_id, Friend.friend_id == user_id, Friend.status == "pending")
            )
        )
        friend = result.scalar_one_or_none()
        
        if not friend:
            return False
        
        friend.status = "accepted"
        await db.commit()
        return True

    @staticmethod
    async def get_friends(db: AsyncSession, user_id: str) -> List[User]:
        """Get user's friends."""
        result = await db.execute(
            select(Friend).where(
                or_(
                    and_(Friend.user_id == user_id, Friend.status == "accepted"),
                    and_(Friend.friend_id == user_id, Friend.status == "accepted")
                )
            )
        )
        friends = result.scalars().all()
        
        friend_ids = []
        for f in friends:
            if f.user_id == user_id:
                friend_ids.append(f.friend_id)
            else:
                friend_ids.append(f.user_id)
        
        result = await db.execute(select(User).where(User.id.in_(friend_ids)))
        return result.scalars().all()