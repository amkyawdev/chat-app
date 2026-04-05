"""
Message queue - buffer system for async message processing.
"""
from typing import Optional, List
from collections import deque
import asyncio
import json
from datetime import datetime


class MessageQueue:
    """
    In-memory message queue with async support.
    In production, use Redis for distributed processing.
    """
    
    def __init__(self, max_size: int = 10000):
        self._queue = deque()
        self._max_size = max_size
        self._lock = asyncio.Lock()
    
    async def enqueue(self, message) -> bool:
        """
        Add a message to the queue.
        
        Args:
            message: Message object to queue
            
        Returns:
            True if enqueued successfully
        """
        async with self._lock:
            if len(self._queue) >= self._max_size:
                return False
            
            # Serialize message for storage
            msg_data = {
                "id": message.id,
                "sender_id": message.sender_id,
                "receiver_id": message.receiver_id,
                "group_id": message.group_id,
                "content": message.content,
                "type": message.type,
                "created_at": message.created_at.isoformat() if message.created_at else None
            }
            self._queue.append(msg_data)
            return True
    
    async def dequeue(self) -> Optional[dict]:
        """
        Remove and return the oldest message from queue.
        
        Returns:
            Message data dict or None if empty
        """
        async with self._lock:
            if not self._queue:
                return None
            return self._queue.popleft()
    
    async def peek(self) -> Optional[dict]:
        """View the oldest message without removing it."""
        async with self._lock:
            if not self._queue:
                return None
            return self._queue[0]
    
    async def get_batch(self, size: int = 100) -> List[dict]:
        """Get multiple messages at once for batch processing."""
        async with self._lock:
            batch = []
            for _ in range(min(size, len(self._queue))):
                if self._queue:
                    batch.append(self._queue.popleft())
            return batch
    
    async def clear(self):
        """Clear all messages from queue."""
        async with self._lock:
            self._queue.clear()
    
    def size(self) -> int:
        """Get current queue size (non-async)."""
        return len(self._queue)
    
    async def is_empty(self) -> bool:
        """Check if queue is empty."""
        async with self._lock:
            return len(self._queue) == 0


# Global queue instance
message_queue = MessageQueue()