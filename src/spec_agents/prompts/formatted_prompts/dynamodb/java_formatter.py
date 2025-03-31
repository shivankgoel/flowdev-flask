import os
from typing import List, Any
from src.specs.dynamodb_spec import DynamoDBTableSpec
from ..base_formatter import BaseFormatter

class JavaDynamoDBFormatter(BaseFormatter):
    """Formatter for Java DynamoDB code generation."""
    
    def __init__(self):
        self.template_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'prompt_templates',
            'dynamodb',
            'java.txt'
        )
        super().__init__(self.template_path)

    @staticmethod
    def _format_attributes(attributes: List[Any]) -> str:
        """
        Format DynamoDB attributes for Java code generation.
        
        Args:
            attributes: List of DynamoDB attributes
            
        Returns:
            str: Formatted attributes string
        """
        return "\n".join([
            f"- {attr.name}: {JavaDynamoDBFormatter._map_java_type(attr.type)}"
            for attr in attributes
        ])
    
    @staticmethod
    def _map_java_type(dynamo_type: str) -> str:
        """
        Map DynamoDB types to Java types.
        
        Args:
            dynamo_type: DynamoDB type string
            
        Returns:
            str: Corresponding Java type
        """
        type_mapping = {
            "String": "String",
            "Number": "Double",
            "Boolean": "Boolean",
            "Binary": "byte[]",
            "StringSet": "Set<String>",
            "NumberSet": "Set<Double>",
            "BinarySet": "Set<byte[]>",
            "List": "List<Object>",
            "Map": "Map<String, Object>"
        }
        return type_mapping.get(dynamo_type, "Object") 