"""Layer generator for handling the generation of all layers for an entity"""

import os
from typing import Dict, Any, List
from ..config.layer_types import (
    get_layer_config,
    get_layer_dependencies,
    get_layer_file_path
)
from ..templates.template_manager import TemplateManager

class LayerGenerator:
    """Generator for handling the generation of all layers for an entity"""
    
    def __init__(self):
        self.template_manager = TemplateManager()
    
    def generate_layers(self, entity_name: str, layer_types: List[str] = None) -> Dict[str, str]:
        """Generate all layers for an entity"""
        if layer_types is None:
            layer_types = ["dao", "service", "controller"]
        
        # Generate layers in dependency order
        generated_layers = {}
        for layer_type in layer_types:
            # Generate base class if it doesn't exist
            self._generate_base_class(layer_type)
            
            # Generate specific layer
            code = self._generate_layer(layer_type, entity_name)
            file_path = get_layer_file_path(layer_type, entity_name)
            generated_layers[file_path] = code
        
        return generated_layers
    
    def _generate_base_class(self, layer_type: str):
        """Generate base class for a layer type if it doesn't exist"""
        config = get_layer_config(layer_type)
        base_class = config["base_class"]
        
        # Determine base class file path
        if layer_type == "dao":
            file_path = "app/dao/base.py"
        elif layer_type == "service":
            file_path = "app/services/base.py"
        elif layer_type == "controller":
            file_path = "app/controllers/base.py"
        else:
            raise ValueError(f"Unknown layer type: {layer_type}")
        
        # Generate base class if it doesn't exist
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w") as f:
                f.write(self.template_manager.get_base_class_template(layer_type))
    
    def _generate_layer(self, layer_type: str, entity_name: str) -> str:
        """Generate code for a specific layer"""
        # Get dependencies
        dependencies = get_layer_dependencies(layer_type)
        
        # Generate the layer code
        code = self.template_manager.get_class_template(layer_type, entity_name)
        
        # Add dependency imports
        if dependencies:
            code = self._add_dependency_imports(code, dependencies, entity_name)
        
        return code
    
    def _add_dependency_imports(self, code: str, dependencies: List[str], entity_name: str) -> str:
        """Add imports for dependencies"""
        imports = []
        for dep in dependencies:
            if dep == "dao":
                imports.append(f"from app.dao.{entity_name.lower()}_dao import {entity_name}DynamoDBDAO")
            elif dep == "service":
                imports.append(f"from app.services.{entity_name.lower()}_service import {entity_name}Service")
        
        if imports:
            # Add imports after the existing imports
            lines = code.split("\n")
            import_end = 0
            for i, line in enumerate(lines):
                if not line.startswith("from") and not line.startswith("import"):
                    import_end = i
                    break
            
            # Insert new imports
            lines[import_end:import_end] = [""] + imports
            code = "\n".join(lines)
        
        return code 