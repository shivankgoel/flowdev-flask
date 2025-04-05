from dataclasses import dataclass

@dataclass
class ParsedResponse:
    """Container for parsed code."""
    code: str
    code_language: str
    response: str
    thoughts: str
    error: str