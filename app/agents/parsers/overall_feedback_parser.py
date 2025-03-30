from typing import Dict, Any, List, Optional
import json
import re

class OverallFeedbackParser:
    """Parser for overall system feedback responses"""
    
    @staticmethod
    def parse_feedback(response: str) -> Dict[str, Any]:
        """
        Parse the overall feedback response into a structured format.
        
        Expected format:
        {
            "status": "completed",
            "feedback": {
                "layer_interactions": {
                    "score": 0-100,
                    "issues": [
                        {
                            "severity": "low/medium/high",
                            "description": "Issue description",
                            "suggestion": "How to fix"
                        }
                    ]
                },
                "data_flow": {
                    "score": 0-100,
                    "issues": [
                        {
                            "severity": "low/medium/high",
                            "description": "Issue description",
                            "suggestion": "How to fix"
                        }
                    ]
                },
                "system_architecture": {
                    "score": 0-100,
                    "issues": [
                        {
                            "severity": "low/medium/high",
                            "description": "Issue description",
                            "suggestion": "How to fix"
                        }
                    ]
                },
                "critical_issues": [
                    "Only list issues that MUST be fixed before proceeding"
                ],
                "summary": "Overall assessment"
            },
            "needs_update": false,  // Only set to true if there are critical issues that must be fixed
            "layers_to_update": []  // Only list layers that MUST be updated to fix critical issues
        }
        """
        try:
            # Try to parse as JSON first
            if isinstance(response, str):
                response = json.loads(response)
            
            # Validate required fields
            if "status" not in response:
                raise ValueError("Missing required field: status")
            
            if "feedback" not in response:
                raise ValueError("Missing required field: feedback")
            
            feedback = response["feedback"]
            if "layer_interactions" not in feedback:
                raise ValueError("Missing required field: feedback.layer_interactions")
            
            if "data_flow" not in feedback:
                raise ValueError("Missing required field: feedback.data_flow")
            
            if "system_architecture" not in feedback:
                raise ValueError("Missing required field: feedback.system_architecture")
            
            if "critical_issues" not in feedback:
                raise ValueError("Missing required field: feedback.critical_issues")
            
            if "summary" not in feedback:
                raise ValueError("Missing required field: feedback.summary")
            
            # Set needs_update based on critical issues
            response["needs_update"] = bool(feedback["critical_issues"])
            
            return response
            
        except json.JSONDecodeError:
            # If not JSON, try to extract structured data from text
            return OverallFeedbackParser._parse_text_response(response)
    
    @staticmethod
    def _parse_text_response(response: str) -> Dict[str, Any]:
        """Parse feedback from text format if JSON parsing fails"""
        result = {
            "status": "completed",
            "feedback": {
                "layer_interactions": {
                    "score": 80,
                    "issues": []
                },
                "data_flow": {
                    "score": 80,
                    "issues": []
                },
                "system_architecture": {
                    "score": 80,
                    "issues": []
                },
                "critical_issues": [],
                "summary": "System looks good overall"
            },
            "needs_update": False,
            "layers_to_update": []
        }
        
        # Extract scores and issues for each category
        categories = ["layer_interactions", "data_flow", "system_architecture"]
        for category in categories:
            category_section = re.search(
                f"{category}:(.*?)(?=\n\n|\Z)",
                response,
                re.DOTALL | re.IGNORECASE
            )
            
            if category_section:
                category_text = category_section.group(1)
                
                # Extract score
                score_match = re.search(r"score:\s*(\d+)", category_text, re.IGNORECASE)
                if score_match:
                    score = int(score_match.group(1))
                    if 0 <= score <= 100:
                        result["feedback"][category]["score"] = score
                
                # Extract issues
                issues_section = re.search(r"issues?:(.*?)(?=\n\n|\Z)", category_text, re.DOTALL | re.IGNORECASE)
                if issues_section:
                    for line in issues_section.group(1).split("\n"):
                        if line.strip():
                            result["feedback"][category]["issues"].append({
                                "severity": "medium",
                                "description": line.strip(),
                                "suggestion": "Review and address if needed"
                            })
        
        # Extract critical issues
        critical_section = re.search(r"critical issues?:(.*?)(?=\n\n|\Z)", response, re.DOTALL | re.IGNORECASE)
        if critical_section:
            result["feedback"]["critical_issues"] = [
                line.strip() for line in critical_section.group(1).split("\n")
                if line.strip()
            ]
            result["needs_update"] = bool(result["feedback"]["critical_issues"])
        
        # Extract layers to update
        layers_section = re.search(r"layers? to update:(.*?)(?=\n\n|\Z)", response, re.DOTALL | re.IGNORECASE)
        if layers_section:
            result["layers_to_update"] = [
                line.strip() for line in layers_section.group(1).split("\n")
                if line.strip()
            ]
        
        # Extract summary
        summary_section = re.search(r"summary:(.*?)(?=\n\n|\Z)", response, re.DOTALL | re.IGNORECASE)
        if summary_section:
            result["feedback"]["summary"] = summary_section.group(1).strip()
        
        return result 