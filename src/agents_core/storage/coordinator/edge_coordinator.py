from typing import Optional, List, Dict, Any
from src.agents_core.storage.dynamodb.edge_dao import EdgeDAO, EdgeMetadata
from src.specs.flow_canvas_spec import CanvasEdgeSpec
from .base_coordinator import BaseCoordinator, StorageCoordinatorError, ImmutableVersionError

class EdgeCoordinator(BaseCoordinator):
    """Coordinates edge operations between DynamoDB and S3."""
    
    def __init__(self):
        self.edge_dao = EdgeDAO()

    def get_edge(self, customer_id: str, canvas_id: str, canvas_version: str, edge_id: str) -> Optional[CanvasEdgeSpec]:
        """Get a complete edge.
        
        Args:
            customer_id: ID of the customer
            canvas_id: ID of the canvas
            canvas_version: Version of the canvas
            edge_id: ID of the edge
            
        Returns:
            Optional[CanvasEdgeSpec]: The complete edge if found, None otherwise
        """
        # Get edge metadata from DynamoDB
        edge_metadata = self.edge_dao.get_edge(customer_id, canvas_id, canvas_version, edge_id)
        if not edge_metadata:
            return None

        # Create and return complete edge spec
        return CanvasEdgeSpec(
            id=edge_metadata.edge_id,
            source=edge_metadata.source,
            target=edge_metadata.target,
            edge_type=edge_metadata.edge_type,
            data=edge_metadata.data
        )

    def get_all_edges(self, customer_id: str, canvas_id: str, canvas_version: str) -> List[CanvasEdgeSpec]:
        """Get all edges for a canvas.
        
        Args:
            customer_id: ID of the customer
            canvas_id: ID of the canvas
            canvas_version: Version of the canvas
            
        Returns:
            List[CanvasEdgeSpec]: List of all edges in the canvas
        """
        edges = []
        for edge_metadata in self.edge_dao.get_all_edges(customer_id, canvas_id, canvas_version):
            edge = CanvasEdgeSpec(
                id=edge_metadata.edge_id,
                source=edge_metadata.source,
                target=edge_metadata.target,
                edge_type=edge_metadata.edge_type,
                data=edge_metadata.data
            )
            edges.append(edge)
        return edges

    def save_edge(self, edge: CanvasEdgeSpec, customer_id: str, canvas_id: str, canvas_version: str) -> bool:
        """Save a complete edge.
        
        Args:
            edge: The complete edge to save
            customer_id: ID of the customer
            canvas_id: ID of the canvas
            canvas_version: Version of the canvas
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ImmutableVersionError: If attempting to modify a non-draft version
        """
        try:
            # Validate version is mutable
            self._validate_version_mutable(canvas_version)

            # Save edge metadata
            edge_metadata = EdgeMetadata(
                customer_id=customer_id,
                canvas_id=canvas_id,
                edge_id=edge.id,
                canvas_version=canvas_version,
                source=edge.source,
                target=edge.target,
                edge_type=edge.edge_type,
                data=edge.data
            )

            return self.edge_dao.put_edge(edge_metadata)

        except ImmutableVersionError as e:
            raise e
        except Exception as e:
            print(f"Error saving edge: {e}")
            return False

    def update_edge_data(self, customer_id: str, canvas_id: str, canvas_version: str, edge_id: str, data: Dict[str, Any]) -> bool:
        """Update an edge's data.
        
        Args:
            customer_id: ID of the customer
            canvas_id: ID of the canvas
            canvas_version: Version of the canvas
            edge_id: ID of the edge
            data: New edge data
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ImmutableVersionError: If attempting to modify a non-draft version
        """
        try:
            # Validate version is mutable
            self._validate_version_mutable(canvas_version)
            return self.edge_dao.update_edge_data(customer_id, canvas_id, canvas_version, edge_id, data)
        except ImmutableVersionError as e:
            raise e
        except Exception as e:
            print(f"Error updating edge data: {e}")
            return False

    def delete_edge(self, customer_id: str, canvas_id: str, canvas_version: str, edge_id: str) -> bool:
        """Delete an edge."""
        try:
            # Validate version is mutable
            self._validate_version_mutable(canvas_version)

            # Delete edge from DynamoDB
            return self.edge_dao.delete_edge(customer_id, canvas_id, canvas_version, edge_id)
        except Exception as e:
            self.logger.error(f"Error deleting edge: {str(e)}")
            raise 