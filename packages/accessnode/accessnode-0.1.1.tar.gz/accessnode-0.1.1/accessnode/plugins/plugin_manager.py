"""Plugin management system."""

from typing import Any, Dict, List
from .base_plugin import Plugin

class PluginManager:
    """Manages AccessNode plugins."""
    
    def __init__(self):
        self.plugins: List[Plugin] = []
        
    def register(self, plugin: Plugin) -> None:
        """Register a new plugin."""
        self.plugins.append(plugin)
        
    async def run_pre_query(self, query: str, params: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
        """Run pre-query hooks for all plugins."""
        for plugin in self.plugins:
            query, params = await plugin.pre_query(query, params)
        return query, params
        
    async def run_post_query(self, result: Any) -> Any:
        """Run post-query hooks for all plugins."""
        for plugin in self.plugins:
            result = await plugin.post_query(result)
        return result