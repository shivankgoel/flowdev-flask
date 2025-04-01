from dataclasses import dataclass
from typing import Optional, List, Dict, Any

@dataclass
class ToolCall:
    """Tool call from the inference service."""
    name: str
    arguments: Dict[str, Any]


@dataclass
class InferenceResponse:
    """Response from the inference service."""
    text_response: Optional[str] = None
    tool_calls: List[ToolCall] = None
    error: Optional[str] = None
