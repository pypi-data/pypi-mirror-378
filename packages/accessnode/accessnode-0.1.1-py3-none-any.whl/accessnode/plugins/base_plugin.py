# base plugin to extend AccessNode

"""Base plugin implementation."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple

class Plugin(ABC):
    """Base class for AccessNode plugins."""
    
    @abstractmethod
    async def initialize(self, context: Dict[str, Any]) -> None:
        """Initialize the plugin with context."""
        pass
    
    @abstractmethod
    async def pre_query(self, query: str, params: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Pre-process query and parameters."""
        return query, params
    
    @abstractmethod
    async def post_query(self, result: Any) -> Any:
        """Post-process query results."""
        return result
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup plugin resources."""
        pass