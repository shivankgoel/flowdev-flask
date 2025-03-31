from typing import List, Tuple
import re
from .base_parser import BaseCodeParser, GeneratedCode
from .exceptions import ImportError, ClassStructureError, ParseError

class JavaCodeParser(BaseCodeParser):
    """Parser for Java code."""
    
    def __init__(self):
        super().__init__()
        self.language = "java"
        
    def parse(self, response: str, language: str = "java") -> GeneratedCode:
        """
        Parse Java code from the response.
        
        Args:
            response: Raw response from the LLM
            language: Programming language (defaults to "java")
            
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
            
            # Validate Java-specific structure
            self._validate_java_structure(cleaned_code)
            
            return GeneratedCode(
                code=cleaned_code,
                imports=imports,
                language=language
            )
            
        except Exception as e:
            raise ParseError(f"Failed to parse Java code: {str(e)}")
            
    def get_language_version(self) -> str:
        """Get the Java version."""
        return "11"  # Default to Java 11
        
    def get_filename(self, code: str) -> str:
        """Get the Java filename from the code."""
        # Look for class name in the code
        class_match = re.search(r'class\s+(\w+)', code)
        if class_match:
            return f"{class_match.group(1)}.java"
        return "Main.java"  # Default filename
        
    def get_filepath(self, code: str) -> str:
        """Get the filepath for the Java file."""
        # Look for package declaration
        package_match = re.search(r'package\s+([a-zA-Z0-9_.]+);', code)
        if package_match:
            package_path = package_match.group(1).replace('.', '/')
            return f"src/main/java/{package_path}/{self.get_filename(code)}"
        return f"src/main/java/{self.get_filename(code)}"
        
    def _validate_java_structure(self, code: str) -> None:
        """
        Validate Java-specific code structure.
        
        Args:
            code: Code string to validate
            
        Raises:
            ClassStructureError: If class structure is invalid
        """
        # Check for class declaration
        class_match = re.search(r'class\s+(\w+)', code)
        if not class_match:
            raise ClassStructureError("No class declaration found")
            
        # Check for proper braces
        brace_count = 0
        for char in code:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count < 0:
                    raise ClassStructureError("Mismatched braces")
        if brace_count != 0:
            raise ClassStructureError("Mismatched braces")
            
    def _validate_code(self, code: str) -> None:
        """
        Validate the code string.
        
        Args:
            code: Code string to validate
            
        Raises:
            ParseError: If code is invalid
        """
        super()._validate_code(code)
        
        # Additional Java-specific validation
        if not re.search(r'class\s+(\w+)', code):
            raise ParseError("Code must contain a class definition") 