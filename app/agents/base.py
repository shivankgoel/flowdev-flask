from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseAgent(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.context: Dict[str, Any] = {}
        self.memory: list = []

    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the input data and return results"""
        pass

    def add_to_memory(self, data: Dict[str, Any]):
        """Add data to agent's memory"""
        self.memory.append(data)

    def get_memory(self) -> list:
        """Retrieve agent's memory"""
        return self.memory

    def update_context(self, new_context: Dict[str, Any]):
        """Update agent's context"""
        self.context.update(new_context)

    def get_context(self) -> Dict[str, Any]:
        """Get agent's current context"""
        return self.context 