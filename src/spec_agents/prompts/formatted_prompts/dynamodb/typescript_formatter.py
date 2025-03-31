import os
from typing import List, Any
from src.specs.dynamodb_spec import DynamoDBTableSpec
from ..base_formatter import BaseFormatter

class TypeScriptDynamoDBFormatter(BaseFormatter):
    """Formatter for TypeScript DynamoDB code generation."""
    
    def __init__(self):
        self.template_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'prompt_templates',
            'dynamodb',
            'typescript.txt'
        )
        super().__init__(self.template_path)

    @staticmethod
    def _format_attributes(attributes: List[Any]) -> str:
        """
        Format DynamoDB attributes for TypeScript code generation.
        
        Args:
            attributes: List of DynamoDB attributes
            
        Returns:
            str: Formatted attributes string
        """
        return "\n".join([
            f"- {attr.name}: {TypeScriptDynamoDBFormatter._map_typescript_type(attr.type)}"
            for attr in attributes
        ])
    
    @staticmethod
    def _map_typescript_type(dynamo_type: str) -> str:
        """
        Map DynamoDB types to TypeScript types.
        
        Args:
            dynamo_type: DynamoDB type string
            
        Returns:
            str: Corresponding TypeScript type
        """
        type_mapping = {
            "String": "string",
            "Number": "number",
            "Boolean": "boolean",
            "Binary": "Buffer",
            "StringSet": "Set<string>",
            "NumberSet": "Set<number>",
            "BinarySet": "Set<Buffer>",
            "List": "any[]",
            "Map": "Record<string, any>"
        }
        return type_mapping.get(dynamo_type, "any") 