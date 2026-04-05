"""
Group routes - create groups, manage members, admin controls.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import Optional, List
from datetime import datetime
import uuid

from ..dependencies import get_db, get_current_user
from ..models import Group, GroupMember, User, Message

router = APIRouter(prefix="/groups", tags=["Group"])


# --- Schemas ---
class CreateGroupRequest(BaseModel):
    name: str
    description: Optional[str] = None
    is_private: bool = False
    max_members: int = 100


class UpdateGroupRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    avatar: Optional[str] = None


class GroupResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    avatar: Optional[str]
    owner_id: str
    is_private: bool
    max_members: int
    created_at: datetime


class AddMemberRequest(BaseModel):
    user_id: str
    role: str = "member"  # member, co_admin


class UpdateMemberRequest(BaseModel):
    nickname: Optional[str] = None
    role: Optional[str] = None
    is_muted: Optional[bool] = None


class MemberResponse(BaseModel):
    id: str
    user_id: str
    group_id: str
    role: str
    nickname: Optional[str]
    is_muted: bool
    joined_at: datetime


# --- Routes ---
@router.post("/", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    request: CreateGroupRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new chat group."""
    group = Group(
        name=request.name,
        description=request.description,
        owner_id=current_user["id"],
        is_private=request.is_private,
        max_members=request.max_members
    )
    
    db.add(group)
    await db.commit()
    await db.refresh(group)
    
    # Add creator as admin
    member = GroupMember(
        group_id=group.id,
        user_id=current_user["id"],
        role="admin"
    )
    db.add(member)
    await db.commit()
    
    return GroupResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        avatar=group.avatar,
        owner_id=group.owner_id,
        is_private=group.is_private,
        max_members=group.max_members,
        created_at=group.created_at
    )


@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(
    group_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get group details."""
    result = await db.execute(select(Group).where(Group.id == group_id))
    group = result.scalar_one_or_none()
    
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    return GroupResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        avatar=group.avatar,
        owner_id=group.owner_id,
        is_private=group.is_private,
        max_members=group.max_members,
        created_at=group.created_at
    )


@router.put("/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: str,
    request: UpdateGroupRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update group (admin only)."""
    # Check if user is admin
    result = await db.execute(
        select(GroupMember).where(
            and_(
                GroupMember.group_id == group_id,
                GroupMember.user_id == current_user["id"],
                GroupMember.role.in_(["admin", "co_admin"])
            )
        )
    )
    member = result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(select(Group).where(Group.id == group_id))
    group = result.scalar_one_or_none()
    
    if request.name:
        group.name = request.name
    if request.description is not None:
        group.description = request.description
    if request.avatar is not None:
        group.avatar = request.avatar
    
    await db.commit()
    await db.refresh(group)
    
    return GroupResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        avatar=group.avatar,
        owner_id=group.owner_id,
        is_private=group.is_private,
        max_members=group.max_members,
        created_at=group.created_at
    )


@router.delete("/{group_id}")
async def delete_group(
    group_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete group (owner only)."""
    result = await db.execute(select(Group).where(Group.id == group_id))
    group = result.scalar_one_or_none()
    
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    if group.owner_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Only owner can delete group")
    
    await db.delete(group)
    await db.commit()
    
    return {"message": "Group deleted"}


@router.get("/{group_id}/members")
async def get_group_members(
    group_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all group members."""
    result = await db.execute(
        select(GroupMember, User).join(User, GroupMember.user_id == User.id).where(
            GroupMember.group_id == group_id,
            GroupMember.is_banned == False
        )
    )
    members = result.all()
    
    return [
        {
            "id": m.GroupMember.id,
            "user_id": m.GroupMember.user_id,
            "username": m.User.username,
            "display_name": m.User.display_name,
            "avatar": m.User.avatar,
            "role": m.GroupMember.role,
            "nickname": m.GroupMember.nickname,
            "is_muted": m.GroupMember.is_muted,
            "joined_at": m.GroupMember.joined_at.isoformat()
        }
        for m in members
    ]


@router.post("/{group_id}/members", status_code=status.HTTP_201_CREATED)
async def add_member(
    group_id: str,
    request: AddMemberRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a member to group (admin only)."""
    # Check admin
    result = await db.execute(
        select(GroupMember).where(
            and_(
                GroupMember.group_id == group_id,
                GroupMember.user_id == current_user["id"],
                GroupMember.role.in_(["admin", "co_admin"])
            )
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check group exists
    result = await db.execute(select(Group).where(Group.id == group_id))
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check not already member
    result = await db.execute(
        select(GroupMember).where(
            and_(GroupMember.group_id == group_id, GroupMember.user_id == request.user_id)
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already a member")
    
    # Add member
    member = GroupMember(
        group_id=group_id,
        user_id=request.user_id,
        role=request.role
    )
    db.add(member)
    await db.commit()
    
    return {"message": "Member added"}


@router.delete("/{group_id}/members/{user_id}")
async def remove_member(
    group_id: str,
    user_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove a member from group (admin only)."""
    # Check admin or self-removal
    result = await db.execute(
        select(GroupMember).where(
            and_(
                GroupMember.group_id == group_id,
                GroupMember.user_id == current_user["id"],
                GroupMember.role.in_(["admin", "co_admin"])
            )
        )
    )
    is_admin = result.scalar_one_or_none() is not None
    
    if not is_admin and user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Find and remove member
    result = await db.execute(
        select(GroupMember).where(
            and_(GroupMember.group_id == group_id, GroupMember.user_id == user_id)
        )
    )
    member = result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    await db.delete(member)
    await db.commit()
    
    return {"message": "Member removed"}


@router.put("/{group_id}/members/{user_id}", response_model=MemberResponse)
async def update_member(
    group_id: str,
    user_id: str,
    request: UpdateMemberRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update member (nickname, role, mute) - admin only."""
    # Check admin
    result = await db.execute(
        select(GroupMember).where(
            and_(
                GroupMember.group_id == group_id,
                GroupMember.user_id == current_user["id"],
                GroupMember.role == "admin"
            )
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(
        select(GroupMember).where(
            and_(GroupMember.group_id == group_id, GroupMember.user_id == user_id)
        )
    )
    member = result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    if request.nickname is not None:
        member.nickname = request.nickname
    if request.role is not None:
        member.role = request.role
    if request.is_muted is not None:
        member.is_muted = request.is_muted
    
    await db.commit()
    
    return MemberResponse(
        id=member.id,
        user_id=member.user_id,
        group_id=member.group_id,
        role=member.role,
        nickname=member.nickname,
        is_muted=member.is_muted,
        joined_at=member.joined_at
    )


@router.get("/{group_id}/messages")
async def get_group_messages(
    group_id: str,
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get group messages."""
    result = await db.execute(
        select(Message).where(
            and_(
                Message.group_id == group_id,
                Message.is_deleted == False
            )
        ).order_by(Message.created_at.desc()).limit(limit).offset(offset)
    )
    messages = result.scalars().all()
    
    return [
        {
            "id": m.id,
            "sender_id": m.sender_id,
            "content": m.content,
            "type": m.type,
            "created_at": m.created_at.isoformat()
        }
        for m in messages
    ]