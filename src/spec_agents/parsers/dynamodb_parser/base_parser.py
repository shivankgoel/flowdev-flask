from typing import Dict, Any, List
from ..generated_code_parser import BaseCodeParser, GeneratedCode

class DynamoDBBaseParser(BaseCodeParser):
    """Base parser for DynamoDB code generation."""
    
    def __init__(self):
        super().__init__()
        # Only require core DynamoDB imports
        self.required_dynamodb_imports = [
            "DynamoDB",
            "DynamoDBClient"
        ]
        
    def _validate_dynamodb_imports(self, imports: List[str]) -> None:
        """
        Validate that at least one DynamoDB import is present.
        
        Args:
            imports: List of import statements
            
        Raises:
            ValueError: If no DynamoDB imports are found
        """
        has_dynamodb_import = any(
            any(imp in import_stmt for imp in self.required_dynamodb_imports)
            for import_stmt in imports
        )
        if not has_dynamodb_import:
            raise ValueError("No DynamoDB imports found")
            
    def _validate_table_name(self, code: str, table_name: str) -> None:
        """
        Validate that the table name is used in the code.
        
        Args:
            code: The generated code
            table_name: The expected table name
            
        Raises:
            ValueError: If table name is not found
        """
        if table_name not in code:
            raise ValueError(f"Table name '{table_name}' not found in code")
            
    def _validate_primary_key(self, code: str, primary_key: str) -> None:
        """
        Validate that the primary key is used in the code.
        
        Args:
            code: The generated code
            primary_key: The expected primary key name
            
        Raises:
            ValueError: If primary key is not found
        """
        if primary_key not in code:
            raise ValueError(f"Primary key '{primary_key}' not found in code")
            
    def _validate_required_methods(self, code: str) -> None:
        """
        Validate that at least one CRUD operation is present.
        
        Args:
            code: The generated code
            
        Raises:
            ValueError: If no CRUD operations are found
        """
        crud_operations = [
            "putItem", "getItem", "updateItem", "deleteItem",
            "put_item", "get_item", "update_item", "delete_item",
            "PutItem", "GetItem", "UpdateItem", "DeleteItem"
        ]
        
        has_crud = any(op in code for op in crud_operations)
        if not has_crud:
            raise ValueError("No CRUD operations found in code") 