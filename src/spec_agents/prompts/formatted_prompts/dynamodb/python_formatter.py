import os
from typing import List, Any
from src.specs.dynamodb_spec import DynamoDBTableSpec
from ..base_formatter import BaseFormatter

class PythonDynamoDBFormatter(BaseFormatter):
    """Formatter for Python DynamoDB code generation."""
    
    def __init__(self):
        self.template_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'prompt_templates',
            'dynamodb',
            'python.txt'
        )
        super().__init__(self.template_path)

    @staticmethod
    def _format_attributes(attributes: List[Any]) -> str:
        """
        Format DynamoDB attributes for Python code generation.
        
        Args:
            attributes: List of DynamoDB attributes
            
        Returns:
            str: Formatted attributes string
        """
        return "\n".join([
            f"- {attr.name}: {PythonDynamoDBFormatter._map_python_type(attr.type)}"
            for attr in attributes
        ])
    
    @staticmethod
    def _map_python_type(dynamo_type: str) -> str:
        """
        Map DynamoDB types to Python types.
        
        Args:
            dynamo_type: DynamoDB type string
            
        Returns:
            str: Corresponding Python type
        """
        type_mapping = {
            "String": "str",
            "Number": "float",
            "Boolean": "bool",
            "Binary": "bytes",
            "StringSet": "Set[str]",
            "NumberSet": "Set[float]",
            "BinarySet": "Set[bytes]",
            "List": "List[Any]",
            "Map": "Dict[str, Any]"
        }
        return type_mapping.get(dynamo_type, "Any") 