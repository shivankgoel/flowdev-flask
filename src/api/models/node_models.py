from typing import Union, Optional
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from enum import Enum

# Node Configurations
from .node_configs.dynamodb_node_config import DynamoDbNodeConfig
from .node_configs.s3_node_config import S3BucketNodeConfig
from .node_configs.application_logic_node_config import ApplicationLogicNodeConfig
from .node_configs.data_model_node_config import DataModelNodeConfig
from .node_configs.api_endpoint_node_config import ApiEndpointNodeConfig
from .node_configs.application_orchestrator_node_config import ApplicationOrchestratorNodeConfig


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CanvasNodeType(str, Enum):
    DYNAMO_DB = "DynamoDB"
    S3_BUCKET = "S3Bucket"
    APPLICATION_LOGIC = "ApplicationLogic"
    DATA_MODEL = "DataModel"
    API_ENDPOINT = "ApiEndpoint"
    APPLICATION_ORCHESTRATOR = "ApplicationOrchestrator"

    def __str__(self):
        return self.value

    def __json__(self):
        return self.value


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CanvasNode:
    nodeId: str
    nodeType: CanvasNodeType
    nodeConfig: Optional[Union[
        DynamoDbNodeConfig,
        S3BucketNodeConfig,
        ApplicationLogicNodeConfig,
        DataModelNodeConfig,
        ApiEndpointNodeConfig,
        ApplicationOrchestratorNodeConfig
    ]] = None

    def to_dict(self) -> dict:
        """Convert the node to a dictionary."""
        return {
            'nodeId': self.nodeId,
            'nodeType': self.nodeType.value if isinstance(self.nodeType, CanvasNodeType) else self.nodeType,
            'nodeConfig': self.nodeConfig.to_dict() if self.nodeConfig else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'CanvasNode':
        """Create a node from a dictionary."""
        node_type = data.get('nodeType')
        if isinstance(node_type, str):
            node_type = CanvasNodeType(node_type)
        
        node_config = data.get('nodeConfig')
        if node_config:
            # Determine the appropriate node config type based on nodeType
            if node_type == CanvasNodeType.DYNAMO_DB:
                node_config = DynamoDbNodeConfig.from_dict(node_config)
            elif node_type == CanvasNodeType.S3_BUCKET:
                node_config = S3BucketNodeConfig.from_dict(node_config)
            # Add other node types as needed
        
        return cls(
            nodeId=data['nodeId'],
            nodeType=node_type,
            nodeConfig=node_config
        )
