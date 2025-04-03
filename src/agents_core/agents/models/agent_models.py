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
class AgentThoughts:
    """Model for agent's thoughts and reasoning."""
    thoughts: str

@dataclass
class AgentResponse:
    """Model for agent's response including code, thoughts, and response text."""
    agent_node_id: str  # Canvas id if canvas else node id
    code: str
    thoughts: Optional[AgentThoughts] = None
    response: Optional[str] = None
    error: Optional[str] = None
