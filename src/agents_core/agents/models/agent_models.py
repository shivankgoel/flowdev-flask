from enum import Enum

class AgentStep(Enum):
    """Steps in the code generation process."""
    FORMAT_PROMPT = "format_prompt"
    GENERATE = "generate"
    PARSE = "parse"
    ERROR = "error"