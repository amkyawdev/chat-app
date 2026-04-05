"""
Avatar utilities - auto-generate avatars for users.
"""
import hashlib
import base64
from typing import Optional
from io import BytesIO
import json


def generate_avatar_seed(user_id: str) -> str:
    """Generate a deterministic seed from user ID for avatar."""
    return hashlib.md5(user_id.encode()).hexdigest()[:16]


def get_avatar_color(user_id: str) -> tuple:
    """Generate a consistent color from user ID (RGB)."""
    seed = generate_avatar_seed(user_id)
    # Generate consistent color based on seed
    r = int(seed[0:2], 16) % 200 + 30  # Avoid too dark
    g = int(seed[2:4], 16) % 200 + 30
    b = int(seed[4:6], 16) % 200 + 30
    return (r, g, b)


def get_avatar_initials(username: str) -> str:
    """Get initials from username for avatar display."""
    if not username:
        return "?"
    parts = username.split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    return username[:2].upper()


def generate_identicon(user_id: str) -> str:
    """
    Generate a simple identicon (base64 encoded).
    In production, use a proper library or service.
    """
    # Simplified placeholder - returns a colored background URL
    color = get_avatar_color(user_id)
    # In production: generate actual identicon or use a service like DiceBear
    return f"https://api.dicebear.com/7.x/initials/svg?seed={user_id}"


async def generate_avatar(user_id: str, username: str) -> str:
    """
    Generate an avatar URL for a user.
    Can be customized to use different styles or services.
    """
    # Using DiceBear API for automatic avatar generation
    # Options: 'initials', 'identicon', 'bottts', 'avataaars', etc.
    return f"https://api.dicebear.com/7.x/initials/svg?seed={username}&backgroundColor={get_avatar_color(user_id)}"