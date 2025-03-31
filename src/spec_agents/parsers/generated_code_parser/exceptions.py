class CodeParserError(Exception):
    """Base exception for code parser errors."""
    pass

class ValidationError(CodeParserError):
    """Raised when code validation fails."""
    pass

class ImportError(ValidationError):
    """Raised when import validation fails."""
    pass

class ClassStructureError(ValidationError):
    """Raised when class structure validation fails."""
    pass

class IndentationError(ValidationError):
    """Raised when indentation validation fails."""
    pass

class ParseError(CodeParserError):
    """Raised when parsing fails."""
    pass 