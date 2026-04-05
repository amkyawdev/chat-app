"""
Group service - group management business logic.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, List

from ..models import Group, GroupMember, User


class GroupService:
    """Group business logic."""

    @staticmethod
    async def create_group(
        db: AsyncSession,
        name: str,
        owner_id: str,
        description: Optional[str] = None,
        is_private: bool = False
    ) -> Group:
        """Create a new group."""
        group = Group(
            name=name,
            owner_id=owner_id,
            description=description,
            is_private=is_private
        )
        db.add(group)
        await db.commit()
        await db.refresh(group)
        
        # Add owner as admin
        member = GroupMember(
            group_id=group.id,
            user_id=owner_id,
            role="admin"
        )
        db.add(member)
        await db.commit()
        
        return group

    @staticmethod
    async def get_group(db: AsyncSession, group_id: str) -> Optional[Group]:
        """Get group by ID."""
        result = await db.execute(select(Group).where(Group.id == group_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def add_member(
        db: AsyncSession,
        group_id: str,
        user_id: str,
        role: str = "member"
    ) -> GroupMember:
        """Add a member to group."""
        # Check not already member
        result = await db.execute(
            select(GroupMember).where(
                and_(GroupMember.group_id == group_id, GroupMember.user_id == user_id)
            )
        )
        if result.scalar_one_or_none():
            raise ValueError("Already a member")
        
        member = GroupMember(
            group_id=group_id,
            user_id=user_id,
            role=role
        )
        db.add(member)
        await db.commit()
        await db.refresh(member)
        return member

    @staticmethod
    async def remove_member(db: AsyncSession, group_id: str, user_id: str) -> bool:
        """Remove a member from group."""
        result = await db.execute(
            select(GroupMember).where(
                and_(GroupMember.group_id == group_id, GroupMember.user_id == user_id)
            )
        )
        member = result.scalar_one_or_none()
        
        if not member:
            return False
        
        await db.delete(member)
        await db.commit()
        return True

    @staticmethod
    async def get_members(db: AsyncSession, group_id: str) -> List[GroupMember]:
        """Get all group members."""
        result = await db.execute(
            select(GroupMember).where(GroupMember.group_id == group_id)
        )
        return result.scalars().all()

    @staticmethod
    async def is_admin(db: AsyncSession, group_id: str, user_id: str) -> bool:
        """Check if user is admin or co_admin."""
        result = await db.execute(
            select(GroupMember).where(
                and_(
                    GroupMember.group_id == group_id,
                    GroupMember.user_id == user_id,
                    GroupMember.role.in_(["admin", "co_admin"])
                )
            )
        )
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def is_owner(db: AsyncSession, group_id: str, user_id: str) -> bool:
        """Check if user is owner."""
        result = await db.execute(select(Group).where(Group.id == group_id))
        group = result.scalar_one_or_none()
        return group and group.owner_id == user_id

    @staticmethod
    async def update_member_role(
        db: AsyncSession,
        group_id: str,
        user_id: str,
        new_role: str
    ) -> bool:
        """Update member role (admin only)."""
        result = await db.execute(
            select(GroupMember).where(
                and_(GroupMember.group_id == group_id, GroupMember.user_id == user_id)
            )
        )
        member = result.scalar_one_or_none()
        
        if not member:
            return False
        
        member.role = new_role
        await db.commit()
        return True