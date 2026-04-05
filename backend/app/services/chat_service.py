"""
Chat service - message handling and queue push.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import Optional, List
from datetime import datetime

from ..models import Message, User
from ..utils.formatter import clean_message


class ChatService:
    """Chat business logic."""

    @staticmethod
    async def send_message(
        db: AsyncSession,
        sender_id: str,
        content: str,
        receiver_id: Optional[str] = None,
        group_id: Optional[str] = None,
        message_type: str = "text"
    ) -> Message:
        """Send a message (queued for batch processing)."""
        # Clean content
        content = clean_message(content)
        
        # Create message (initially uncompressed)
        message = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            group_id=group_id,
            content=content,
            type=message_type,
            compressed=False
        )
        
        db.add(message)
        await db.commit()
        await db.refresh(message)
        
        # TODO: Push to async queue for batch processing
        # from ..system.queue import message_queue
        # await message_queue.push(message)
        
        return message

    @staticmethod
    async def get_private_messages(
        db: AsyncSession,
        user_id: str,
        other_user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Message]:
        """Get private messages between two users."""
        result = await db.execute(
            select(Message).where(
                and_(
                    or_(
                        and_(Message.sender_id == user_id, Message.receiver_id == other_user_id),
                        and_(Message.sender_id == other_user_id, Message.receiver_id == user_id)
                    ),
                    Message.group_id.is_(None),
                    Message.is_deleted == False
                )
            ).order_by(Message.created_at.desc()).limit(limit).offset(offset)
        )
        return result.scalars().all()

    @staticmethod
    async def delete_message(db: AsyncSession, message_id: str, user_id: str) -> bool:
        """Delete a message (soft delete)."""
        result = await db.execute(
            select(Message).where(
                and_(Message.id == message_id, Message.sender_id == user_id)
            )
        )
        message = result.scalar_one_or_none()
        
        if not message:
            return False
        
        message.is_deleted = True
        message.deleted_at = datetime.utcnow()
        await db.commit()
        return True

    @staticmethod
    async def get_conversations(db: AsyncSession, user_id: str) -> List[dict]:
        """Get list of conversations for a user."""
        # Get recent private conversations
        result = await db.execute(
            select(Message).where(
                or_(
                    Message.sender_id == user_id,
                    Message.receiver_id == user_id
                )
            ).order_by(Message.created_at.desc()).limit(100)
        )
        messages = result.scalars().all()
        
        # Group by conversation partner
        conversations = {}
        for msg in messages:
            partner_id = msg.receiver_id if msg.sender_id == user_id else msg.sender_id
            if partner_id and partner_id not in conversations:
                conversations[partner_id] = {
                    "user_id": partner_id,
                    "last_message": msg.content[:50],
                    "last_time": msg.created_at
                }
        
        return list(conversations.values())[:20]