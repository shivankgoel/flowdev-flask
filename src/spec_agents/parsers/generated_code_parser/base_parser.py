from typing import List, Dict, Any
import json
from dataclasses import dataclass
from .exceptions import ParseError

@dataclass
class GeneratedCode:
    """Container for parsed code and metadata."""
    code: str
    imports: List[str]
    language: str

class BaseCodeParser:
    """Base class for code parsers."""
    
    def __init__(self):
        self.language = "base"
        
    def parse(self, response: str, language: str = None) -> GeneratedCode:
        """
        Parse code from the response.
        
        Args:
            response: Raw response from the LLM
            language: Programming language (defaults to self.language)
            
        Returns:
            GeneratedCode: Parsed code and metadata
            
        Raises:
            ParseError: If parsing fails
        """
        try:
            # Parse JSON response
            parsed_json = self._parse_json(response)
            
            # Extract code and imports
            code = parsed_json.get('generated_code', '')
            imports = parsed_json.get('imports', [])
            
            # Parse the code if it's a JSON string
            if code.startswith('"') and code.endswith('"'):
                try:
                    code = json.loads(code)
                except json.JSONDecodeError:
                    # If it's not valid JSON, just use the string as is
                    pass
            
            # Clean up code
            cleaned_code = self._clean_code(code)
            
            # Validate code
            self._validate_code(cleaned_code)
            
            return GeneratedCode(
                code=cleaned_code,
                imports=imports,
                language=language or self.language
            )
            
        except Exception as e:
            raise ParseError(f"Failed to parse code: {str(e)}")
            
    def _parse_json(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON response from LLM.
        
        Args:
            response: Raw response string
            
        Returns:
            Dict[str, Any]: Parsed JSON data
            
        Raises:
            ParseError: If JSON parsing fails
        """
        try:
            # Remove any markdown formatting if present
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.endswith('```'):
                response = response[:-3]
                
            # Parse JSON
            return json.loads(response)
        except json.JSONDecodeError as e:
            raise ParseError(f"Invalid JSON response: {str(e)}")
            
    def _clean_code(self, code: str) -> str:
        """
        Clean up the code string.
        
        Args:
            code: Raw code string
            
        Returns:
            str: Cleaned code string
        """
        # Remove any markdown formatting if present
        code = code.strip()
        if code.startswith('```'):
            code = code[3:]
        if code.endswith('```'):
            code = code[:-3]
            
        # Remove language identifier if present
        if code.startswith('python') or code.startswith('java'):
            code = code.split('\n', 1)[1]
            
        return code.strip()
        
    def _validate_code(self, code: str) -> None:
        """
        Validate the code string.
        
        Args:
            code: Code string to validate
            
        Raises:
            ParseError: If code is invalid
        """
        if not code:
            raise ParseError("Empty code string")
            
    def get_language(self) -> str:
        """Get the programming language."""
        return self.language
        
    def get_language_version(self) -> str:
        """Get the programming language version."""
        return "1.0"  # Default version 