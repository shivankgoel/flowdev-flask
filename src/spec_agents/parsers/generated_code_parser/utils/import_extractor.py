from typing import List, Tuple
import re

class ImportExtractor:
    """Common import extraction functionality for different programming languages."""
    
    def __init__(self, import_patterns: List[str]):
        """
        Initialize with language-specific import patterns.
        
        Args:
            import_patterns: List of regex patterns for import statements
        """
        self.patterns = [re.compile(pattern, re.MULTILINE) for pattern in import_patterns]
    
    def extract_imports(self, code: str) -> List[str]:
        """
        Extract imports using the configured patterns.
        
        Args:
            code: Complete code string
            
        Returns:
            List[str]: List of import statements
        """
        imports = []
        for pattern in self.patterns:
            for match in pattern.finditer(code):
                # Extract the actual import statement from the match groups
                import_stmt = self._process_match_groups(match.groups())
                if import_stmt:
                    imports.append(import_stmt)
        return imports
    
    def _process_match_groups(self, groups: Tuple) -> str:
        """
        Process match groups to extract the import statement.
        To be overridden by language-specific implementations.
        
        Args:
            groups: Tuple of match groups
            
        Returns:
            str: Processed import statement
        """
        raise NotImplementedError("Subclasses must implement _process_match_groups") 