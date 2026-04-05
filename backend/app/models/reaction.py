"""
Reaction model - emoji/like reactions on messages.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..dependencies import Base
import uuid


class Reaction(Base):
    """Message reaction (emoji) model."""

    __tablename__ = "reactions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String, ForeignKey("messages.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Emoji: '👍', '❤️', '😂', '😢', '😮', '😡', etc.
    emoji = Column(String(10), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Reaction {self.emoji} on {self.message_id[:8]}>"