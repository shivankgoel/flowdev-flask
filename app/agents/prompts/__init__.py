from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class BasePromptTemplate(ABC):
    @abstractmethod
    def create_prompt(self, layer_spec: Dict[str, Any], parent_code: Optional[str] = None, feedback: Optional[Dict] = None, layer_dependencies: Optional[Dict] = None) -> str:
        pass 