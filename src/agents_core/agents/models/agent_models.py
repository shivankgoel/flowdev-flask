from enum import Enum
from dataclasses import dataclass
from typing import Optional

class AgentStep(Enum):
    """Steps in the code generation process."""
    FORMAT_PROMPT = "format_prompt"
    GENERATE = "generate"
    PARSE = "parse"
    ERROR = "error"


@dataclass
class CodingAgentResponse:
    """Response from the agent."""
    code: str
    error: Optional[str] = None
