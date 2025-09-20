from typing import Any, Dict, List, Optional, Set, Callable
from enum import Enum
import json
from datetime import datetime
from ..core.exceptions import ChangeTrackingError
from .subscription import Subscription;
import uuid

class ChangeType(Enum):
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"

class Change:
    def __init__(
        self,
        type: ChangeType,
        table: str,
        data: Dict[str, Any],
        old_data: Optional[Dict[str, Any]] = None
    ):
        self.id = str(uuid.uuid4())
        self.type = type
        self.table = table
        self.data = data
        self.old_data = old_data
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert change to dictionary."""
        return {
            'id': self.id,
            'type': self.type.value,
            'table': self.table,
            'data': self.data,
            'old_data': self.old_data,
            'timestamp': self.timestamp.isoformat()
        }

class ChangeTracker:
    def __init__(self, subscription_manager):
        self.subscription_manager = subscription_manager
        self._tracked_tables: Set[str] = set()

    async def track_table(self, table: str) -> None:
        """Start tracking changes for a table."""
        self._tracked_tables.add(table)

    async def untrack_table(self, table: str) -> None:
        """Stop tracking changes for a table."""
        self._tracked_tables.discard(table)

    async def record_change(
        self,
        type: ChangeType,
        table: str,
        data: Dict[str, Any],
        old_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record a change and notify subscribers."""
        if table not in self._tracked_tables:
            return

        change = Change(type, table, data, old_data)
        
        # Publish to table-specific channel
        await self.subscription_manager.publish(
            f"table:{table}",
            change.to_dict()
        )

        # Publish to model-specific channels
        if type == ChangeType.UPDATE:
            for field, new_value in data.items():
                if old_data and old_data.get(field) != new_value:
                    await self.subscription_manager.publish(
                        f"table:{table}:field:{field}",
                        change.to_dict()
                    )

    async def watch_table(
        self,
        table: str,
        callback: Callable,
        filters: Optional[Dict[str, Any]] = None
    ) -> Subscription:
        """Watch for changes on a table."""
        if table not in self._tracked_tables:
            await self.track_table(table)

        return await self.subscription_manager.subscribe(
            f"table:{table}",
            callback,
            filters
        )

    async def watch_field(
        self,
        table: str,
        field: str,
        callback: Callable,
        filters: Optional[Dict[str, Any]] = None
    ) -> Subscription:
        """Watch for changes on a specific field."""
        if table not in self._tracked_tables:
            await self.track_table(table)

        return await self.subscription_manager.subscribe(
            f"table:{table}:field:{field}",
            callback,
            filters
        )


























# """Change Data Capture management."""

# from typing import Any, Callable, Dict, List, Set, Optional
# import asyncio
# import json

# class CDCManager:
#     """Manages Change Data Capture and real-time updates."""
    
#     def __init__(self):
#         self.subscribers: Set[Callable] = set()
#         self._queue: asyncio.Queue = asyncio.Queue()
#         self._task: Optional[asyncio.Task] = None
        
#     async def start(self):
#         """Start the CDC manager."""
#         self._task = asyncio.create_task(self._process_queue())
        
#     async def notify_change(self, query: str, result: Any):
#         """Notify subscribers of database changes."""
#         await self._queue.put({
#             'query': query,
#             'result': result,
#             'timestamp': asyncio.get_event_loop().time()
#         })
        
#     async def subscribe(self, callback: Callable):
#         """Subscribe to database changes."""
#         self.subscribers.add(callback)
#         return lambda: self.subscribers.remove(callback)
        
#     async def _process_queue(self):
#         """Process the change notification queue."""
#         while True:
#             try:
#                 change = await self._queue.get()
#                 for subscriber in self.subscribers:
#                     try:
#                         await subscriber(change)
#                     except Exception as e:
#                         print(f"Error in subscriber callback: {e}")
#             except asyncio.CancelledError:
#                 break
                
#     async def close(self):
#         """Cleanup CDC manager resources."""
#         if self._task:
#             self._task.cancel()
#             await self._task