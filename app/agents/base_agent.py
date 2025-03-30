from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import os
from .inference.openai_inference import OpenAIInference

class BaseAgent(ABC):
    """Base class for all agents in the system"""
    
    def __init__(self, max_retries: int = 3):
        """
        Initialize the agent.
        
        Args:
            max_retries: Maximum number of retries for feedback loops
        """
        self.max_retries = max_retries
        self.inference = OpenAIInference()
        
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the input data and return results.
        
        Args:
            input_data: Input data dictionary
            
        Returns:
            Dict containing the results
        """
        pass
    
    def _get_env_var(self, key: str, default: Any = None) -> Any:
        """Get environment variable with optional default value"""
        return os.getenv(key, default)
    
    def _update_max_retries_from_env(self, env_key: str):
        """Update max_retries from environment variable if set"""
        retries = self._get_env_var(env_key)
        if retries is not None:
            self.max_retries = int(retries) 