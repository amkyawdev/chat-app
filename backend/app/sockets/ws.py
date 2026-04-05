"""
WebSocket handler - real-time notifications (optional).
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict
import json
import asyncio


class ConnectionManager:
    """Manage WebSocket connections."""
    
    def __init__(self):
        # user_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, user_id: str, websocket: WebSocket):
        """Accept and store a WebSocket connection."""
        await websocket.accept()
        self.active_connections[user_id] = websocket
    
    def disconnect(self, user_id: str):
        """Remove a connection."""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
    
    async def send_personal(self, user_id: str, message: dict):
        """Send message to specific user."""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(json.dumps(message))
            except Exception:
                self.disconnect(user_id)
    
    async def broadcast(self, message: dict):
        """Broadcast to all connected users."""
        for ws in list(self.active_connections.values()):
            try:
                await ws.send_text(json.dumps(message))
            except Exception:
                pass


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time notifications.
    
    Events:
    - new_message: New message received
    - message_deleted: Message was deleted
    - friend_request: New friend request
    - group_invite: Group invitation
    """
    await manager.connect(user_id, websocket)
    try:
        while True:
            # Keep connection alive, listen for client messages
            data = await websocket.receive_text()
            # Could handle client acknowledgments here
            pass
    except WebSocketDisconnect:
        manager.disconnect(user_id)


async def notify_new_message(receiver_id: str, message: dict):
    """Notify user of new message."""
    await manager.send_personal(receiver_id, {
        "type": "new_message",
        "data": message
    })


async def notify_friend_request(user_id: str, request: dict):
    """Notify user of friend request."""
    await manager.send_personal(user_id, {
        "type": "friend_request",
        "data": request
    })


async def notify_group_invite(user_id: str, invite: dict):
    """Notify user of group invite."""
    await manager.send_personal(user_id, {
        "type": "group_invite",
        "data": invite
    })