from typing import List, Tuple
from .base_parser import DynamoDBBaseParser
from ..generated_code_parser import GeneratedCode
from ..generated_code_parser.typescript_parser import TypeScriptCodeParser

class TypeScriptDynamoDBParser(DynamoDBBaseParser, TypeScriptCodeParser):
    """Parser for TypeScript DynamoDB code generation."""
    
    def __init__(self):
        DynamoDBBaseParser.__init__(self)
        TypeScriptCodeParser.__init__(self)
        self.required_dynamodb_imports.extend([
            "@aws-sdk/client-dynamodb"
        ])
        
    def parse(self, response: str, table_name: str, primary_key: str) -> GeneratedCode:
        """
        Parse the LLM response for TypeScript DynamoDB code.
        
        Args:
            response: The LLM response string
            table_name: The DynamoDB table name
            primary_key: The primary key name
            
        Returns:
            GeneratedCode: Parsed code with metadata
            
        Raises:
            ValueError: If response is invalid or missing required elements
        """
        # First parse using TypeScript parser to validate TypeScript-specific syntax
        result = TypeScriptCodeParser.parse(self, response)
        
        # Then validate DynamoDB-specific requirements
        self._validate_dynamodb_imports(result.imports)
        self._validate_table_name(result.code, table_name)
        self._validate_primary_key(result.code, primary_key)
        self._validate_required_methods(result.code)
        
        # Validate TypeScript-specific DynamoDB patterns
        self._validate_typescript_dynamodb_patterns(result.code)
        
        return result
        
    def _validate_typescript_dynamodb_patterns(self, code: str) -> None:
        """
        Validate TypeScript-specific DynamoDB patterns.
        
        Args:
            code: The generated code
            
        Raises:
            ValueError: If TypeScript-specific patterns are invalid
        """
        # Check for at least one AWS SDK v3 pattern
        sdk_patterns = [
            "DynamoDBClient",
            "DynamoDBDocumentClient"
        ]
        
        has_sdk_pattern = any(pattern in code for pattern in sdk_patterns)
        if not has_sdk_pattern:
            raise ValueError("No AWS SDK v3 patterns found")
            
        # Check for at least one operation pattern
        operation_patterns = [
            "PutCommand",
            "GetCommand",
            "UpdateCommand",
            "DeleteCommand",
            "QueryCommand",
            "ScanCommand"
        ]
        
        has_operation = any(pattern in code for pattern in operation_patterns)
        if not has_operation:
            raise ValueError("No DynamoDB operation patterns found")
            
        # Check for basic error handling
        if "try {" not in code and "catch" not in code:
            raise ValueError("No error handling found")
            
        # Check for async/await only if async is used
        if "async" in code and "await" not in code:
            raise ValueError("Missing await in async functions") 