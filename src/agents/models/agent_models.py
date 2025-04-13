from enum import Enum
from dataclasses import dataclass
from src.agents.models.parser_models import CodeParserResponse


class InvokeAgentQuerySource(Enum):
    USER = "user"

@dataclass
class InvokeAgentRequest:
    query: str
    query_source: InvokeAgentQuerySource

class AgentStep(Enum):
    """Steps in the code generation process."""
    FORMAT_PROMPT = "format_prompt"
    GENERATE = "generate"
    PARSE = "parse"
    ERROR = "error"

@dataclass
class AgentResponse:
    agent_node_id: str
    code_parser_response: CodeParserResponse
    
