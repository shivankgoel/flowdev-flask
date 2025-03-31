import json
import os
from typing import Dict, Any
from pathlib import Path

from .canvas_parser import CanvasParser
from specs.flow_canvas_spec import CanvasDefinitionSpec

class SpecFileReader:
    @staticmethod
    def read_spec_file(file_path: str) -> CanvasDefinitionSpec:
        """
        Read a spec file from disk and convert it to a CanvasDefinitionSpec.
        
        Args:
            file_path: Path to the spec file (JSON format)
            
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
    def read_spec_directory(directory_path: str) -> Dict[str, CanvasDefinitionSpec]:
        """
        Read all spec files from a directory and convert them to CanvasDefinitionSpecs.
        
        Args:
            directory_path: Path to the directory containing spec files
            
        Returns:
            Dict[str, CanvasDefinitionSpec]: Dictionary mapping filenames to canvas definitions
            
        Raises:
            FileNotFoundError: If the directory doesn't exist
            json.JSONDecodeError: If any JSON file is invalid
        """
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Directory not found: {directory_path}")
            
        specs = {}
        for file_path in Path(directory_path).glob("*.json"):
            try:
                specs[file_path.stem] = SpecFileReader.read_spec_file(str(file_path))
            except json.JSONDecodeError as e:
                print(f"Warning: Skipping invalid JSON file {file_path}: {str(e)}")
                continue
                
        return specs 