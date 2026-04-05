"""
User routes - profile, avatar, block user.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import Optional, List
from datetime import datetime

from ..dependencies import get_db, get_current_user
from ..models import User, Friend
from ..utils.avatar import generate_avatar

router = APIRouter(prefix="/users", tags=["User"])


# --- Schemas ---
class UserProfileResponse(BaseModel):
    id: str
    username: str
    email: str
    display_name: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None
    status: str
    is_public: bool = True
    created_at: datetime


class UpdateProfileRequest(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    is_public: Optional[bool] = None
    allow_friends: Optional[bool] = None


class BlockUserRequest(BaseModel):
    user_id: str


class FriendRequest(BaseModel):
    user_id: str


# --- Routes ---
@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a user's public profile."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user allows public profile
    if not user.is_public and user.id != current_user["id"]:
        raise HTTPException(status_code=403, detail="This profile is private")
    
    return UserProfileResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        display_name=user.display_name,
        avatar=user.avatar,
        bio=user.bio,
        status=user.status,
        is_public=user.is_public,
        created_at=user.created_at
    )


@router.put("/profile", response_model=UserProfileResponse)
async def update_profile(
    request: UpdateProfileRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's profile."""
    result = await db.execute(select(User).where(User.id == current_user["id"]))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields
    if request.display_name is not None:
        user.display_name = request.display_name
    if request.bio is not None:
        user.bio = request.bio
    if request.is_public is not None:
        user.is_public = request.is_public
    if request.allow_friends is not None:
        user.allow_friends = request.allow_friends
    
    await db.commit()
    await db.refresh(user)
    
    return UserProfileResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        display_name=user.display_name,
        avatar=user.avatar,
        bio=user.bio,
        status=user.status,
        is_public=user.is_public,
        created_at=user.created_at
    )


@router.put("/avatar")
async def update_avatar(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update avatar (auto-generate or custom URL)."""
    result = await db.execute(select(User).where(User.id == current_user["id"]))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate new avatar based on username
    user.avatar = await generate_avatar(user.id, user.username)
    await db.commit()
    
    return {"avatar": user.avatar}


@router.post("/block")
async def block_user(
    request: BlockUserRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Block a user (add to blocked list)."""
    # In a real implementation, this would create a BlockedUser record
    # For now, return success
    return {"message": f"User {request.user_id} blocked"}


@router.post("/unblock")
async def unblock_user(
    request: BlockUserRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Unblock a user."""
    return {"message": f"User {request.user_id} unblocked"}


@router.get("/search/{query}")
async def search_users(
    query: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Search users by username or display name."""
    result = await db.execute(
        select(User).where(
            or_(
                User.username.ilike(f"%{query}%"),
                User.display_name.ilike(f"%{query}%")
            )
        ).limit(20)
    )
    users = result.scalars().all()
    
    return [
        {
            "id": u.id,
            "username": u.username,
            "display_name": u.display_name,
            "avatar": u.avatar,
            "status": u.status
        }
        for u in users
    ]