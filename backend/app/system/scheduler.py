"""
Scheduler - time-based trigger for batch processing (daily/hourly).
"""
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Callable
from ..config import settings


class BatchScheduler:
    """
    Scheduler for automatic batch processing.
    Triggers compression at configured intervals.
    """
    
    def __init__(self):
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._interval_minutes = settings.BATCH_INTERVAL_MINUTES
        self._next_run: Optional[datetime] = None
        self._last_run: Optional[datetime] = None
    
    async def start(self):
        """Start the scheduler."""
        self._running = True
        self._calculate_next_run()
        self._task = asyncio.create_task(self._run_loop())
    
    async def stop(self):
        """Stop the scheduler."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
    
    async def _run_loop(self):
        """Main scheduler loop."""
        while self._running:
            try:
                if self._should_run():
                    await self._trigger_batch()
            except Exception as e:
                print(f"Scheduler error: {e}")
            
            # Check every minute
            await asyncio.sleep(60)
    
    def _should_run(self) -> bool:
        """Check if it's time to run."""
        if not self._next_run:
            return False
        return datetime.utcnow() >= self._next_run
    
    def _calculate_next_run(self):
        """Calculate next run time."""
        self._next_run = datetime.utcnow() + timedelta(minutes=self._interval_minutes)
    
    async def _trigger_batch(self):
        """Trigger batch processing."""
        from .batch import batch_processor
        from .monitor import system_monitor
        
        try:
            await batch_processor.force_compress()
            self._last_run = datetime.utcnow()
            self._calculate_next_run()
            system_monitor.increment_batches()
        except Exception as e:
            print(f"Scheduled batch error: {e}")
    
    def get_next_run(self) -> Optional[datetime]:
        """Get next scheduled run time."""
        return self._next_run
    
    def get_last_run(self) -> Optional[datetime]:
        """Get last run time."""
        return self._last_run
    
    async def run_now(self):
        """Manually trigger a batch immediately."""
        await self._trigger_batch()


# Global scheduler
batch_scheduler = BatchScheduler()