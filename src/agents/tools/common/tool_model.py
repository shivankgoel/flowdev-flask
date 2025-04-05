from typing import Dict, Any, List, Optional, Type, Callable, Awaitable
from dataclasses import dataclass
from enum import Enum
import json
from dataclasses_json import dataclass_json, LetterCase

class ToolParameterType(Enum):
    """Types of parameters that tools can accept."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ToolParameter:
    """Definition of a tool parameter."""
    name: str
    type: ToolParameterType
    description: str
    required: bool = True
    default: Any = None

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ToolResponse:
    """Standard response format for tool execution."""
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    
    @classmethod
    def success_response(cls, message: str, data: Optional[Dict[str, Any]] = None) -> 'ToolResponse':
        """Create a success response."""
        return cls(success=True, message=message, data=data)
    
    @classmethod
    def error_response(cls, error: str) -> 'ToolResponse':
        """Create an error response."""
        return cls(success=False, error=error)
    
    def to_json(self) -> str:
        """Convert the response to a JSON string for LLM consumption."""
        return self.to_json()  # Uses dataclass_json's to_json
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the response to a dictionary for LLM consumption."""
        return self.to_dict()  # Uses dataclass_json's to_dict
    
    def to_natural_language(self) -> str:
        """Convert the response to natural language for LLM consumption."""
        if self.success:
            result = f"✅ {self.message}"
            if self.data:
                # Format data in a readable way
                data_str = json.dumps(self.data, indent=2)
                result += f"\n\nData:\n{data_str}"
            return result
        else:
            return f"❌ Error while invoking tool: {self.error}"

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ToolDefinition:
    """Definition of a tool that can be used by LLMs."""
    name: str
    description: str
    parameters: List[ToolParameter]
    handler: Callable[[Dict[str, Any]], Awaitable[ToolResponse]]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the tool definition to a dictionary format for LLMs."""
        return self.to_dict()  # Uses dataclass_json's to_dict
    
    def validate_args(self, args: Dict[str, Any]) -> Optional[str]:
        """Validate the arguments provided to the tool.
        
        Returns:
            None if validation passes, error message if validation fails
        """
        # Check required parameters
        for param in self.parameters:
            if param.required and param.name not in args:
                return f"Missing required parameter: {param.name}"
            
            # Type validation could be added here if needed
            
        return None 