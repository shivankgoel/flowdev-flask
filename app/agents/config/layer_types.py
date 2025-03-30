"""Configuration for different layer types and their requirements"""

from typing import Dict, List, Any

# Base layer configurations
LAYER_CONFIGS = {
    "dao": {
        "base_class": "DynamoDBDAO",
        "required_methods": [
            "create_item",
            "get_item",
            "update_item",
            "delete_item",
            "query_items"
        ],
        "required_imports": [
            "from typing import Dict, Any, Optional, List",
            "from datetime import datetime",
            "import boto3",
            "from botocore.exceptions import ClientError",
            "import logging"
        ],
        "required_dependencies": [
            "boto3>=1.26.0"
        ],
        "template_path": "templates/code_generation/dao.py"
    },
    "service": {
        "base_class": "BaseService",
        "required_methods": [
            "create",
            "get",
            "update",
            "delete",
            "list"
        ],
        "required_imports": [
            "from typing import Dict, Any, Optional, List",
            "from datetime import datetime",
            "import logging"
        ],
        "required_dependencies": [],
        "template_path": "templates/code_generation/service.py"
    },
    "controller": {
        "base_class": "BaseController",
        "required_methods": [
            "create",
            "get",
            "update",
            "delete",
            "list"
        ],
        "required_imports": [
            "from typing import Dict, Any, Optional, List",
            "from datetime import datetime",
            "import logging",
            "from fastapi import APIRouter, HTTPException"
        ],
        "required_dependencies": [
            "fastapi>=0.68.0"
        ],
        "template_path": "templates/code_generation/controller.py"
    }
}

# Layer dependencies configuration
LAYER_DEPENDENCIES = {
    "dao": [],  # DAO layer has no dependencies
    "service": ["dao"],  # Service layer depends on DAO
    "controller": ["service"]  # Controller depends on Service
}

# Layer naming conventions
LAYER_NAMING = {
    "dao": "{entity_name}DynamoDBDAO",
    "service": "{entity_name}Service",
    "controller": "{entity_name}Controller"
}

# Layer file structure
LAYER_FILE_STRUCTURE = {
    "dao": "app/dao/{entity_name.lower()}_dao.py",
    "service": "app/services/{entity_name.lower()}_service.py",
    "controller": "app/controllers/{entity_name.lower()}_controller.py"
}

def get_layer_config(layer_type: str) -> Dict[str, Any]:
    """Get configuration for a specific layer type"""
    if layer_type not in LAYER_CONFIGS:
        raise ValueError(f"Unknown layer type: {layer_type}")
    return LAYER_CONFIGS[layer_type]

def get_layer_dependencies(layer_type: str) -> List[str]:
    """Get dependencies for a specific layer type"""
    if layer_type not in LAYER_DEPENDENCIES:
        raise ValueError(f"Unknown layer type: {layer_type}")
    return LAYER_DEPENDENCIES[layer_type]

def get_layer_class_name(layer_type: str, entity_name: str) -> str:
    """Get class name for a specific layer type and entity"""
    if layer_type not in LAYER_NAMING:
        raise ValueError(f"Unknown layer type: {layer_type}")
    return LAYER_NAMING[layer_type].format(entity_name=entity_name)

def get_layer_file_path(layer_type: str, entity_name: str) -> str:
    """Get file path for a specific layer type and entity"""
    if layer_type not in LAYER_FILE_STRUCTURE:
        raise ValueError(f"Unknown layer type: {layer_type}")
    return LAYER_FILE_STRUCTURE[layer_type].format(entity_name=entity_name.lower()) 