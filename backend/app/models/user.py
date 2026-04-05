"""
User model - represents a user in the chat system.
"""
from sqlalchemy import Column, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from ..dependencies import Base
import uuid


class User(Base):
    """User account model."""

    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    # Profile
    display_name = Column(String(100), nullable=True)
    avatar = Column(Text, nullable=True)  # URL or base64
    bio = Column(Text, nullable=True)
    status = Column(String(20), default="offline")  # online, offline, away

    # Settings
    is_public = Column(Boolean, default=True)  # Public profile?
    allow_friends = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_seen = Column(DateTime(timezone=True), nullable=True)

    # Blocked users (relationship defined elsewhere)
    # blocked_users = relationship("BlockedUser", back_populates="user")

    def __repr__(self):
        return f"<User {self.username}>"