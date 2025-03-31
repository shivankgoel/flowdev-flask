from typing import List, Tuple
from .base_parser import DynamoDBBaseParser
from ..generated_code_parser import GeneratedCode
from ..generated_code_parser.python_parser import PythonCodeParser

class PythonDynamoDBParser(DynamoDBBaseParser, PythonCodeParser):
    """Parser for Python DynamoDB code generation."""
    
    def __init__(self):
        DynamoDBBaseParser.__init__(self)
        PythonCodeParser.__init__(self)
        self.required_dynamodb_imports.extend([
            "boto3"
        ])
        
    def parse(self, response: str, table_name: str, primary_key: str) -> GeneratedCode:
        """
        Parse the LLM response for Python DynamoDB code.
        
        Args:
            response: The LLM response string
            table_name: The DynamoDB table name
            primary_key: The primary key name
            
        Returns:
            GeneratedCode: Parsed code with metadata
            
        Raises:
            ValueError: If response is invalid or missing required elements
        """
        # First parse using Python parser to validate Python-specific syntax
        result = PythonCodeParser.parse(self, response)
        
        # Then validate DynamoDB-specific requirements
        self._validate_dynamodb_imports(result.imports)
        self._validate_table_name(result.code, table_name)
        self._validate_primary_key(result.code, primary_key)
        self._validate_required_methods(result.code)
        
        # Validate Python-specific DynamoDB patterns
        self._validate_python_dynamodb_patterns(result.code)
        
        return result
        
    def _validate_python_dynamodb_patterns(self, code: str) -> None:
        """
        Validate Python-specific DynamoDB patterns.
        
        Args:
            code: The generated code
            
        Raises:
            ValueError: If Python-specific patterns are invalid
        """
        # Check for at least one boto3 pattern
        boto3_patterns = [
            "boto3.client('dynamodb')",
            "boto3.resource('dynamodb')",
            "dynamodb = boto3"
        ]
        
        has_boto3 = any(pattern in code for pattern in boto3_patterns)
        if not has_boto3:
            raise ValueError("No boto3 patterns found")
            
        # Check for at least one table operation
        table_patterns = [
            "table = dynamodb.Table",
            "table.put_item",
            "table.get_item",
            "table.update_item",
            "table.delete_item"
        ]
        
        has_table_op = any(pattern in code for pattern in table_patterns)
        if not has_table_op:
            raise ValueError("No table operations found")
            
        # Check for basic error handling
        if "try:" not in code and "except" not in code:
            raise ValueError("No error handling found")
            
        # Check for async support only if async is used
        if "async def" in code and "aioboto3" not in code:
            raise ValueError("Missing aioboto3 for async support") 