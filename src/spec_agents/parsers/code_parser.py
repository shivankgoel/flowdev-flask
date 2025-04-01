from typing import List
from dataclasses import dataclass
import re

class ParseError(Exception):
    """Raised when parsing fails."""
    pass

@dataclass
class GeneratedCode:
    """Container for parsed code and metadata."""
    code: str
    imports: List[str]
    language: str

class CodeParser:
    """Parser for code generation responses."""
    
    def __init__(self):
        self.language = "auto"
        
    def parse(self, response: str, language: str = "auto") -> GeneratedCode:
        """
        Parse code from the response.
        
        Args:
            response: Raw response from the LLM
            language: Programming language (defaults to "auto")
            
        Returns:
            GeneratedCode: Parsed code and metadata
            
        Raises:
            ParseError: If parsing fails
        """
        try:
            # Extract code from XML tags
            code = self._extract_code(response)
            
            # Clean up code
            cleaned_code = self._clean_code(code)
            
            return GeneratedCode(
                code=cleaned_code,
                imports=[],  # No imports in new format
                language=language
            )
            
        except Exception as e:
            raise ParseError(f"Failed to parse code: {str(e)}")
            
    def _extract_code(self, response: str) -> str:
        """
        Extract code from XML tags.
        
        Args:
            response: Raw response string
            
        Returns:
            str: Extracted code
            
        Raises:
            ParseError: If code extraction fails
        """
        match = re.search(r'<generated_code>(.*?)</generated_code>', response, re.DOTALL)
        if not match:
            raise ParseError("No code found in XML tags")
        return match.group(1).strip()
            
    def _clean_code(self, code: str) -> str:
        """
        Clean up the code string.
        
        Args:
            code: Raw code string
            
        Returns:
            str: Cleaned code string
        """
        return code.strip() 