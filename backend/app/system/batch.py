"""
Batch builder - groups messages and compresses them.
"""
import json
from typing import List, Optional
from pathlib import Path
from datetime import datetime
import uuid

from ..config import settings
from ..utils.compression import compress_zstd
from ..utils.time import get_date_path, utc_timestamp
from ..services.file_service import FileService


class BatchProcessor:
    """
    Batch processor - groups messages by user/project/time and compresses.
    """
    
    def __init__(self, max_size_mb: int = 10):
        self._max_size_bytes = max_size_mb * 1024 * 1024
        self._current_batch: List[dict] = []
        self._current_size = 0
        self._batch_id = str(uuid.uuid4())[:8]
        self._file_service = FileService()
    
    async def add_message(self, message: dict) -> bool:
        """
        Add a message to the current batch.
        
        Args:
            message: Cleaned message dict
            
        Returns:
            True if added, False if batch is full
        """
        msg_size = len(json.dumps(message).encode())
        
        # Check if adding would exceed limit
        if self._current_size + msg_size > self._max_size_bytes:
            # Compress current batch
            await self.compress_and_save()
            self._start_new_batch()
        
        self._current_batch.append(message)
        self._current_size += msg_size
        return True
    
    def is_ready(self) -> bool:
        """Check if batch is ready for compression."""
        # Ready if has messages and reaches size threshold (1MB)
        return len(self._current_batch) > 0 and self._current_size > 1024 * 1024
    
    async def compress_and_save(self) -> Optional[Path]:
        """
        Compress current batch and save to storage.
        
        Returns:
            Path to saved file or None on failure
        """
        if not self._current_batch:
            return None
        
        try:
            # Prepare batch data
            batch_data = {
                "batch_id": self._batch_id,
                "created_at": datetime.utcnow().isoformat(),
                "message_count": len(self._current_batch),
                "messages": self._current_batch
            }
            
            # Serialize and compress
            json_data = json.dumps(batch_data, ensure_ascii=False)
            compressed = compress_zstd(json_data.encode())
            
            # Generate filename
            timestamp = utc_timestamp()
            filename = f"{timestamp}_{self._batch_id}.zst"
            
            # Save to local storage
            # In production, use user_id from messages
            user_id = self._current_batch[0].get("sender_id", "default")
            project_id = "chat_messages"
            date_path = get_date_path()
            
            storage_path = self._file_service.get_local_storage_path(user_id, project_id, date_path)
            file_path = storage_path / filename
            
            with open(file_path, "wb") as f:
                f.write(compressed)
            
            # Create index file
            await self._save_index(storage_path, filename, batch_data)
            
            # Optionally upload to GitHub
            if settings.GITHUB_REPO:
                await self._file_service.upload_to_github(file_path, settings.GITHUB_REPO)
            
            self._start_new_batch()
            return file_path
        
        except Exception as e:
            print(f"Batch save error: {e}")
            return None
    
    async def _save_index(self, storage_path: Path, filename: str, batch_data: dict):
        """Save or update index.json for the directory."""
        index_path = storage_path / "index.json"
        
        index_data = []
        if index_path.exists():
            with open(index_path, "r") as f:
                index_data = json.load(f)
        
        index_data.append({
            "filename": filename,
            "batch_id": self._batch_id,
            "created_at": batch_data["created_at"],
            "message_count": batch_data["message_count"],
            "compressed_size": len(compress_zstd(json.dumps(batch_data).encode()))
        })
        
        with open(index_path, "w") as f:
            json.dump(index_data, f, indent=2)
    
    def _start_new_batch(self):
        """Start a new batch."""
        self._current_batch = []
        self._current_size = 0
        self._batch_id = str(uuid.uuid4())[:8]
    
    async def force_compress(self) -> Optional[Path]:
        """Force compress current batch even if not full."""
        if self._current_batch:
            return await self.compress_and_save()
        return None


# Global batch processor
batch_processor = BatchProcessor()