from typing import List, Tuple, Optional
import re
from .base_parser import BaseCodeParser, ParsedCode
from .exceptions import ParserError, ClassStructureError, ImportError

class TypeScriptCodeParser(BaseCodeParser):
    """Parser for TypeScript code."""
    
    def __init__(self):
        super().__init__()
        self.language = "typescript"
        
        # TypeScript-specific patterns
        self.import_patterns = [
            r'^import\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'^import\s*{([^}]+)}\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'^import\s+type\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]'
        ]
        
        self.code_block_patterns = [
            r'```typescript\n(.*?)```',
            r'```\n(.*?)```'
        ]
        
    def parse(self, response: str, language: str = "typescript") -> ParsedCode:
        """
        Parse TypeScript code from the LLM response.
        
        Args:
            response: Raw response from the LLM
            language: Programming language (defaults to "typescript")
            
        Returns:
            ParsedCode: Parsed TypeScript code and metadata
            
        Raises:
            ParserError: If parsing fails
        """
        try:
            # Extract code block
            code = self._extract_code_block(response)
            if not code:
                raise ParserError("No TypeScript code block found in response")
                
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
            raise ParserError(f"Failed to parse TypeScript code: {str(e)}")
            
    def _extract_imports(self, code: str) -> List[str]:
        """Extract TypeScript import statements."""
        imports = []
        
        # Handle default imports
        default_matches = re.finditer(r'^import\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]', code, re.MULTILINE)
        for match in default_matches:
            imports.append(f"{match.group(1)} from '{match.group(2)}'")
            
        # Handle named imports
        named_matches = re.finditer(r'^import\s*{([^}]+)}\s+from\s+[\'"]([^\'"]+)[\'"]', code, re.MULTILINE)
        for match in named_matches:
            names = [n.strip() for n in match.group(1).split(',')]
            module = match.group(2)
            imports.extend(f"{name} from '{module}'" for name in names)
            
        # Handle type imports
        type_matches = re.finditer(r'^import\s+type\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]', code, re.MULTILINE)
        for match in type_matches:
            imports.append(f"type {match.group(1)} from '{match.group(2)}'")
            
        return list(set(imports))  # Remove duplicates

    def get_language(self) -> str:
        """Get the programming language name."""
        return "typescript"

    def get_language_version(self) -> str:
        """Get the programming language version."""
        return "4.0+"

    def get_filename(self, code: str) -> str:
        """Get the filename based on the code content."""
        # Extract class name from code
        class_match = re.search(r'class\s+(\w+)', code)
        if class_match:
            class_name = class_match.group(1)
            return f"{class_name}.ts"
        return "generated.ts"

    def get_filepath(self, code: str) -> str:
        """Get the filepath based on the code content."""
        filename = self.get_filename(code)
        return f"src/models/{filename}"

    def _extract_code_parts(self, code: str) -> Tuple[List[str], str]:
        """
        Extract imports and main code from TypeScript code.
        
        Args:
            code: The complete TypeScript code string
            
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
        Validate TypeScript imports.
        
        Args:
            imports: List of import statements
            
        Raises:
            ImportError: If imports are invalid
        """
        for imp in imports:
            if not re.match(r'^import\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]', imp):
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
        for match in re.finditer(r'^import\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]', code, re.MULTILINE):
            last_import = match.end()
        
        # Return everything after the last import
        return code[last_import:].strip()

    def _validate_class_structure(self, code: str) -> None:
        """
        Validate TypeScript class structure.
        
        Args:
            code: Main code string
            
        Raises:
            ClassStructureError: If class structure is invalid
        """
        # Check for class declaration
        class_match = re.search(r'class\s+(\w+)', code)
        if not class_match:
            raise ClassStructureError("No class declaration found")

    def _clean_code(self, code: str) -> str:
        """Clean up the code by removing comments and unnecessary whitespace."""
        # Remove comments
        code = re.sub(r'//.*', '', code)
        code = re.sub(r'/\*[\s\S]*?\*/', '', code)
        
        # Remove unnecessary whitespace
        code = re.sub(r'\s+', ' ', code)
        code = re.sub(r'\n+', '\n', code)
        
        return code.strip()

    def _validate_code(self, code: str) -> None:
        """
        Validate the cleaned code for TypeScript compilation requirements.
        
        Raises:
            ParserError: If code doesn't meet TypeScript compilation requirements
        """
        # Check for required TypeScript features
        if 'interface' in code and not re.search(r'interface\s+\w+', code):
            raise ParserError("Invalid interface declaration")
            
        if 'type' in code and not re.search(r'type\s+\w+', code):
            raise ParserError("Invalid type declaration")
            
        if 'enum' in code and not re.search(r'enum\s+\w+', code):
            raise ParserError("Invalid enum declaration")
            
        # Check for proper type annotations
        if ':' in code and not re.search(r':\s*[A-Za-z<>\[\]|&]+', code):
            raise ParserError("Invalid type annotation")
            
        # Check for proper class implementation
        if 'implements' in code and not re.search(r'class\s+\w+\s+implements\s+\w+', code):
            raise ParserError("Invalid class implementation")
            
        # Check for proper extends
        if 'extends' in code and not re.search(r'class\s+\w+\s+extends\s+\w+', code):
            raise ParserError("Invalid class extension")

    def _extract_code_block(self, response: str) -> Optional[str]:
        """Extract a TypeScript code block from the LLM response."""
        for pattern in self.code_block_patterns:
            match = re.search(pattern, response)
            if match:
                return match.group(1)
        return None

    def _extract_code_block(self, response: str) -> Optional[str]:
        """Extract a TypeScript code block from the LLM response."""
        for pattern in self.code_block_patterns:
            match = re.search(pattern, response)
            if match:
                return match.group(1)
        return None 