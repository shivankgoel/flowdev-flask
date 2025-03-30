from typing import Dict, Any, List, Optional
from . import BasePromptTemplate

class LayerFeedbackPrompt(BasePromptTemplate):
    """Prompt for generating layer-specific feedback"""
    
    def __init__(self):
        self.base_prompt = """You are an expert code reviewer. Your task is to analyze the generated code and provide detailed feedback on its implementation.

Please provide your feedback in the following JSON format:

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
}

Guidelines for feedback:
1. Be lenient with minor issues - only mark issues as critical if they would cause system failures
2. Focus on code quality, error handling, and documentation
3. Consider the layer's specific responsibilities and requirements
4. Provide constructive feedback that helps improve the code
5. Only request updates for issues that would impact system reliability or security"""
    
    def create_prompt(self, layer_spec: Dict[str, Any], parent_code: Optional[str] = None, feedback: Optional[Dict] = None, layer_dependencies: Optional[Dict] = None) -> str:
        """Create the prompt for layer feedback"""
        
        # Build layer info section
        layer_info = f"""Layer Information:
- Layer ID: {layer_spec['layer_id']}
- Language: {layer_spec['language']}
- Artifact Type: {layer_spec['artifact_type']}
- Functionality Type: {layer_spec['functionality_type']}

Generated Code:
{parent_code if parent_code else "No code generated yet"}"""
        
        # Add layer dependencies if available
        if layer_dependencies:
            layer_info += "\n\nLayer Dependencies:"
            for dep_id, dep_info in layer_dependencies.items():
                layer_info += f"\n- {dep_id}: {dep_info}"
        
        # Add previous feedback if available
        if feedback:
            layer_info += f"\n\nPrevious Feedback:\n{feedback}"
        
        # Combine all sections
        prompt = f"{self.base_prompt}\n\n{layer_info}"
        
        return prompt 