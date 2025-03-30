from typing import Dict, Any, List, Optional
from . import BasePromptTemplate
import json

# Prompt templates
LAYER_INFO_TEMPLATE = """Layer Information:
- Layer ID: {layer_id}
- Language: {language}
- Artifact Type: {artifact_type}
- Functionality Type: {functionality_type}

Required Imports:
{imports}

Class Structure:
- Class Name: {class_name}
- Base Class: {base_class}

Fields:
{fields}

Required Methods:
{required_methods}"""

CODE_REQUIREMENTS = """Please generate the code with:
1. Type hints for all parameters and return values
2. Comprehensive docstrings following Google style
3. Proper error handling with try/except blocks
4. Logging statements for important operations
5. Follow Python best practices and PEP 8 style guide
6. Include all necessary imports
7. Make the code production-ready and maintainable"""

PARENT_CODE_TEMPLATE = """

Parent Layer Code:
{parent_code}"""

class LayerCodeGenerationPrompt(BasePromptTemplate):
    """Prompt for generating code for a specific layer"""
    
    def __init__(self):
        self.base_prompt = """You are an expert software developer. Your task is to generate high-quality, production-ready code based on the provided layer specification.

Please generate the code with:
1. Type hints for all parameters and return values
2. Comprehensive docstrings following Google style
3. Proper error handling with try/except blocks
4. Logging statements for important operations
5. Follow Python best practices and PEP 8 style guide
6. Include all necessary imports
7. Make the code production-ready and maintainable

IMPORTANT: You must generate TWO classes:
1. First, generate the base DynamoDBDAO class with common functionality
2. Then, generate the specific DAO class that extends it

Please provide your response in the following JSON format:

{
    "status": "completed",
    "generated_code": {
        "language": "python",
        "code": "Your generated code here (including both classes)",
        "imports": [
            "import os",
            "import json"
        ],
        "dependencies": [
            "boto3>=1.26.0"
        ],
        "notes": [
            "Note 1",
            "Note 2"
        ]
    },
    "metadata": {
        "class_name": "ExampleClass",
        "base_class": "BaseClass",
        "methods": [
            "method1",
            "method2"
        ],
        "fields": [
            "field1",
            "field2"
        ],
        "complexity": "medium",
        "estimated_lines": 50
    }
}"""
    
    def create_prompt(self, layer_spec: Dict[str, Any], parent_code: Optional[str] = None, feedback: Optional[Dict] = None, layer_dependencies: Optional[Dict] = None) -> str:
        """Create the prompt for code generation"""
        
        # Get base class and imports based on functionality type
        base_class, imports = self._get_base_class_and_imports(layer_spec)
        
        # Generate class name
        class_name = self._generate_class_name(layer_spec)
        
        # Format fields and methods
        fields = self._format_fields(layer_spec)
        required_methods = self._get_required_methods(layer_spec)
        
        # Build layer info section
        layer_info = f"""Layer Information:
- Layer ID: {layer_spec['layer_id']}
- Language: {layer_spec['language']}
- Artifact Type: {layer_spec['artifact_type']}
- Functionality Type: {layer_spec['functionality_type']}

Required Imports:
{imports}

Class Structure:
- Base Class: DynamoDBDAO (You must generate this first)
  - Common DynamoDB operations
  - Error handling
  - Logging
  - Connection management
  - Table operations

- Specific Class: {class_name} (extends DynamoDBDAO)
  - Table-specific operations
  - Business logic
  - Data validation

{fields}

Required Methods:
{required_methods}"""
        
        # Add layer dependencies if available
        if layer_dependencies:
            layer_info += "\n\nLayer Dependencies:"
            for dep_id, dep_info in layer_dependencies.items():
                layer_info += f"\n- {dep_id}: {dep_info}"
        
        # Add parent code if available
        if parent_code:
            layer_info += f"\n\nParent Code:\n{parent_code}"
        
        # Add feedback if available
        if feedback:
            layer_info += f"\n\nFeedback:\n{feedback}"
        
        # Combine all sections
        prompt = f"{self.base_prompt}\n\n{layer_info}"
        
        return prompt

    def _format_fields(self, layer_spec: Dict[str, Any]) -> str:
        """Format the fields for the prompt"""
        formatted = []
        
        # Handle table configuration if present
        if "properties" in layer_spec and "table_config" in layer_spec["properties"]:
            table_config = layer_spec["properties"]["table_config"]
            formatted.append(f"- Table Name: {table_config['table_name']}")
            formatted.append(f"- Partition Key: {table_config['partition_key']}")
            formatted.append(f"- Sort Key: {table_config['sort_key']}")
        
        # Handle attributes if present
        if "properties" in layer_spec and "attributes" in layer_spec["properties"]:
            formatted.append("\nAttributes:")
            for name, attr in layer_spec["properties"]["attributes"].items():
                type_info = attr.get("type", "")
                description = attr.get("description", "")
                enum_values = attr.get("enum", [])
                enum_str = f" (enum: {', '.join(enum_values)})" if enum_values else ""
                formatted.append(f"- {name}: {type_info}{enum_str}")
                if description:
                    formatted.append(f"  Description: {description}")
        
        return "\n".join(formatted)

    def _get_required_methods(self, layer_spec: Dict[str, Any]) -> str:
        """Get the required methods based on functionality type"""
        methods = []
        
        if layer_spec["functionality_type"] == "ddb":
            methods.extend([
                "create_item(self, item: Dict[str, Any]) -> Dict[str, Any]",
                "get_item(self, key: Dict[str, Any]) -> Dict[str, Any]",
                "update_item(self, key: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]",
                "delete_item(self, key: Dict[str, Any]) -> None",
                "query_items(self, query_params: Dict[str, Any]) -> List[Dict[str, Any]]"
            ])
        elif layer_spec["functionality_type"] == "business_logic":
            if "properties" in layer_spec and "methods" in layer_spec["properties"]:
                for method in layer_spec["properties"]["methods"]:
                    params = ", ".join(f"{p['name']}: {p['type']}" for p in method["parameters"])
                    methods.append(f"{method['name']}(self, {params}) -> {method['return_type']}")
        
        return "\n".join(f"- {method}" for method in methods)

    def _get_base_class_and_imports(self, layer_spec: Dict[str, Any]) -> tuple[str, str]:
        """Get the appropriate base class and imports based on functionality type"""
        functionality_type = layer_spec.get("functionality_type", "")
        
        if functionality_type == "ddb":
            return (
                "DynamoDBDAO",
                """from typing import Dict, Any, Optional, List
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
import logging"""
            )
        elif functionality_type == "s3":
            return (
                "S3DAO",
                """from typing import Dict, Any, Optional, BinaryIO
import boto3
from botocore.exceptions import ClientError
import logging"""
            )
        elif functionality_type == "business_logic":
            return (
                "BaseService",
                """from typing import Dict, Any, Optional, List
import logging"""
            )
        elif functionality_type == "api":
            return (
                "BaseController",
                """from typing import Dict, Any, Optional, List
from flask import Blueprint, request, jsonify
import logging"""
            )
        else:
            return (
                "object",
                """from typing import Dict, Any, Optional, List
import logging"""
            )

    def _generate_class_name(self, layer_spec: Dict[str, Any]) -> str:
        """Generate an appropriate class name based on layer specification"""
        # Extract the main entity name from the layer_id
        layer_id = layer_spec.get("layer_id", "")
        if layer_id:
            entity_name = layer_id.split('_')[0].capitalize()
        else:
            entity_name = "Entity"
        
        if layer_spec["functionality_type"] == "ddb":
            return f"{entity_name}DynamoDBDAO"
        elif layer_spec["functionality_type"] == "s3":
            return f"{entity_name}S3DAO"
        elif layer_spec["functionality_type"] == "business_logic":
            return f"{entity_name}Service"
        elif layer_spec["functionality_type"] == "api":
            return f"{entity_name}Controller"
        else:
            return f"{entity_name}Service" 