from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseLLMInference(ABC):
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        pass 