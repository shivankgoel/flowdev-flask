from typing import List, Optional
from dataclasses import dataclass
import re
from .exceptions import ParserError

@dataclass
class ParsedCode:
    """Container for parsed code and its metadata."""
    code: str
    imports: List[str]
    language: str

class BaseCodeParser:
    """Base class for parsing generated code in different languages."""
    
    def __init__(self):
        self.language = None
        self.import_patterns = []
        self.code_block_patterns = []
        
    def parse(self, response: str, language: str) -> ParsedCode:
        """
        Parse the LLM response to extract code and imports.
        
        Args:
            response: Raw response from the LLM
            language: Programming language of the code
            
        Returns:
            ParsedCode: Parsed code and metadata
            
        Raises:
            ParserError: If parsing fails
        """
        try:
            # Extract code block
            code = self._extract_code_block(response)
            if not code:
                raise ParserError("No code block found in response")
                
            # Extract imports
            imports = self._extract_imports(code)
            
            # Clean up code
            cleaned_code = self._clean_code(code)
            
            # Validate code
            self._validate_code(cleaned_code)
            
            return ParsedCode(
                code=cleaned_code,
                imports=imports,
                language=language
            )
            
        except Exception as e:
            raise ParserError(f"Failed to parse {language} code: {str(e)}")
            
    def _extract_code_block(self, response: str) -> Optional[str]:
        """Extract code block from response using language-specific patterns."""
        for pattern in self.code_block_patterns:
            match = re.search(pattern, response, re.DOTALL)
            if match:
                return match.group(1).strip()
        return None
        
    def _extract_imports(self, code: str) -> List[str]:
        """Extract import statements from code using language-specific patterns."""
        imports = []
        for pattern in self.import_patterns:
            matches = re.finditer(pattern, code)
            imports.extend(match.group(1) for match in matches)
        return list(set(imports))  # Remove duplicates
        
    def _clean_code(self, code: str) -> str:
        """Clean up the extracted code."""
        # Remove any markdown code block markers
        code = re.sub(r'```\w*', '', code)
        # Remove any leading/trailing whitespace
        return code.strip()
        
    def _validate_code(self, code: str) -> None:
        """Validate the extracted code."""
        if not code:
            raise ParserError("Empty code block")
        if len(code.split('\n')) < 1:
            raise ParserError("Code block contains no lines") 