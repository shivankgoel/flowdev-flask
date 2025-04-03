from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from boto3.dynamodb.conditions import Key
import logging
from src.agents_core.storage.dynamodb.base_dao import BaseDynamoDBDAO
from src.infra.dynamodb.tables import NODES_TABLE
from src.specs.flow_canvas_spec import (
    CanvasPosition,
    DynamoDBTableSpec,
    S3BucketSpec,
    ApplicationLogicSpec,
    DataModelNodeSpec,
    ApiEndpointSpec,
    ApplicationOrchestratorSpec
)

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class NodeMetadata:
    """Essential node metadata stored in DynamoDB."""
    customer_id: str
    canvas_id: str
    node_id: str
    canvas_version: str
    type: str
    position: CanvasPosition
    # References to data in S3
    application_code_s3_uris: Optional[Dict[str, str]] = None  # language -> s3_uri
    infra_code_s3_uris: Optional[Dict[str, str]] = None  # language -> s3_uri
    # Node-specific data stored directly in DynamoDB
    data: Optional[Union[
        DynamoDBTableSpec,
        S3BucketSpec,
        ApplicationLogicSpec,
        DataModelNodeSpec,
        ApiEndpointSpec,
        ApplicationOrchestratorSpec
    ]] = None
    # Quick access metadata
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None  # Custom metadata key-value pairs

class NodeDAO(BaseDynamoDBDAO):
    """DAO for node metadata operations. Large data (code) is stored in S3, while node-specific data is stored in DynamoDB."""
    
    def __init__(self):
        super().__init__(NODES_TABLE.table_name)
        self.logger = logging.getLogger(__name__)

    def getNodeMetadataFromItem(self, item: dict) -> NodeMetadata:
        """Convert DynamoDB item to NodeMetadata."""
        customer_id, canvas_id = item['customer_id_and_canvas_id'].split('#')
        canvas_version, node_id = item['version_and_node_id'].split('#')
        return NodeMetadata(
            customer_id=customer_id,
            canvas_id=canvas_id,
            node_id=node_id,
            canvas_version=canvas_version,
            type=item['type'],
            position=item['position'],
            application_code_s3_uris=item.get('application_code_s3_uris'),
            infra_code_s3_uris=item.get('infra_code_s3_uris'),
            data=item.get('data'),
            created_at=item.get('created_at'),
            updated_at=item.get('updated_at'),
            metadata=item.get('metadata')
        )

    def get_node_metadata(self, customer_id: str, canvas_id: str, node_id: str, canvas_version: str) -> Optional[NodeMetadata]:
        """Get node metadata by ID."""
        try:
            item = self._get_item({
                'customer_id_and_canvas_id': f"{customer_id}#{canvas_id}",
                'version_and_node_id': f"{canvas_version}#{node_id}"
            })
            if not item:
                return None
            return self.getNodeMetadataFromItem(item)
        except Exception as e:
            self.logger.error(f"Error getting node metadata: {str(e)}")
            raise

    def put_node_metadata(self, metadata: NodeMetadata) -> bool:
        """Save node metadata."""
        try:
            metadata.updated_at = datetime.now().isoformat()
            if not metadata.created_at:
                metadata.created_at = metadata.updated_at

            return self._put_item({
                'customer_id_and_canvas_id': f"{metadata.customer_id}#{metadata.canvas_id}",
                'version_and_node_id': f"{metadata.canvas_version}#{metadata.node_id}",
                'type': metadata.type,
                'position': metadata.position,
                'application_code_s3_uris': metadata.application_code_s3_uris,
                'infra_code_s3_uris': metadata.infra_code_s3_uris,
                'data': metadata.data,
                'created_at': metadata.created_at,
                'updated_at': metadata.updated_at,
                'metadata': metadata.metadata
            })
        except Exception as e:
            self.logger.error(f"Error saving node metadata: {str(e)}")
            return False

    def get_all_nodes_metadata(self, customer_id: str, canvas_id: str, version: str) -> List[NodeMetadata]:
        """Get all node metadata for a canvas.
        
        Args:
            customer_id: ID of the customer
            canvas_id: ID of the canvas
            version: Version of the canvas
            
        Returns:
            List[NodeMetadata]: List of node metadata objects
        """
        items = self._query_items(
            'customer_id_and_canvas_id = :key AND begins_with(version_and_node_id, :version)',
            {
                ':key': f"{customer_id}#{canvas_id}",
                ':version': f"{version}#"
            }
        )
        return [self._deserialize(item['data'], NodeMetadata) for item in items]

    def update_node_code_uri(self, metadata: NodeMetadata, language: str, s3_uri: str, is_infra: bool = False) -> bool:
        """Update the S3 URI for a node's code.
        
        Args:
            metadata: The node metadata to update
            language: Programming language of the code
            s3_uri: S3 URI where the code is stored
            is_infra: Whether this is infrastructure code (True) or application code (False)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if is_infra:
            if not metadata.infra_code_s3_uris:
                metadata.infra_code_s3_uris = {}
            metadata.infra_code_s3_uris[language] = s3_uri
        else:
            if not metadata.application_code_s3_uris:
                metadata.application_code_s3_uris = {}
            metadata.application_code_s3_uris[language] = s3_uri
        
        return self.put_node_metadata(metadata)

    def update_node_data(self, metadata: NodeMetadata, data: Union[
        DynamoDBTableSpec,
        S3BucketSpec,
        ApplicationLogicSpec,
        DataModelNodeSpec,
        ApiEndpointSpec,
        ApplicationOrchestratorSpec
    ]) -> bool:
        """Update the node-specific data.
        
        Args:
            metadata: The node metadata to update
            data: The node-specific data to store
            
        Returns:
            bool: True if successful, False otherwise
        """
        metadata.data = data
        return self.put_node_metadata(metadata)

    def get_node(self, customer_id: str, canvas_id: str, canvas_version: str, node_id: str) -> Optional[NodeMetadata]:
        """Get a node by ID."""
        try:
            item = self._get_item({
                'customer_id_and_canvas_id': f"{customer_id}#{canvas_id}",
                'version_and_node_id': f"{canvas_version}#{node_id}"
            })
            if not item:
                return None
            return self.getNodeMetadataFromItem(item)
        except Exception as e:
            self.logger.error(f"Error getting node: {str(e)}")
            raise

    def get_all_nodes(self, customer_id: str, canvas_id: str, canvas_version: str) -> List[NodeMetadata]:
        """Get all nodes for a canvas version."""
        try:
            response = self.table.query(
                KeyConditionExpression=Key('customer_id_and_canvas_id').eq(f"{customer_id}#{canvas_id}") & 
                Key('version_and_node_id').begins_with(f"{canvas_version}#")
            )
            return [self.getNodeMetadataFromItem(item) for item in response.get('Items', [])]
        except Exception as e:
            self.logger.error(f"Error getting all nodes: {str(e)}")
            raise 