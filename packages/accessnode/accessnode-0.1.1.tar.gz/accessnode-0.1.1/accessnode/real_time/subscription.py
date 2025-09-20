from typing import Any, Callable, Dict, List, Optional, Set
import asyncio
import json
from datetime import datetime
from ..core.exceptions import SubscriptionError
import uuid
class Subscription:
    def __init__(
        self,
        channel: str,
        callback: Callable,
        filters: Optional[Dict[str, Any]] = None
    ):
        self.id = str(uuid.uuid4())
        self.channel = channel
        self.callback = callback
        self.filters = filters
        self.created_at = datetime.utcnow()
        self.last_event_at: Optional[datetime] = None

    async def handle_event(self, event: Dict[str, Any]) -> None:
        """Handle incoming event."""
        if self._matches_filters(event):
            self.last_event_at = datetime.utcnow()
            await self.callback(event)

    def _matches_filters(self, event: Dict[str, Any]) -> bool:
        """Check if event matches subscription filters."""
        if not self.filters:
            return True

        return all(
            event.get(key) == value
            for key, value in self.filters.items()
        )

class SubscriptionManager:
    def __init__(self):
        self._subscriptions: Dict[str, Set[Subscription]] = {}
        self._lock = asyncio.Lock()

    async def subscribe(
        self,
        channel: str,
        callback: Callable,
        filters: Optional[Dict[str, Any]] = None
    ) -> Subscription:
        """Subscribe to a channel."""
        subscription = Subscription(channel, callback, filters)
        
        async with self._lock:
            if channel not in self._subscriptions:
                self._subscriptions[channel] = set()
            self._subscriptions[channel].add(subscription)

        return subscription

    async def unsubscribe(self, subscription: Subscription) -> None:
        """Unsubscribe from a channel."""
        async with self._lock:
            if subscription.channel in self._subscriptions:
                self._subscriptions[subscription.channel].discard(subscription)
                if not self._subscriptions[subscription.channel]:
                    del self._subscriptions[subscription.channel]

    async def publish(
        self,
        channel: str,
        event: Dict[str, Any]
    ) -> int:
        """Publish event to channel."""
        if channel not in self._subscriptions:
            return 0

        subscribers = self._subscriptions[channel].copy()
        tasks = [
            subscriber.handle_event(event)
            for subscriber in subscribers
        ]
        
        if tasks:
            await asyncio.gather(*tasks)
        
        return len(tasks)

    def get_channel_subscribers(self, channel: str) -> List[Subscription]:
        """Get all subscribers for a channel."""
        return list(self._subscriptions.get(channel, set()))