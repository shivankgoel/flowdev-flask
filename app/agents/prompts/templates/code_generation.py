"""Templates for code generation prompts"""

from .base import CODE_REQUIREMENTS, LAYER_INFO_TEMPLATE, PARENT_CODE_TEMPLATE

# Code generation base prompt
CODE_GENERATION_BASE = """You are an expert software developer. Your task is to generate high-quality, production-ready code based on the provided layer specification.

{code_requirements}

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

# Code generation class structure template
CLASS_STRUCTURE_TEMPLATE = """Class Structure:
- Base Class: DynamoDBDAO (You must generate this first)
  - Common DynamoDB operations
  - Error handling
  - Logging
  - Connection management
  - Table operations

- Specific Class: {class_name} (extends DynamoDBDAO)
  - Table-specific operations
  - Business logic
  - Data validation"""

# Layer dependencies template
LAYER_DEPENDENCIES_TEMPLATE = """

Layer Dependencies:
{dependencies}"""

# Feedback template
FEEDBACK_TEMPLATE = """

Feedback:
{feedback}""" 