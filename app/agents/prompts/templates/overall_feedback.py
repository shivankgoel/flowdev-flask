"""Templates for overall feedback prompts"""

from .base import JSON_RESPONSE_FORMAT, LAYER_INFO_TEMPLATE

# Overall feedback base prompt
OVERALL_FEEDBACK_BASE = """You are an expert software architect and code reviewer. Your task is to analyze the generated code and provide comprehensive feedback on the overall system architecture, layer interactions, and data flow.

Please provide your feedback in the following JSON format:

{
    "status": "completed",
    "feedback": {
        "layer_interactions": {
            "score": <score 0-100>,
            "issues": [
                {
                    "severity": "high|medium|low",
                    "description": "Issue description",
                    "suggestion": "How to fix"
                }
            ]
        },
        "data_flow": {
            "score": <score 0-100>,
            "issues": [
                {
                    "severity": "high|medium|low",
                    "description": "Issue description",
                    "suggestion": "How to fix"
                }
            ]
        },
        "system_architecture": {
            "score": <score 0-100>,
            "issues": [
                {
                    "severity": "high|medium|low",
                    "description": "Issue description",
                    "suggestion": "How to fix"
                }
            ]
        }
    },
    "needs_update": <boolean>,
    "layers_to_update": [
        {
            "layer_id": "layer identifier",
            "reason": "Why this layer needs updating"
        }
    ],
    "critical_issues": [
        {
            "severity": "high|medium|low",
            "description": "Critical issue description",
            "impact": "Impact on the system",
            "suggestion": "How to fix"
        }
    ],
    "summary": "Overall summary of the system architecture and recommendations"
}

Guidelines for feedback:
1. Focus on architectural concerns and system-wide issues
2. Evaluate layer interactions and dependencies
3. Assess data flow and state management
4. Consider scalability and maintainability
5. Provide constructive feedback that helps improve the system"""

# Layer specs template
LAYER_SPECS_TEMPLATE = """

Layer Specifications:
{specs}"""

# Generated code template
GENERATED_CODE_TEMPLATE = """

Generated Code:
{code}"""

# Layer feedback template
LAYER_FEEDBACK_TEMPLATE = """

Layer Feedback:
{feedback}"""

# Layer dependencies template
LAYER_DEPENDENCIES_TEMPLATE = """

Layer Dependencies:
{dependencies}""" 