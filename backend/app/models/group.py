"""
Group model - represents chat groups.
"""
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Boolean, Integer
from sqlalchemy.sql import func
from ..dependencies import Base
import uuid


class Group(Base):
    """Chat group model."""

    __tablename__ = "groups"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    avatar = Column(Text, nullable=True)
    
    # Admin (owner)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Settings
    is_private = Column(Boolean, default=False)
    max_members = Column(Integer, default=100)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Group {self.name}>"


class GroupMember(Base):
    """Group member with roles."""

    __tablename__ = "group_members"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    group_id = Column(String, ForeignKey("groups.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Role: 'admin', 'co_admin', 'member'
    role = Column(String(20), default="member")
    
    # Custom nickname in group
    nickname = Column(String(50), nullable=True)
    
    # Mute notifications?
    is_muted = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    
    # Timestamps
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<GroupMember {self.user_id} in {self.group_id}>"