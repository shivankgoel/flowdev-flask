from typing import List, Tuple
import re
from .base_parser import BaseCodeParser, ParsedCode
from .config.language_config import PYTHON_CONFIG
from .utils.import_extractor import ImportExtractor
from .exceptions import ImportError, ClassStructureError, IndentationError, ParserError

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
        
        # Python-specific patterns
        self.import_patterns = [
            r'^import\s+(\w+(?:\s*,\s*\w+)*)',
            r'^from\s+(\w+(?:\.\w+)*)\s+import\s+(\w+(?:\s*,\s*\w+)*)'
        ]
        
        self.code_block_patterns = [
            r'```python\n(.*?)```',
            r'```\n(.*?)```'
        ]
        
    def parse(self, response: str, language: str = "python") -> ParsedCode:
        """
        Parse Python code from the LLM response.
        
        Args:
            response: Raw response from the LLM
            language: Programming language (defaults to "python")
            
        Returns:
            ParsedCode: Parsed Python code and metadata
            
        Raises:
            ParserError: If parsing fails
        """
        try:
            # Extract code block
            code = self._extract_code_block(response)
            if not code:
                raise ParserError("No Python code block found in response")
                
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
            raise ParserError(f"Failed to parse Python code: {str(e)}")
            
    def _extract_imports(self, code: str) -> List[str]:
        """Extract Python import statements."""
        imports = []
        
        # Handle 'import' statements
        import_matches = re.finditer(r'^import\s+(\w+(?:\s*,\s*\w+)*)', code, re.MULTILINE)
        for match in import_matches:
            imports.extend(imp.strip() for imp in match.group(1).split(','))
            
        # Handle 'from ... import' statements
        from_matches = re.finditer(r'^from\s+(\w+(?:\.\w+)*)\s+import\s+(\w+(?:\s*,\s*\w+)*)', code, re.MULTILINE)
        for match in from_matches:
            module = match.group(1)
            names = match.group(2).split(',')
            imports.extend(f"{module}.{name.strip()}" for name in names)
            
        return list(set(imports))  # Remove duplicates

    def get_language(self) -> str:
        """Get the programming language name."""
        return "python"

    def get_language_version(self) -> str:
        """Get the programming language version."""
        return "3.8+"

    def get_filename(self, code: str) -> str:
        """Get the filename based on the code content."""
        # Extract class name from code
        class_match = re.compile(PYTHON_CONFIG.class_pattern, re.MULTILINE).search(code)
        if class_match:
            class_name = class_match.group(1)
            return f"{class_name.lower()}.py"
        return "generated.py"

    def get_filepath(self, code: str) -> str:
        """Get the filepath based on the code content."""
        filename = self.get_filename(code)
        return f"src/models/{filename}"

    def _extract_code_parts(self, code: str) -> Tuple[List[str], str]:
        """
        Extract imports and main code from Python code.
        
        Args:
            code: The complete Python code string
            
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
        Validate Python imports.
        
        Args:
            imports: List of import statements
            
        Raises:
            ImportError: If imports are invalid
        """
        for imp in imports:
            if not re.compile(PYTHON_CONFIG.import_validation_pattern).match(imp.split()[0]):
                raise ImportError(f"Invalid import statement: {imp}")

    def _extract_main_code(self, code: str) -> str:
        """
        Extract main code after imports.
        
        Args:
            code: Complete code string
            
        Returns:
            str: Main code without imports
        """
        # Find the last import statement
        last_import = 0
        for match in re.finditer(r'^import\s+(\w+(?:\s*,\s*\w+)*)', code, re.MULTILINE):
            last_import = match.end()
        
        # Return everything after the last import
        return code[last_import:].strip()

    def _validate_class_structure(self, code: str) -> None:
        """
        Validate Python class structure.
        
        Args:
            code: Main code string
            
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