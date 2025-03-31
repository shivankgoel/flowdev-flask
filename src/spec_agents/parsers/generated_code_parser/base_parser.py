from abc import ABC, abstractmethod
from typing import Dict, Any, List
import json
from dataclasses import dataclass

@dataclass
class GeneratedCode:
    """Represents the parsed generated code with metadata."""
    language: str
    language_version: str
    filename: str
    filepath: str
    imports: List[str]
    code: str
    metadata: Dict[str, Any]

class BaseCodeParser(ABC):
    """Base class for language-specific code parsers."""
    
    def __init__(self):
        self.required_fields = [
            "language",
            "language_version",
            "filename",
            "filepath",
            "generated_code"
        ]

    def parse(self, response: str) -> GeneratedCode:
        """
        Parse the LLM response into a structured format.
        
        Args:
            response: The LLM response string
            
        Returns:
            GeneratedCode: Parsed code with metadata
            
        Raises:
            ValueError: If response is invalid or missing required fields
        """
        try:
            # Parse JSON response
            data = json.loads(response)
            
            # Validate required fields
            self._validate_required_fields(data)
            
            # Extract imports and code
            imports, code = self._extract_code_parts(data["generated_code"])
            
            # Create GeneratedCode instance
            return GeneratedCode(
                language=data["language"],
                language_version=data["language_version"],
                filename=data["filename"],
                filepath=data["filepath"],
                imports=imports,
                code=code,
                metadata=self._extract_metadata(data)
            )
            
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON response from LLM")
        except Exception as e:
            raise ValueError(f"Error parsing LLM response: {str(e)}")

    def _validate_required_fields(self, data: Dict[str, Any]) -> None:
        """Validate that all required fields are present."""
        missing_fields = [
            field for field in self.required_fields 
            if field not in data
        ]
        if missing_fields:
            raise ValueError(
                f"Missing required fields in LLM response: {', '.join(missing_fields)}"
            )

    @abstractmethod
    def _extract_code_parts(self, code: str) -> tuple[List[str], str]:
        """
        Extract imports and main code from the generated code.
        
        Args:
            code: The complete generated code string
            
        Returns:
            tuple[List[str], str]: List of imports and main code
        """
        pass

    def _extract_metadata(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract additional metadata from the response.
        
        Args:
            data: The parsed JSON response
            
        Returns:
            Dict[str, Any]: Additional metadata
        """
        return {
            k: v for k, v in data.items() 
            if k not in self.required_fields
        } 