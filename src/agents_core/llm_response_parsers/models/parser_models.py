from dataclasses import dataclass

@dataclass
class ParsedCode:
    """Container for parsed code."""
    code: str
    language: str