"""
Friend model - represents friend relationships between users.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.sql import func
from ..dependencies import Base
import uuid
import enum


class FriendStatus(enum.Enum):
    """Friend request status."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    BLOCKED = "blocked"


class Friend(Base):
    """Friend relationship model."""

    __tablename__ = "friends"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # User who initiated the friend request
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # User who received the request
    friend_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Status: pending, accepted, blocked
    status = Column(String(20), default="pending")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    accepted_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<Friend {self.user_id} <-> {self.friend_id}>"