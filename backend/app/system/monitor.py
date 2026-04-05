"""
Monitor - logs, queue size, errors tracking.
"""
from typing import Dict, List
from datetime import datetime
from collections import deque


class SystemMonitor:
    """
    System monitor - tracks metrics, logs, and errors.
    """
    
    def __init__(self, max_log_entries: int = 1000):
        self._queue_size = 0
        self._processed_count = 0
        self._batch_count = 0
        self._error_count = 0
        self._errors: deque = deque(maxlen=100)
        self._max_log = max_log_entries
    
    def increment_queue_size(self, delta: int = 1):
        """Increment queue size counter."""
        self._queue_size += delta
    
    def decrement_queue_size(self, delta: int = 1):
        """Decrement queue size counter."""
        self._queue_size = max(0, self._queue_size - delta)
    
    def increment_processed(self, delta: int = 1):
        """Increment processed messages counter."""
        self._processed_count += delta
    
    def increment_batches(self, delta: int = 1):
        """Increment batch count."""
        self._batch_count += delta
    
    def increment_errors(self, delta: int = 1):
        """Increment error counter."""
        self._error_count += delta
    
    def log_error(self, message: str):
        """Log an error message."""
        self._errors.append({
            "timestamp": datetime.utcnow().isoformat(),
            "message": message
        })
        self.increment_errors()
    
    def get_stats(self) -> Dict:
        """Get current statistics."""
        return {
            "queue_size": self._queue_size,
            "processed_total": self._processed_count,
            "batches_processed": self._batch_count,
            "error_count": self._error_count,
            "error_rate": self._error_count / max(1, self._processed_count)
        }
    
    def get_recent_errors(self, limit: int = 10) -> List[Dict]:
        """Get recent error entries."""
        return list(self._errors)[-limit:]
    
    def reset(self):
        """Reset all counters."""
        self._queue_size = 0
        self._processed_count = 0
        self._batch_count = 0
        self._error_count = 0
        self._errors.clear()


# Global monitor instance
system_monitor = SystemMonitor()