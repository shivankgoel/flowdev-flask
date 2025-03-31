from typing import List, Tuple
from .base_parser import DynamoDBBaseParser
from ..generated_code_parser import GeneratedCode
from ..generated_code_parser.java_parser import JavaCodeParser

class JavaDynamoDBParser(DynamoDBBaseParser, JavaCodeParser):
    """Parser for Java DynamoDB code generation."""
    
    def __init__(self):
        DynamoDBBaseParser.__init__(self)
        JavaCodeParser.__init__(self)
        self.required_dynamodb_imports.extend([
            "software.amazon.awssdk.services.dynamodb"
        ])
        
    def parse(self, response: str, table_name: str, primary_key: str) -> GeneratedCode:
        """
        Parse the LLM response for Java DynamoDB code.
        
        Args:
            response: The LLM response string
            table_name: The DynamoDB table name
            primary_key: The primary key name
            
        Returns:
            GeneratedCode: Parsed code with metadata
            
        Raises:
            ValueError: If response is invalid or missing required elements
        """
        # First parse using Java parser to validate Java-specific syntax
        result = JavaCodeParser.parse(self, response)
        
        # Then validate DynamoDB-specific requirements
        self._validate_dynamodb_imports(result.imports)
        self._validate_table_name(result.code, table_name)
        self._validate_primary_key(result.code, primary_key)
        self._validate_required_methods(result.code)
        
        # Validate Java-specific DynamoDB patterns
        self._validate_java_dynamodb_patterns(result.code)
        
        return result
        
    def _validate_java_dynamodb_patterns(self, code: str) -> None:
        """
        Validate Java-specific DynamoDB patterns.
        
        Args:
            code: The generated code
            
        Raises:
            ValueError: If Java-specific patterns are invalid
        """
        # Check for at least one AWS SDK v2 pattern
        sdk_patterns = [
            "DynamoDbClient",
            "DynamoDbEnhancedClient",
            "TableSchema",
            "DynamoDbTable"
        ]
        
        has_sdk_pattern = any(pattern in code for pattern in sdk_patterns)
        if not has_sdk_pattern:
            raise ValueError("No AWS SDK v2 patterns found")
            
        # Check for at least one operation pattern
        operation_patterns = [
            "PutItemEnhancedRequest",
            "GetItemEnhancedRequest",
            "UpdateItemEnhancedRequest",
            "DeleteItemEnhancedRequest"
        ]
        
        has_operation = any(pattern in code for pattern in operation_patterns)
        if not has_operation:
            raise ValueError("No DynamoDB operation patterns found")
            
        # Check for basic error handling
        if "DynamoDbException" not in code and "Exception" not in code:
            raise ValueError("No exception handling found") 