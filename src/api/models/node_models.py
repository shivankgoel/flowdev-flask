from typing import Union, Optional, Dict, Any
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from enum import Enum
from pydantic import Field

# Node Configurations
from .node_configs.s3_node_config import S3BucketNodeConfig
from .node_configs.ddb_node_config import DynamoDbNodeConfig
from .node_configs.auth_service_node_config import AuthServiceNodeConfig
from .node_configs.custom_service_node_config import CustomServiceNodeConfig


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CanvasNodeType(str, Enum):
    """Enum representing different types of canvas nodes."""
    DYNAMO_DB = "DYNAMO_DB"
    S3_BUCKET = "S3_BUCKET"
    AUTH_SERVICE = "AUTH_SERVICE"
    CUSTOM_SERVICE = "CUSTOM_SERVICE"

    def __str__(self) -> str:
        """String representation of the node type."""
        return self.value

    def __json__(self) -> str:
        """JSON serialization of the node type."""
        return self.value


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class NodePosition:
    """Represents the position of a node in the canvas."""
    x: float = Field(..., description="X coordinate of the node")
    y: float = Field(..., description="Y coordinate of the node")

    def __post_init__(self):
        """Validate coordinates after initialization."""
        if not isinstance(self.x, (int, float)) or not isinstance(self.y, (int, float)):
            raise ValueError("Coordinates must be numbers")
        self.x = float(self.x)
        self.y = float(self.y)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CanvasNode:
    """Represents a node in the canvas with its configuration."""
    nodeId: str = Field(..., description="Unique identifier for the node")
    nodeName: str = Field(..., description="Display name of the node")
    nodeType: CanvasNodeType = Field(..., description="Type of the node")
    nodePosition: NodePosition = Field(..., description="Position of the node in the canvas")
    nodeConfig: Optional[Union[
        DynamoDbNodeConfig,
        S3BucketNodeConfig,
        AuthServiceNodeConfig,
        CustomServiceNodeConfig
    ]] = Field(None, description="Configuration specific to the node type")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the node to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the node
        """
        return {
            'nodeId': self.nodeId,
            'nodeName': self.nodeName,
            'nodeType': self.nodeType.value if isinstance(self.nodeType, CanvasNodeType) else self.nodeType,
            'nodePosition': self.nodePosition.to_dict(),
            'nodeConfig': self.nodeConfig.to_dict() if self.nodeConfig else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CanvasNode':
        """Create a node from a dictionary.
        
        Args:
            data: Dictionary containing node data
            
        Returns:
            CanvasNode: New CanvasNode instance
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Validate required fields
        required_fields = ['nodeId', 'nodeName', 'nodeType', 'nodePosition']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        # Convert node type
        node_type = data['nodeType']
        if isinstance(node_type, str):
            try:
                node_type = CanvasNodeType(node_type)
            except ValueError as e:
                raise ValueError(f"Invalid node type: {node_type}") from e

        # Convert node position
        node_position = data['nodePosition']
        if isinstance(node_position, dict):
            node_position = NodePosition.from_dict(node_position)

        # Convert node config based on node type
        node_config = data.get('nodeConfig')
        if node_config:
            try:
                if node_type == CanvasNodeType.DYNAMO_DB:
                    node_config = DynamoDbNodeConfig.from_dict(node_config)
                elif node_type == CanvasNodeType.S3_BUCKET:
                    node_config = S3BucketNodeConfig.from_dict(node_config)
                elif node_type == CanvasNodeType.AUTH_SERVICE:
                    node_config = AuthServiceNodeConfig.from_dict(node_config)
                elif node_type == CanvasNodeType.CUSTOM_SERVICE:
                    node_config = CustomServiceNodeConfig.from_dict(node_config)
            except Exception as e:
                raise ValueError(f"Invalid node configuration for type {node_type}: {str(e)}") from e

        return cls(
            nodeId=data['nodeId'],
            nodeName=data['nodeName'],
            nodeType=node_type,
            nodePosition=node_position,
            nodeConfig=node_config
        )

    def validate(self) -> None:
        """Validate the node configuration.
        
        Raises:
            ValueError: If the node configuration is invalid
        """
        if not self.nodeId:
            raise ValueError("Node ID is required")
        if not self.nodeName:
            raise ValueError("Node name is required")
        if not self.nodeType:
            raise ValueError("Node type is required")
        if not self.nodePosition:
            raise ValueError("Node position is required")
        
        # Validate node config based on node type
        if self.nodeConfig:
            if self.nodeType == CanvasNodeType.DYNAMO_DB and not isinstance(self.nodeConfig, DynamoDbNodeConfig):
                raise ValueError("DynamoDB node requires DynamoDbNodeConfig")
            elif self.nodeType == CanvasNodeType.S3_BUCKET and not isinstance(self.nodeConfig, S3BucketNodeConfig):
                raise ValueError("S3 bucket node requires S3BucketNodeConfig")
            elif self.nodeType == CanvasNodeType.AUTH_SERVICE and not isinstance(self.nodeConfig, AuthServiceNodeConfig):
                raise ValueError("Auth service node requires AuthServiceNodeConfig")
            elif self.nodeType == CanvasNodeType.CUSTOM_SERVICE and not isinstance(self.nodeConfig, CustomServiceNodeConfig):
                raise ValueError("Custom service node requires CustomServiceNodeConfig")
