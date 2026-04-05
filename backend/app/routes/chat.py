"""
Chat routes - send messages, delete, reactions.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import Optional, List
from datetime import datetime
import uuid

from ..dependencies import get_db, get_current_user
from ..models import Message, Reaction, User
from ..utils.formatter import clean_message

router = APIRouter(prefix="/chat", tags=["Chat"])


# --- Schemas ---
class SendMessageRequest(BaseModel):
    receiver_id: Optional[str] = None
    group_id: Optional[str] = None
    content: str
    type: str = "text"  # text, image, file


class MessageResponse(BaseModel):
    id: str
    sender_id: str
    receiver_id: Optional[str] = None
    group_id: Optional[str] = None
    type: str
    content: str
    is_deleted: bool
    created_at: datetime


class ReactionRequest(BaseModel):
    message_id: str
    emoji: str


class ReactionResponse(BaseModel):
    id: str
    message_id: str
    user_id: str
    emoji: str
    created_at: datetime


# --- Routes ---
@router.post("/send", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    request: SendMessageRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a message to a user or group."""
    # Validate - must have either receiver_id or group_id
    if not request.receiver_id and not request.group_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must specify receiver_id or group_id"
        )
    
    if request.receiver_id and request.group_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot send to both receiver and group"
        )
    
    # Clean message content
    content = clean_message(request.content)
    
    # Create message
    message = Message(
        sender_id=current_user["id"],
        receiver_id=request.receiver_id,
        group_id=request.group_id,
        content=content,
        type=request.type,
        compressed=False
    )
    
    db.add(message)
    await db.commit()
    await db.refresh(message)
    
    # TODO: Push to async queue for batch processing
    # await queue.push_message(message)
    
    return MessageResponse(
        id=message.id,
        sender_id=message.sender_id,
        receiver_id=message.receiver_id,
        group_id=message.group_id,
        type=message.type,
        content=message.content,
        is_deleted=message.is_deleted,
        created_at=message.created_at
    )


@router.get("/messages/{user_id}")
async def get_private_messages(
    user_id: str,
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get private messages between current user and another user."""
    result = await db.execute(
        select(Message).where(
            and_(
                or_(
                    and_(Message.sender_id == current_user["id"], Message.receiver_id == user_id),
                    and_(Message.sender_id == user_id, Message.receiver_id == current_user["id"])
                ),
                Message.group_id.is_(None),
                Message.is_deleted == False
            )
        ).order_by(Message.created_at.desc()).limit(limit).offset(offset)
    )
    messages = result.scalars().all()
    
    return [
        {
            "id": m.id,
            "sender_id": m.sender_id,
            "receiver_id": m.receiver_id,
            "content": m.content,
            "type": m.type,
            "created_at": m.created_at.isoformat()
        }
        for m in messages
    ]


@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a message (soft delete)."""
    result = await db.execute(
        select(Message).where(
            and_(Message.id == message_id, Message.sender_id == current_user["id"])
        )
    )
    message = result.scalar_one_or_none()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found or not authorized")
    
    message.is_deleted = True
    message.deleted_at = datetime.utcnow()
    await db.commit()
    
    return {"message": "Message deleted"}


@router.post("/reactions", response_model=ReactionResponse)
async def add_reaction(
    request: ReactionRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add an emoji reaction to a message."""
    # Verify message exists
    result = await db.execute(select(Message).where(Message.id == request.message_id))
    message = result.scalar_one_or_none()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Check if user already reacted with this emoji
    result = await db.execute(
        select(Reaction).where(
            and_(
                Reaction.message_id == request.message_id,
                Reaction.user_id == current_user["id"],
                Reaction.emoji == request.emoji
            )
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=400, detail="Reaction already exists")
    
    # Create reaction
    reaction = Reaction(
        message_id=request.message_id,
        user_id=current_user["id"],
        emoji=request.emoji
    )
    
    db.add(reaction)
    await db.commit()
    await db.refresh(reaction)
    
    return ReactionResponse(
        id=reaction.id,
        message_id=reaction.message_id,
        user_id=reaction.user_id,
        emoji=reaction.emoji,
        created_at=reaction.created_at
    )


@router.delete("/reactions/{reaction_id}")
async def remove_reaction(
    reaction_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove a reaction."""
    result = await db.execute(
        select(Reaction).where(
            and_(Reaction.id == reaction_id, Reaction.user_id == current_user["id"])
        )
    )
    reaction = result.scalar_one_or_none()
    
    if not reaction:
        raise HTTPException(status_code=404, detail="Reaction not found")
    
    await db.delete(reaction)
    await db.commit()
    
    return {"message": "Reaction removed"}


@router.get("/messages/{message_id}/reactions")
async def get_message_reactions(
    message_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all reactions on a message."""
    result = await db.execute(
        select(Reaction).where(Reaction.message_id == message_id)
    )
    reactions = result.scalars().all()
    
    # Group by emoji
    emoji_counts = {}
    for r in reactions:
        if r.emoji not in emoji_counts:
            emoji_counts[r.emoji] = {"count": 0, "users": []}
        emoji_counts[r.emoji]["count"] += 1
        emoji_counts[r.emoji]["users"].append(r.user_id)
    
    return emoji_counts