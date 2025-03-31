from typing import List, Tuple
import re
from .base_parser import BaseCodeParser, ParsedCode
from .exceptions import ParserError, ClassStructureError

class JavaCodeParser(BaseCodeParser):
    """Parser for Java code."""
    
    def __init__(self):
        super().__init__()
        self.language = "java"
        
        # Java-specific patterns
        self.import_patterns = [
            r'^import\s+([a-zA-Z0-9_.*]+);',
            r'^import\s+static\s+([a-zA-Z0-9_.*]+);'
        ]
        
        self.code_block_patterns = [
            r'```java\n(.*?)```',
            r'```\n(.*?)```'
        ]
        
    def parse(self, response: str, language: str = "java") -> ParsedCode:
        """
        Parse Java code from the LLM response.
        
        Args:
            response: Raw response from the LLM
            language: Programming language (defaults to "java")
            
        Returns:
            ParsedCode: Parsed Java code and metadata
            
        Raises:
            ParserError: If parsing fails
        """
        try:
            # Extract code block
            code = self._extract_code_block(response)
            if not code:
                raise ParserError("No Java code block found in response")
                
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
            raise ParserError(f"Failed to parse Java code: {str(e)}")
            
    def _extract_imports(self, code: str) -> List[str]:
        """Extract Java import statements."""
        imports = []
        
        # Handle regular imports
        import_matches = re.finditer(r'^import\s+([a-zA-Z0-9_.*]+);', code, re.MULTILINE)
        for match in import_matches:
            imports.append(match.group(1))
            
        # Handle static imports
        static_matches = re.finditer(r'^import\s+static\s+([a-zA-Z0-9_.*]+);', code, re.MULTILINE)
        for match in static_matches:
            imports.append(f"static {match.group(1)}")
            
        return list(set(imports))  # Remove duplicates

    def get_language(self) -> str:
        """Get the programming language name."""
        return "java"

    def get_language_version(self) -> str:
        """Get the programming language version."""
        return "11+"

    def get_filename(self, code: str) -> str:
        """Get the filename based on the code content."""
        # Extract class name from code
        class_match = re.search(r'class\s+(\w+)', code)
        if class_match:
            class_name = class_match.group(1)
            return f"{class_name}.java"
        return "Generated.java"

    def get_filepath(self, code: str) -> str:
        """Get the filepath based on the code content."""
        # Extract package name if present
        package_match = re.search(r'^package\s+([^;]+);', code, re.MULTILINE)
        if package_match:
            package_path = package_match.group(1).replace('.', '/')
            filename = self.get_filename(code)
            return f"src/{package_path}/{filename}"
        return f"src/models/{self.get_filename(code)}"

    def _extract_code_parts(self, code: str) -> Tuple[List[str], str]:
        """
        Extract imports and main code from Java code.
        
        Args:
            code: The complete Java code string
            
        Returns:
            Tuple[List[str], str]: List of imports and main code
            
        Raises:
            ImportError: If imports are invalid
            ClassStructureError: If class structure is invalid
            IndentationError: If indentation is invalid
        """
        # Extract imports
        imports = self._extract_imports(code)
        
        # Validate imports
        self._validate_imports(imports)
        
        # Extract main code (everything after imports)
        main_code = self._extract_main_code(code)
        
        # Validate class structure
        self._validate_class_structure(main_code)
        
        return imports, main_code

    def _validate_imports(self, imports: List[str]) -> None:
        """
        Validate Java imports.
        
        Args:
            imports: List of import statements
            
        Raises:
            ImportError: If imports are invalid
        """
        for imp in imports:
            if imp.startswith('package'):
                continue  # Skip package declaration validation
            if not re.match(r'^[a-zA-Z0-9_.*]+$', imp.split()[1]):  # Skip 'import' keyword
                raise ImportError(f"Invalid import statement: {imp}")

    def _extract_main_code(self, code: str) -> str:
        """
        Extract main code after imports.
        
        Args:
            code: Complete code string
            
        Returns:
            str: Main code without imports
        """
        # Find the last import or package statement
        last_import = 0
        for pattern in self.import_patterns:
            for match in re.finditer(pattern, code, re.MULTILINE):
                last_import = max(last_import, match.end())
        
        # Return everything after the last import/package
        return code[last_import:].strip()

    def _validate_class_structure(self, code: str) -> None:
        """
        Validate Java class structure.
        
        Args:
            code: Main code string
            
        Raises:
            ClassStructureError: If class structure is invalid
        """
        # Check for class declaration
        class_match = re.search(r'class\s+(\w+)', code)
        if not class_match:
            raise ClassStructureError("No public class declaration found") 