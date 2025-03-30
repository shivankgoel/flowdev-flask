"""Template manager for handling different layer types and their templates"""

import os
from typing import Dict, Any, List
from ..config.layer_types import get_layer_config, get_layer_class_name

class TemplateManager:
    """Manages templates for different layer types"""
    
    def __init__(self):
        self.template_dir = os.path.join(os.path.dirname(__file__), "templates")
    
    def get_template_path(self, layer_type: str) -> str:
        """Get the template path for a layer type"""
        config = get_layer_config(layer_type)
        return os.path.join(self.template_dir, config["template_path"])
    
    def get_base_class_template(self, layer_type: str) -> str:
        """Get the base class template for a layer type"""
        from ..generators.base_classes import generate_base_class
        return generate_base_class(layer_type)
    
    def get_class_template(self, layer_type: str, entity_name: str) -> str:
        """Get the class template for a layer type and entity"""
        config = get_layer_config(layer_type)
        class_name = get_layer_class_name(layer_type, entity_name)
        
        template = f"""from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

{config["required_imports"]}

logger = logging.getLogger(__name__)

class {class_name}({config["base_class"]}):
    \"\"\"{entity_name.title()} {layer_type.upper()} implementation\"\"\"
    
    def __init__(self{self._get_init_params(layer_type)}):
        {self._get_init_body(layer_type)}
    
    {self._get_required_methods(config["required_methods"])}"""
        
        return template
    
    def _get_init_params(self, layer_type: str) -> str:
        """Get initialization parameters based on layer type"""
        if layer_type == "dao":
            return ", table_name: str, partition_key: str, sort_key: Optional[str] = None"
        elif layer_type == "service":
            return ", dao: Any"
        elif layer_type == "controller":
            return ", service: Any"
        return ""
    
    def _get_init_body(self, layer_type: str) -> str:
        """Get initialization body based on layer type"""
        if layer_type == "dao":
            return "super().__init__(table_name, partition_key, sort_key)"
        elif layer_type == "service":
            return "super().__init__()\n        self.dao = dao"
        elif layer_type == "controller":
            return "super().__init__()\n        self.service = service"
        return "super().__init__()"
    
    def _get_required_methods(self, methods: List[str]) -> str:
        """Get required method templates"""
        method_templates = []
        for method in methods:
            method_templates.append(self._get_method_template(method))
        return "\n\n    ".join(method_templates)
    
    def _get_method_template(self, method: str) -> str:
        """Get template for a specific method"""
        if method.startswith("create"):
            return f"""def {method}(self, data: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"Create a new {method.split('_')[1] if '_' in method else 'resource'}\"\"\"
        raise NotImplementedError("Subclasses must implement {method}")"""
        elif method.startswith("get"):
            return f"""def {method}(self, resource_id: str) -> Dict[str, Any]:
        \"\"\"Get a {method.split('_')[1] if '_' in method else 'resource'} by ID\"\"\"
        raise NotImplementedError("Subclasses must implement {method}")"""
        elif method.startswith("update"):
            return f"""def {method}(self, resource_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"Update a {method.split('_')[1] if '_' in method else 'resource'}\"\"\"
        raise NotImplementedError("Subclasses must implement {method}")"""
        elif method.startswith("delete"):
            return f"""def {method}(self, resource_id: str) -> None:
        \"\"\"Delete a {method.split('_')[1] if '_' in method else 'resource'}\"\"\"
        raise NotImplementedError("Subclasses must implement {method}")"""
        elif method.startswith("list") or method.startswith("query"):
            return f"""def {method}(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        \"\"\"List {method.split('_')[1] if '_' in method else 'resources'} with optional filters\"\"\"
        raise NotImplementedError("Subclasses must implement {method}")"""
        else:
            return f"""def {method}(self, *args, **kwargs):
        \"\"\"{method.title()} operation\"\"\"
        raise NotImplementedError("Subclasses must implement {method}")""" 