from typing import Dict, Any, List, Optional
from . import BasePromptTemplate

class OverallFeedbackPrompt(BasePromptTemplate):
    """Prompt for generating overall system feedback"""
    
    def __init__(self):
        self.base_prompt = """You are an expert software architect and code reviewer. Your task is to analyze the generated code and provide comprehensive feedback on the overall system architecture, layer interactions, and data flow.

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
    
    def create_prompt(self, layer_spec: Dict[str, Any], parent_code: Optional[str] = None, feedback: Optional[Dict] = None, layer_dependencies: Optional[Dict] = None) -> str:
        """Create the prompt for overall feedback"""
        
        # Build layer specs section
        layer_specs_text = "\nLayer Specifications:\n"
        for spec in layer_spec:
            layer_specs_text += f"\nLayer ID: {spec['layer_id']}"
            layer_specs_text += f"\nType: {spec['layer_type']}"
            layer_specs_text += f"\nDescription: {spec['description']}"
            layer_specs_text += "\nMethods:"
            for method in spec.get("methods", []):
                layer_specs_text += f"\n  - {method['name']}: {method['description']}"
            layer_specs_text += "\n"
        
        # Build generated code section
        generated_code_text = "\nGenerated Code:\n"
        if parent_code:
            generated_code_text += f"\n{parent_code}\n"
        
        # Build layer feedback section
        layer_feedback_text = "\nLayer Feedback:\n"
        if feedback:
            for fb in feedback:
                if fb.get("type") == "layer":
                    layer_feedback_text += f"\nLayer ID: {fb.get('layer_id')}"
                    layer_feedback_text += f"\nNeeds Update: {fb.get('needs_update', False)}"
                    layer_feedback_text += f"\nCritical Issues: {len(fb.get('critical_issues', []))}"
                    layer_feedback_text += f"\nSummary: {fb.get('summary', '')}\n"
        
        # Add layer dependencies if available
        if layer_dependencies:
            layer_deps_text = "\nLayer Dependencies:\n"
            for dep_id, dep_info in layer_dependencies.items():
                layer_deps_text += f"\n- {dep_id}: {dep_info}"
            layer_specs_text += layer_deps_text
        
        # Combine all sections
        prompt = f"{self.base_prompt}\n\n{layer_specs_text}\n{generated_code_text}\n{layer_feedback_text}"
        
        return prompt 