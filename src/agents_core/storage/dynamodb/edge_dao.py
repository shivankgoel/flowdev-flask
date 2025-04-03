from typing import Optional, List
from datetime import datetime
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from src.agents_core.storage.dynamodb.base_dao import BaseDynamoDBDAO
from src.infra.dynamodb.tables import EDGES_TABLE
from src.specs.flow_canvas_spec import CanvasEdgeSpec, EdgeDataSpec

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class EdgeMetadata:
    """Edge metadata stored in DynamoDB."""
    customer_id: str
    canvas_id: str
    edge_id: str
    canvas_version: str
    # Edge data stored directly in DynamoDB
    source: str
    target: str
    edge_type: str
    data: Optional[EdgeDataSpec] = None
    # Quick access metadata
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class EdgeDAO(BaseDynamoDBDAO):
    """DAO for edge operations. All edge data is stored directly in DynamoDB."""
    
    def __init__(self):
        super().__init__(EDGES_TABLE.table_name)

    def get_edge(self, customer_id: str, canvas_id: str, edge_id: str, canvas_version: str) -> Optional[EdgeMetadata]:
        """Get an edge by ID.
        
        Args:
            customer_id: ID of the customer
            canvas_id: ID of the canvas
            edge_id: ID of the edge
            canvas_version: Version of the canvas
            
        Returns:
            Optional[EdgeMetadata]: The edge metadata if found, None otherwise
        """
        item = self._get_item({
            'customer_id_and_canvas_id': f"{customer_id}#{canvas_id}",
            'version_and_edge_id': f"{canvas_version}#{edge_id}"
        })
        if not item:
            return None
        return self._deserialize(item['data'], EdgeMetadata)

    def put_edge(self, metadata: EdgeMetadata) -> bool:
        """Save an edge.
        
        Args:
            metadata: The edge metadata to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        metadata.updated_at = datetime.now().isoformat()
        if not metadata.created_at:
            metadata.created_at = metadata.updated_at

        return self._put_item({
            'customer_id_and_canvas_id': f"{metadata.customer_id}#{metadata.canvas_id}",
            'version_and_edge_id': f"{metadata.canvas_version}#{metadata.edge_id}",
            'data': self._serialize(metadata),
            'last_updated': metadata.updated_at
        })

    def get_all_edges(self, customer_id: str, canvas_id: str, canvas_version: str) -> List[EdgeMetadata]:
        """Get all edges for a canvas.
        
        Args:
            customer_id: ID of the customer
            canvas_id: ID of the canvas
            canvas_version: Version of the canvas
            
        Returns:
            List[EdgeMetadata]: List of edge metadata objects
        """
        items = self._query_items(
            'customer_id_and_canvas_id = :key AND begins_with(version_and_edge_id, :version)',
            {
                ':key': f"{customer_id}#{canvas_id}",
                ':version': f"{canvas_version}#"
            }
        )
        return [self._deserialize(item['data'], EdgeMetadata) for item in items]

    def update_edge_data(self, metadata: EdgeMetadata, data: Optional[EdgeDataSpec]) -> bool:
        """Update the edge data.
        
        Args:
            metadata: The edge metadata to update
            data: The new edge data specification
            
        Returns:
            bool: True if successful, False otherwise
        """
        metadata.data = data
        return self.put_edge(metadata) 