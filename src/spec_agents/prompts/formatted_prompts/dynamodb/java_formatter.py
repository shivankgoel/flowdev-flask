import os
from typing import List, Any, Dict
from specs.dynamodb_spec import DynamoDBTableSpec

class JavaDynamoDBFormatter:
    def __init__(self):
        self.format_template_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'code_generation_format',
            'java_format.txt'
        )

    def _read_format_template(self) -> str:
        """Read the format template from file."""
        with open(self.format_template_path, 'r') as f:
            return f.read()

    def format_prompt(self, prompt: str, **kwargs) -> str:
        """Format the prompt with the given parameters."""
        # Read the format template
        format_template = self._read_format_template()
        
        # Replace the format template placeholder in the prompt
        formatted_prompt = prompt.replace(
            '{code_generation_format/java_format.txt}',
            format_template
        )
        
        # Format any other placeholders in the prompt
        return formatted_prompt.format(**kwargs)

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