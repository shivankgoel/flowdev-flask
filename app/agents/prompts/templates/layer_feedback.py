"""Templates for layer feedback prompts"""

from .base import JSON_RESPONSE_FORMAT, LAYER_INFO_TEMPLATE, PARENT_CODE_TEMPLATE

# Layer feedback base prompt
LAYER_FEEDBACK_BASE = """You are an expert code reviewer. Your task is to analyze the generated code and provide detailed feedback on its implementation.

Please review the code and provide feedback in the following JSON format:

{json_response_format}

Guidelines for feedback:
1. Be lenient with minor issues - only mark issues as critical if they would cause system failures
2. Focus on code quality, error handling, and documentation
3. Consider the layer's specific responsibilities and requirements
4. Provide constructive feedback that helps improve the code
5. Only request updates for issues that would impact system reliability or security"""

# Generated code template
GENERATED_CODE_TEMPLATE = """

Generated Code:
{code}"""

# Layer dependencies template
LAYER_DEPENDENCIES_TEMPLATE = """

Layer Dependencies:
{dependencies}"""

# Previous feedback template
PREVIOUS_FEEDBACK_TEMPLATE = """

Previous Feedback:
{feedback}""" 