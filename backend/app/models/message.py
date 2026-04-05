"""
Message model - represents chat messages.
"""
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Boolean, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..dependencies import Base
import uuid


class Message(Base):
    """Chat message model."""

    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sender_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Message type: 'text', 'image', 'file', 'system'
    type = Column(String(20), default="text")
    
    # Content (text or file URL)
    content = Column(Text, nullable=False)
    
    # For private chat (user-to-user)
    receiver_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    
    # For group chat
    group_id = Column(String, ForeignKey("groups.id"), nullable=True, index=True)
    
    # Message status
    is_deleted = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    
    # Batch processing info
    batch_id = Column(String, nullable=True, index=True)
    compressed = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    # sender = relationship("User", back_populates="messages")
    # reactions = relationship("Reaction", back_populates="message")

    def __repr__(self):
        return f"<Message {self.id[:8]} from {self.sender_id[:8]}>"