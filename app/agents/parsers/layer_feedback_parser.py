from typing import Dict, Any, List, Optional
import json
import re

class LayerFeedbackParser:
    """Parser for layer feedback responses"""
    
    @staticmethod
    def parse_feedback(response: str) -> Dict[str, Any]:
        """
        Parse the feedback response into a structured format.
        
        Expected format:
        {
            "status": "completed",
            "feedback": {
                "scores": {
                    "code_quality": 0-100,
                    "type_safety": 0-100,
                    "error_handling": 0-100,
                    "documentation": 0-100,
                    "best_practices": 0-100
                },
                "issues": [
                    {
                        "severity": "low/medium/high",
                        "category": "code_quality/type_safety/error_handling/documentation/best_practices",
                        "description": "Issue description",
                        "suggestion": "How to fix"
                    }
                ],
                "suggestions": [
                    "Optional improvement suggestions"
                ],
                "critical_issues": [
                    "Only list issues that MUST be fixed before proceeding"
                ],
                "summary": "Overall assessment"
            },
            "needs_update": false  // Only set to true if there are critical issues that must be fixed
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
            if "scores" not in feedback:
                raise ValueError("Missing required field: feedback.scores")
            
            if "issues" not in feedback:
                raise ValueError("Missing required field: feedback.issues")
            
            if "critical_issues" not in feedback:
                raise ValueError("Missing required field: feedback.critical_issues")
            
            if "summary" not in feedback:
                raise ValueError("Missing required field: feedback.summary")
            
            # Set needs_update based on critical issues
            response["needs_update"] = bool(feedback["critical_issues"])
            
            return response
            
        except json.JSONDecodeError:
            # If not JSON, try to extract structured data from text
            return LayerFeedbackParser._parse_text_response(response)
    
    @staticmethod
    def _parse_text_response(response: str) -> Dict[str, Any]:
        """Parse feedback from text format if JSON parsing fails"""
        result = {
            "status": "completed",
            "feedback": {
                "scores": {
                    "code_quality": 80,
                    "type_safety": 80,
                    "error_handling": 80,
                    "documentation": 80,
                    "best_practices": 80
                },
                "issues": [],
                "suggestions": [],
                "critical_issues": [],
                "summary": "Code looks good overall"
            },
            "needs_update": False
        }
        
        # Extract scores
        scores_section = re.search(r"scores?:(.*?)(?=\n\n|\Z)", response, re.DOTALL | re.IGNORECASE)
        if scores_section:
            for line in scores_section.group(1).split("\n"):
                if ":" in line:
                    category, score = line.split(":", 1)
                    category = category.strip().lower().replace(" ", "_")
                    try:
                        score = int(score.strip())
                        if 0 <= score <= 100:
                            result["feedback"]["scores"][category] = score
                    except ValueError:
                        continue
        
        # Extract issues
        issues_section = re.search(r"issues?:(.*?)(?=\n\n|\Z)", response, re.DOTALL | re.IGNORECASE)
        if issues_section:
            for line in issues_section.group(1).split("\n"):
                if line.strip():
                    result["feedback"]["issues"].append({
                        "severity": "medium",
                        "category": "code_quality",
                        "description": line.strip(),
                        "suggestion": "Review and address if needed"
                    })
        
        # Extract suggestions
        suggestions_section = re.search(r"suggestions?:(.*?)(?=\n\n|\Z)", response, re.DOTALL | re.IGNORECASE)
        if suggestions_section:
            result["feedback"]["suggestions"] = [
                line.strip() for line in suggestions_section.group(1).split("\n")
                if line.strip()
            ]
        
        # Extract critical issues
        critical_section = re.search(r"critical issues?:(.*?)(?=\n\n|\Z)", response, re.DOTALL | re.IGNORECASE)
        if critical_section:
            result["feedback"]["critical_issues"] = [
                line.strip() for line in critical_section.group(1).split("\n")
                if line.strip()
            ]
            result["needs_update"] = bool(result["feedback"]["critical_issues"])
        
        # Extract summary
        summary_section = re.search(r"summary:(.*?)(?=\n\n|\Z)", response, re.DOTALL | re.IGNORECASE)
        if summary_section:
            result["feedback"]["summary"] = summary_section.group(1).strip()
        
        return result 