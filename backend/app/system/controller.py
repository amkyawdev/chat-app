"""
System controller - main entry point for async batch processing.
Receives messages and routes to appropriate handlers.
"""
from typing import Optional
from ..models import Message
from .queue import MessageQueue
from .batch import BatchProcessor
from .scheduler import BatchScheduler
from .monitor import SystemMonitor


class SystemController:
    """
    Main controller for async message processing.
    Coordinates queue, batch, scheduler, and monitoring.
    """
    
    def __init__(self):
        self.queue = MessageQueue()
        self.batch_processor = BatchProcessor()
        self.scheduler = BatchScheduler()
        self.monitor = SystemMonitor()
    
    async def receive_message(self, message: Message) -> bool:
        """
        Receive a message and add it to the processing queue.
        
        Args:
            message: Message to process
            
        Returns:
            True if queued successfully
        """
        try:
            await self.queue.enqueue(message)
            self.monitor.increment_queue_size()
            return True
        except Exception as e:
            self.monitor.log_error(f"Failed to queue message: {e}")
            return False
    
    async def trigger_batch(
        self,
        user_id: Optional[str] = None,
        group_id: Optional[str] = None
    ) -> dict:
        """
        Manually trigger batch processing.
        
        Args:
            user_id: Optional specific user to process
            group_id: Optional specific group to process
            
        Returns:
            Status dict with processing results
        """
        return await self.batch_processor.process_batch(user_id, group_id)
    
    async def get_status(self) -> dict:
        """Get system status."""
        return {
            "queue_size": self.queue.size(),
            "monitor": self.monitor.get_stats(),
            "scheduler_next": self.scheduler.get_next_run()
        }
    
    async def start_scheduler(self):
        """Start the batch scheduler."""
        await self.scheduler.start()
    
    async def stop_scheduler(self):
        """Stop the batch scheduler."""
        await self.scheduler.stop()


# Global controller instance
controller = SystemController()