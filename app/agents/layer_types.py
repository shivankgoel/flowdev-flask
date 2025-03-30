from typing import Dict, List, Optional, Union

class LayerType:
    """Configuration for different layer types"""
    
    def __init__(
        self,
        name: str,
        base_class: str,
        required_methods: List[str],
        required_imports: List[str],
        dependencies: List[str],
        sublayers: Optional[List[Dict]] = None,
        storage_configs: Optional[List[Dict]] = None
    ):
        self.name = name
        self.base_class = base_class
        self.required_methods = required_methods
        self.required_imports = required_imports
        self.dependencies = dependencies
        self.sublayers = sublayers or []
        self.storage_configs = storage_configs or []

# Define storage configurations
STORAGE_CONFIGS = {
    "dynamodb": {
        "name": "DynamoDB",
        "base_class": "BaseDynamoDBDAO",
        "required_imports": ["boto3", "from typing import Dict, List, Optional"],
        "config_fields": [
            "table_name",
            "partition_key",
            "sort_key",
            "indexes",
            "ttl_attribute",
            "stream_config"
        ]
    },
    "s3": {
        "name": "S3",
        "base_class": "BaseS3DAO",
        "required_imports": ["boto3", "from typing import Dict, List, Optional"],
        "config_fields": [
            "bucket_name",
            "prefix",
            "encryption",
            "lifecycle_rules",
            "versioning"
        ]
    }
}

# Define layer types with their sublayers
LAYER_TYPES = {
    "dao": LayerType(
        name="DAO",
        base_class="BaseDAO",
        required_methods=["create_item", "get_item", "update_item", "delete_item", "query_items"],
        required_imports=["boto3", "from typing import Dict, List, Optional"],
        dependencies=["base_classes"],
        storage_configs=["dynamodb", "s3"],
        sublayers=[
            {
                "name": "data_model",
                "description": "Data model and validation",
                "methods": ["validate_item", "transform_item"],
                "imports": ["pydantic", "from typing import Dict, Any"]
            },
            {
                "name": "query_builder",
                "description": "Query construction and optimization",
                "methods": ["build_query", "optimize_query"],
                "imports": ["from typing import Dict, List"]
            },
            {
                "name": "error_handler",
                "description": "Error handling and retries",
                "methods": ["handle_error", "retry_operation"],
                "imports": ["from botocore.exceptions import ClientError"]
            },
            {
                "name": "storage_manager",
                "description": "Storage configuration and management",
                "methods": ["get_storage_config", "validate_storage_config"],
                "imports": ["from typing import Dict, Any"]
            }
        ]
    ),
    "service": LayerType(
        name="Service",
        base_class="BaseService",
        required_methods=["create", "get", "update", "delete", "list"],
        required_imports=["from typing import Dict, List, Optional"],
        dependencies=["dao"],
        sublayers=[
            {
                "name": "validator",
                "description": "Input validation and sanitization",
                "methods": ["validate_input", "sanitize_input"],
                "imports": ["pydantic", "from typing import Dict, Any"]
            },
            {
                "name": "business_logic",
                "description": "Core business rules and workflows",
                "methods": ["apply_business_rules", "execute_workflow"],
                "imports": ["from typing import Dict, List"]
            },
            {
                "name": "event_handler",
                "description": "Event handling and notifications",
                "methods": ["handle_event", "send_notification"],
                "imports": ["from typing import Dict, Any"]
            },
            {
                "name": "storage_orchestrator",
                "description": "Coordinate operations across multiple storage systems",
                "methods": ["coordinate_storage_ops", "handle_storage_failures"],
                "imports": ["from typing import Dict, List"]
            }
        ]
    ),
    "controller": LayerType(
        name="Controller",
        base_class="BaseController",
        required_methods=["create", "get", "update", "delete", "list"],
        required_imports=["fastapi", "from typing import Dict, List, Optional"],
        dependencies=["service"],
        sublayers=[
            {
                "name": "request_handler",
                "description": "Request parsing and validation",
                "methods": ["parse_request", "validate_request"],
                "imports": ["fastapi", "pydantic"]
            },
            {
                "name": "response_formatter",
                "description": "Response formatting and serialization",
                "methods": ["format_response", "serialize_response"],
                "imports": ["from typing import Dict, Any"]
            },
            {
                "name": "middleware",
                "description": "Request/response middleware",
                "methods": ["authenticate", "authorize", "log_request"],
                "imports": ["fastapi", "from typing import Callable"]
            }
        ]
    )
}

def get_layer_type(layer_type: str) -> LayerType:
    """Get layer type configuration"""
    if layer_type not in LAYER_TYPES:
        raise ValueError(f"Unknown layer type: {layer_type}")
    return LAYER_TYPES[layer_type]

def get_sublayer_config(layer_type: str, sublayer_name: str) -> Dict:
    """Get configuration for a specific sublayer"""
    layer = get_layer_type(layer_type)
    for sublayer in layer.sublayers:
        if sublayer["name"] == sublayer_name:
            return sublayer
    raise ValueError(f"Unknown sublayer: {sublayer_name} for layer type: {layer_type}")

def get_storage_config(storage_type: str) -> Dict:
    """Get configuration for a specific storage type"""
    if storage_type not in STORAGE_CONFIGS:
        raise ValueError(f"Unknown storage type: {storage_type}")
    return STORAGE_CONFIGS[storage_type]

class StorageConfig:
    """Configuration for storage systems"""
    
    def __init__(
        self,
        storage_type: str,
        name: str,
        config: Dict[str, Any]
    ):
        self.storage_type = storage_type
        self.name = name
        self.config = config
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate storage configuration"""
        storage_spec = get_storage_config(self.storage_type)
        for field in storage_spec["config_fields"]:
            if field not in self.config:
                raise ValueError(f"Missing required field: {field}")

class EntityStorageManager:
    """Manages multiple storage configurations for an entity"""
    
    def __init__(self):
        self.storage_configs: Dict[str, StorageConfig] = {}
    
    def add_storage(self, config: StorageConfig) -> None:
        """Add a storage configuration"""
        self.storage_configs[config.name] = config
    
    def get_storage(self, name: str) -> StorageConfig:
        """Get storage configuration by name"""
        if name not in self.storage_configs:
            raise ValueError(f"Unknown storage: {name}")
        return self.storage_configs[name]
    
    def list_storages(self) -> List[str]:
        """List all storage names"""
        return list(self.storage_configs.keys()) 