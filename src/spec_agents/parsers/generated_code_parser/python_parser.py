from typing import List, Tuple
import re
from .base_parser import BaseCodeParser, GeneratedCode
from .config.language_config import PYTHON_CONFIG
from .utils.import_extractor import ImportExtractor
from .exceptions import ImportError, ClassStructureError, IndentationError, ParseError

class PythonImportExtractor(ImportExtractor):
    """Python-specific import extraction."""
    
    def __init__(self):
        super().__init__(PYTHON_CONFIG.import_patterns)
    
    def _process_match_groups(self, groups: Tuple) -> str:
        if groups[0]:  # import statement
            return groups[0].strip()
        elif groups[1] and groups[2]:  # from ... import statement
            return f"from {groups[1].strip()} import {groups[2].strip()}"
        return ""

class PythonCodeParser(BaseCodeParser):
    """Parser for Python code."""
    
    def __init__(self):
        super().__init__()
        self.language = "python"
        
    def parse(self, response: str, language: str = "python") -> GeneratedCode:
        """
        Parse Python code from the response.
        
        Args:
            response: Raw response from the LLM
            language: Programming language (defaults to "python")
            
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
            
            # Clean up code
            cleaned_code = self._clean_code(code)
            
            # Validate code
            self._validate_code(cleaned_code)
            
            # Validate Python-specific structure
            self._validate_python_structure(cleaned_code)
            
            return GeneratedCode(
                code=cleaned_code,
                imports=imports,
                language=language
            )
            
        except Exception as e:
            raise ParseError(f"Failed to parse Python code: {str(e)}")
            
    def get_language_version(self) -> str:
        """Get the Python version."""
        return "3.8"  # Default to Python 3.8
        
    def get_filename(self, code: str) -> str:
        """Get the Python filename from the code."""
        # Look for class name in the code
        class_match = re.compile(PYTHON_CONFIG.class_pattern, re.MULTILINE).search(code)
        if class_match:
            return f"{class_match.group(1).lower()}.py"
        return "main.py"  # Default filename
        
    def get_filepath(self, code: str) -> str:
        """Get the filepath for the Python file."""
        return f"src/models/{self.get_filename(code)}"
        
    def _validate_python_structure(self, code: str) -> None:
        """
        Validate Python-specific code structure.
        
        Args:
            code: Code string to validate
            
        Raises:
            ClassStructureError: If class structure is invalid
            IndentationError: If indentation is invalid
        """
        # Check for class declaration
        class_match = re.compile(PYTHON_CONFIG.class_pattern, re.MULTILINE).search(code)
        if not class_match:
            raise ClassStructureError("No class declaration found")
        
        # Check for proper indentation
        if PYTHON_CONFIG.indentation_validation:
            lines = code.split('\n')
            for i, line in enumerate(lines):
                if line.strip() and not line.startswith(' '):
                    raise IndentationError(f"Invalid indentation at line {i+1}")
                    
    def _validate_code(self, code: str) -> None:
        """
        Validate the code string.
        
        Args:
            code: Code string to validate
            
        Raises:
            ParseError: If code is invalid
        """
        super()._validate_code(code)
        
        # Additional Python-specific validation
        if not re.compile(PYTHON_CONFIG.class_pattern, re.MULTILINE).search(code):
            raise ParseError("Code must contain a class definition") 