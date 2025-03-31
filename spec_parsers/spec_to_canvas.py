import json
import os
from typing import Dict, Any, Optional
from datetime import datetime

from .canvas_parser import CanvasParser
from specs.flow_canvas_spec import CanvasDefinitionSpec, ProgrammingLanguage

class SpecToCanvas:
    @staticmethod
    def from_json_file(file_path: str) -> CanvasDefinitionSpec:
        """
        Read a JSON spec file and convert it to a CanvasDefinitionSpec.
        
        Args:
            file_path: Path to the JSON spec file
            
        Returns:
            CanvasDefinitionSpec: The parsed canvas definition
            
        Raises:
            FileNotFoundError: If the spec file doesn't exist
            json.JSONDecodeError: If the JSON is invalid
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Spec file not found: {file_path}")
            
        with open(file_path, 'r') as f:
            spec_data = json.load(f)
            
        return CanvasParser.parse_canvas_definition(spec_data)
    
    @staticmethod
    def from_json_string(json_str: str) -> CanvasDefinitionSpec:
        """
        Convert a JSON string to a CanvasDefinitionSpec.
        
        Args:
            json_str: JSON string containing the spec
            
        Returns:
            CanvasDefinitionSpec: The parsed canvas definition
            
        Raises:
            json.JSONDecodeError: If the JSON is invalid
        """
        spec_data = json.loads(json_str)
        return CanvasParser.parse_canvas_definition(spec_data)
    
    @staticmethod
    def from_dict(spec_dict: Dict[str, Any]) -> CanvasDefinitionSpec:
        """
        Convert a dictionary to a CanvasDefinitionSpec.
        
        Args:
            spec_dict: Dictionary containing the spec
            
        Returns:
            CanvasDefinitionSpec: The parsed canvas definition
        """
        return CanvasParser.parse_canvas_definition(spec_dict)
    
    @staticmethod
    def create_empty_canvas(
        canvas_id: str,
        programming_language: ProgrammingLanguage = ProgrammingLanguage.JAVA,
        version: str = "1.0.0"
    ) -> CanvasDefinitionSpec:
        """
        Create an empty canvas definition with basic metadata.
        
        Args:
            canvas_id: Unique identifier for the canvas
            programming_language: Programming language for the canvas
            version: Version of the canvas
            
        Returns:
            CanvasDefinitionSpec: An empty canvas definition
        """
        now = datetime.utcnow().isoformat() + "Z"
        spec_dict = {
            "canvasId": canvas_id,
            "version": version,
            "programmingLanguage": programming_language.value,
            "createdAt": now,
            "updatedAt": now,
            "nodes": [],
            "edges": []
        }
        return CanvasParser.parse_canvas_definition(spec_dict)
    
    @staticmethod
    def to_json(canvas_def: CanvasDefinitionSpec, indent: int = 2) -> str:
        """
        Convert a CanvasDefinitionSpec to a JSON string.
        
        Args:
            canvas_def: The canvas definition to convert
            indent: Number of spaces for indentation
            
        Returns:
            str: JSON string representation of the canvas definition
        """
        # Convert the canvas definition to a dictionary
        spec_dict = {
            "canvasId": canvas_def.canvas_id,
            "version": canvas_def.version,
            "programmingLanguage": canvas_def.programming_language.value,
            "createdAt": canvas_def.created_at,
            "updatedAt": canvas_def.updated_at,
            "nodes": [
                {
                    "id": node.id,
                    "type": node.type,
                    "position": {
                        "x": node.position.x,
                        "y": node.position.y
                    },
                    "data": {
                        "spec": node.data.spec.__dict__
                    }
                }
                for node in canvas_def.nodes
            ],
            "edges": [
                {
                    "id": edge.id,
                    "source": edge.source,
                    "target": edge.target,
                    "arrowHeadType": edge.arrow_head_type,
                    "data": {
                        "label": edge.data.label
                    }
                }
                for edge in canvas_def.edges
            ]
        }
        return json.dumps(spec_dict, indent=indent)
    
    @staticmethod
    def save_to_file(canvas_def: CanvasDefinitionSpec, file_path: str, indent: int = 2) -> None:
        """
        Save a CanvasDefinitionSpec to a JSON file.
        
        Args:
            canvas_def: The canvas definition to save
            file_path: Path where to save the JSON file
            indent: Number of spaces for indentation
            
        Raises:
            IOError: If there's an error writing to the file
        """
        json_str = SpecToCanvas.to_json(canvas_def, indent)
        with open(file_path, 'w') as f:
            f.write(json_str) 