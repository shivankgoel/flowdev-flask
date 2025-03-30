"""Base prompt templates for all agents"""

# Common prompt sections
CODE_REQUIREMENTS = """Please generate the code with:
1. Type hints for all parameters and return values
2. Comprehensive docstrings following Google style
3. Proper error handling with try/except blocks
4. Logging statements for important operations
5. Follow Python best practices and PEP 8 style guide
6. Include all necessary imports
7. Make the code production-ready and maintainable"""

# Common JSON response format
JSON_RESPONSE_FORMAT = """Please provide your response in the following JSON format:

{
    "status": "completed",
    "feedback": {
        "scores": {
            "code_quality": <score 0-100>,
            "error_handling": <score 0-100>,
            "documentation": <score 0-100>,
            "testability": <score 0-100>
        },
        "issues": [
            {
                "severity": "high|medium|low",
                "description": "Issue description",
                "suggestion": "How to fix"
            }
        ],
        "suggestions": [
            "Suggestion 1",
            "Suggestion 2"
        ],
        "critical_issues": [
            {
                "severity": "high|medium|low",
                "description": "Critical issue description",
                "impact": "Impact on the system",
                "suggestion": "How to fix"
            }
        ],
        "summary": "Overall summary of the code review"
    },
    "needs_update": <boolean>
}"""

# Common layer info template
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

# Common parent code template
PARENT_CODE_TEMPLATE = """

Parent Layer Code:
{parent_code}""" 