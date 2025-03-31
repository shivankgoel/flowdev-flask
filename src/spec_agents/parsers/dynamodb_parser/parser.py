from typing import Dict, Any
from ..generated_code_parser import GeneratedCode
from ..generated_code_parser.python_parser import PythonCodeParser
from ..generated_code_parser.typescript_parser import TypeScriptCodeParser
from ..generated_code_parser.java_parser import JavaCodeParser

class DynamoDBParser:
    """Simple parser that routes to language-specific parsers."""
    
    def __init__(self):
        self.parsers = {
            'python': PythonCodeParser(),
            'typescript': TypeScriptCodeParser(),
            'java': JavaCodeParser()
        }
    
    def parse(self, response: str, language: str) -> GeneratedCode:
        """
        Parse the LLM response using the appropriate language parser.
        
        Args:
            response: The LLM response string
            language: The programming language of the code
            
        Returns:
            GeneratedCode: Parsed code with metadata
            
        Raises:
            ValueError: If language is not supported
        """
        if language not in self.parsers:
            raise ValueError(f"Unsupported language: {language}")
            
        return self.parsers[language].parse(response) 