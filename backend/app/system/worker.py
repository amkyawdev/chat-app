"""
Worker - process messages from queue (clean, group, compress).
"""
import asyncio
from typing import Optional, List
from datetime import datetime

from .queue import message_queue
from .batch import BatchProcessor
from .monitor import SystemMonitor


class Worker:
    """
    Background worker that processes messages from queue.
    Handles cleaning, grouping, and preparing for compression.
    """
    
    def __init__(self):
        self.batch_processor = BatchProcessor()
        self.monitor = SystemMonitor()
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    async def start(self, interval_seconds: int = 5):
        """
        Start the worker process.
        
        Args:
            interval_seconds: How often to check queue
        """
        self._running = True
        self._task = asyncio.create_task(self._run_loop(interval_seconds))
    
    async def stop(self):
        """Stop the worker."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
    
    async def _run_loop(self, interval: int):
        """Main worker loop."""
        while self._running:
            try:
                await self._process_queue()
            except Exception as e:
                self.monitor.log_error(f"Worker error: {e}")
            
            await asyncio.sleep(interval)
    
    async def _process_queue(self):
        """Process pending messages in queue."""
        # Get batch of messages
        messages = await message_queue.get_batch(size=100)
        
        if not messages:
            return
        
        # Process each message
        for msg_data in messages:
            try:
                # Clean and normalize message
                cleaned = await self._clean_message(msg_data)
                
                # Add to batch processor
                await self.batch_processor.add_message(cleaned)
                
                self.monitor.increment_processed()
            except Exception as e:
                self.monitor.log_error(f"Message processing error: {e}")
        
        # Check if batch is ready to compress
        await self._check_batch_ready()
    
    async def _clean_message(self, msg_data: dict) -> dict:
        """Clean and normalize message data."""
        # In production, use formatter.clean_message
        content = msg_data.get("content", "")
        
        # Basic cleaning
        cleaned_content = content.strip()
        
        return {
            **msg_data,
            "content": cleaned_content,
            "processed_at": datetime.utcnow().isoformat()
        }
    
    async def _check_batch_ready(self):
        """Check if batch is ready for compression."""
        if self.batch_processor.is_ready():
            await self.batch_processor.compress_and_save()


# Global worker instance
worker = Worker()