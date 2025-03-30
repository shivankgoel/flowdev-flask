from typing import Dict, Any, List, Optional
import json
import re

class CodeGenerationParser:
    """Parser for code generation responses"""
    
    @staticmethod
    def parse_response(response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the ChatGPT response into a structured format.
        
        Expected format:
        {
            "status": "completed",
            "generated_code": {
                "language": "python",
                "code": "Your generated code here",
                "imports": ["import os", "import json"],
                "dependencies": ["boto3>=1.26.0"],
                "notes": ["Note 1", "Note 2"]
            },
            "metadata": {
                "class_name": "ExampleClass",
                "base_class": "BaseClass",
                "methods": ["method1", "method2"],
                "fields": ["field1", "field2"],
                "complexity": "medium",
                "estimated_lines": 50
            }
        }
        """
        try:
            # Try to parse as JSON first
            if isinstance(response, str):
                response = json.loads(response)
            
            # Validate required fields
            if "status" not in response:
                raise ValueError("Missing required field: status")
            
            if "generated_code" not in response:
                raise ValueError("Missing required field: generated_code")
            
            code_info = response["generated_code"]
            if "language" not in code_info:
                raise ValueError("Missing required field: generated_code.language")
            
            if "code" not in code_info:
                raise ValueError("Missing required field: generated_code.code")
            
            # Clean up the code by removing any markdown code blocks if present
            code = code_info["code"]
            if code.startswith("```") and code.endswith("```"):
                # Remove the first and last lines (```python and ```)
                lines = code.split("\n")
                if len(lines) >= 2:
                    # Remove the first line (```python) and last line (```)
                    code = "\n".join(lines[1:-1])
                else:
                    code = ""
            
            # Update the code in the response
            code_info["code"] = code
            
            return response
            
        except json.JSONDecodeError:
            # If not JSON, try to extract code from text response
            if isinstance(response, str):
                # Extract code from text response
                code = response.strip()
                
                # Create structured response
                return {
                    "status": "completed",
                    "generated_code": {
                        "language": "python",  # Default to Python
                        "code": code,
                        "imports": [],
                        "dependencies": [],
                        "notes": []
                    },
                    "metadata": {
                        "class_name": "GeneratedClass",
                        "base_class": "object",
                        "methods": [],
                        "fields": [],
                        "complexity": "unknown",
                        "estimated_lines": len(code.split("\n"))
                    }
                }
            else:
                raise ValueError("Invalid response format")
    
    @staticmethod
    def _parse_text_response(response: str) -> Dict[str, Any]:
        """Parse response from text format if JSON parsing fails"""
        result = {
            "status": "completed",
            "generated_code": {
                "language": "python",  # Default to python
                "code": "",
                "imports": [],
                "dependencies": [],
                "notes": []
            },
            "metadata": {
                "class_name": "",
                "base_class": "",
                "methods": [],
                "fields": [],
                "complexity": "medium",
                "estimated_lines": 0
            }
        }
        
        # Extract code block
        code_block = re.search(r"```(\w+)?\n(.*?)\n```", response, re.DOTALL)
        if code_block:
            language = code_block.group(1) or "python"
            code = code_block.group(2)
            result["generated_code"].update({
                "language": language,
                "code": code
            })
        
        # Extract imports
        imports_section = re.search(r"imports?:(.*?)(?=\n\n|\Z)", response, re.DOTALL | re.IGNORECASE)
        if imports_section:
            result["generated_code"]["imports"] = [
                imp.strip() for imp in imports_section.group(1).split("\n")
                if imp.strip()
            ]
        
        # Extract dependencies
        deps_section = re.search(r"dependencies?:(.*?)(?=\n\n|\Z)", response, re.DOTALL | re.IGNORECASE)
        if deps_section:
            result["generated_code"]["dependencies"] = [
                dep.strip() for dep in deps_section.group(1).split("\n")
                if dep.strip()
            ]
        
        # Extract notes
        notes_section = re.search(r"notes?:(.*?)(?=\n\n|\Z)", response, re.DOTALL | re.IGNORECASE)
        if notes_section:
            result["generated_code"]["notes"] = [
                note.strip() for note in notes_section.group(1).split("\n")
                if note.strip()
            ]
        
        # Extract metadata
        metadata_section = re.search(r"metadata:(.*?)(?=\n\n|\Z)", response, re.DOTALL | re.IGNORECASE)
        if metadata_section:
            metadata_text = metadata_section.group(1)
            
            # Extract class name
            class_match = re.search(r"class name:\s*(\w+)", metadata_text, re.IGNORECASE)
            if class_match:
                result["metadata"]["class_name"] = class_match.group(1)
            
            # Extract base class
            base_match = re.search(r"base class:\s*(\w+)", metadata_text, re.IGNORECASE)
            if base_match:
                result["metadata"]["base_class"] = base_match.group(1)
            
            # Extract methods
            methods_section = re.search(r"methods?:(.*?)(?=\n\n|\Z)", metadata_text, re.DOTALL | re.IGNORECASE)
            if methods_section:
                result["metadata"]["methods"] = [
                    method.strip() for method in methods_section.group(1).split("\n")
                    if method.strip()
                ]
            
            # Extract fields
            fields_section = re.search(r"fields?:(.*?)(?=\n\n|\Z)", metadata_text, re.DOTALL | re.IGNORECASE)
            if fields_section:
                result["metadata"]["fields"] = [
                    field.strip() for field in fields_section.group(1).split("\n")
                    if field.strip()
                ]
            
            # Extract complexity
            complexity_match = re.search(r"complexity:\s*(low|medium|high)", metadata_text, re.IGNORECASE)
            if complexity_match:
                result["metadata"]["complexity"] = complexity_match.group(1).lower()
            
            # Extract estimated lines
            lines_match = re.search(r"estimated lines:\s*(\d+)", metadata_text, re.IGNORECASE)
            if lines_match:
                result["metadata"]["estimated_lines"] = int(lines_match.group(1))
        
        return result 