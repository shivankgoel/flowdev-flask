from typing import Optional, List, Dict, Any
from src.agents_core.storage.dynamodb.canvas_dao import CanvasDAO, Canvas
from src.agents_core.storage.dynamodb.node_dao import NodeDAO, NodeMetadata
from src.agents_core.storage.dynamodb.edge_dao import EdgeDAO, EdgeMetadata
from src.agents_core.storage.dynamodb.chat_thread_dao import ChatThreadDAO
from src.agents_core.storage.s3_dao import S3DAO
from src.specs.flow_canvas_spec import (
    CanvasDefinition,
    CanvasNodeSpec,
    CanvasEdgeSpec,
    ProgrammingLanguage
)
from .base_coordinator import BaseCoordinator, StorageCoordinatorError, ImmutableVersionError
from src.agents_core.storage.coordinator.node_coordinator import NodeCoordinator
from src.agents_core.storage.coordinator.edge_coordinator import EdgeCoordinator
from src.agents_core.storage.coordinator.chat_thread_coordinator import ChatThreadCoordinator
import uuid

class CanvasCoordinator(BaseCoordinator):
    """Coordinates canvas operations between DynamoDB and S3."""
    
    def __init__(self):
        super().__init__()
        self.canvas_dao = CanvasDAO()
        self.node_dao = NodeDAO()
        self.edge_dao = EdgeDAO()
        self.chat_thread_dao = ChatThreadDAO()
        self.s3_dao = S3DAO()
        self.node_coordinator = NodeCoordinator()
        self.edge_coordinator = EdgeCoordinator()
        self.chat_thread_coordinator = ChatThreadCoordinator()

    def get_canvas(self, customer_id: str, canvas_id: str, canvas_version: str) -> Optional[Canvas]:
        """Get canvas only.
        
        Args:
            customer_id: ID of the customer
            canvas_id: ID of the canvas
            canvas_version: Version of the canvas
            
        Returns:
            Optional[Canvas]: The canvas if found, None otherwise
        """
        try:
            return self.canvas_dao.get_canvas(customer_id, canvas_id, canvas_version)
        except Exception as e:
            self.logger.error(f"Error getting canvas: {str(e)}")
            raise

    def get_canvas_definition(self, customer_id: str, canvas_id: str, canvas_version: str) -> Optional[CanvasDefinition]:
        """Get a complete canvas with all its nodes and edges.
        
        Args:
            customer_id: ID of the customer
            canvas_id: ID of the canvas
            canvas_version: Version of the canvas
            
        Returns:
            Optional[CanvasDefinition]: The complete canvas if found, None otherwise
        """
        try:
            # Get canvas from DynamoDB
            canvas = self.get_canvas(customer_id, canvas_id, canvas_version)
            if not canvas:
                return None

            # Get all nodes for this canvas
            nodes = []
            node_metadata_list = self.node_dao.get_all_nodes(customer_id, canvas_id, canvas_version)
            for node_metadata in node_metadata_list:
                node = self.node_coordinator.get_node(customer_id, canvas_id, canvas_version, node_metadata.node_id)
                if node:
                    nodes.append(node)

            # Get all edges for this canvas
            edges = []
            edge_metadata_list = self.edge_dao.get_all_edges(customer_id, canvas_id, canvas_version)
            for edge_metadata in edge_metadata_list:
                edge = self.edge_coordinator.get_edge(customer_id, canvas_id, canvas_version, edge_metadata.edge_id)
                if edge:
                    edges.append(edge)

            # Construct complete canvas
            return CanvasDefinition(
                customer_id=customer_id,
                canvas_id=canvas_id,
                canvas_version=canvas_version,
                canvas_name=canvas.canvas_name,
                nodes=nodes,
                edges=edges,
                created_at=canvas.created_at,
                updated_at=canvas.updated_at
            )
        except Exception as e:
            self.logger.error(f"Error getting complete canvas: {str(e)}")
            raise

    def save_canvas(self, canvas: Canvas, immutability_check: bool = True) -> bool:
        """Save canvas only.
        
        Args:
            canvas: The canvas to save
            immutability_check: Whether to check if the version is mutable (draft)
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ImmutableVersionError: If attempting to modify a non-draft version
        """
        try:
            if immutability_check and canvas.canvas_version != "draft":
                raise ImmutableVersionError(f"Cannot modify non-draft version: {canvas.canvas_version}")
                
            # For existing canvases, only allow updating canvas_name and updated_at
            existing_canvas = self.get_canvas(canvas.customer_id, canvas.canvas_id, canvas.canvas_version)
            if existing_canvas:
                # Preserve original created_at
                canvas.created_at = existing_canvas.created_at
                # Only allow updating canvas_name
                if not canvas.canvas_name:
                    canvas.canvas_name = existing_canvas.canvas_name
                    
            return self.canvas_dao.put_canvas(canvas)
        except ImmutableVersionError as e:
            raise e
        except Exception as e:
            self.logger.error(f"Error saving canvas: {str(e)}")
            return False

    def save_canvas_definition(self, canvas: CanvasDefinition) -> bool:
        """Save a complete canvas with all its nodes and edges.
        
        Args:
            canvas: The complete canvas to save
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ImmutableVersionError: If attempting to modify a non-draft version
        """
        try:
            # Save canvas
            canvas_obj = Canvas(
                customer_id=canvas.customer_id,
                canvas_id=canvas.canvas_id,
                canvas_version=canvas.canvas_version,
                canvas_name=canvas.canvas_name,
                created_at=canvas.created_at,
                updated_at=canvas.updated_at
            )
            if not self.save_canvas(canvas_obj):
                return False

            # Save all nodes
            for node in canvas.nodes:
                if not self.node_coordinator.save_node(node, canvas.customer_id, canvas.canvas_id, canvas.canvas_version):
                    return False

            # Save all edges
            for edge in canvas.edges:
                if not self.edge_coordinator.save_edge(edge, canvas.customer_id, canvas.canvas_id, canvas.canvas_version):
                    return False

            return True

        except ImmutableVersionError as e:
            raise e
        except Exception as e:
            self.logger.error(f"Error saving complete canvas: {str(e)}")
            return False

    def delete_canvas(self, customer_id: str, canvas_id: str) -> bool:
        """Delete a canvas and all its related entities (nodes, edges, chat threads)."""
        try:
            # Get all versions of the canvas
            versions = self.canvas_dao.list_canvas_versions(customer_id, canvas_id)
            if not versions:
                return False

            # Delete each version
            for version in versions:
                # Delete canvas
                if not self.canvas_dao.delete_canvas(customer_id, canvas_id, version):
                    return False

            return True
        except Exception as e:
            self.logger.error(f"Error deleting canvas: {str(e)}")
            raise

    def list_canvas_versions(self, customer_id: str, canvas_id: str) -> List[str]:
        """List all versions of a canvas."""
        try:
            return self.canvas_dao.list_canvas_versions(customer_id, canvas_id)
        except Exception as e:
            self.logger.error(f"Error listing canvas versions: {str(e)}")
            raise

    def create_canvas_version(self, customer_id: str, canvas_id: str) -> Optional[str]:
        """Create a new version of a canvas from its draft version."""
        try:
            # Get the draft version
            draft_canvas = self.get_canvas(customer_id, canvas_id, "draft")
            if not draft_canvas:
                return None

            # Generate new version ID
            new_version = str(uuid.uuid4())
            timestamp = self._get_timestamp()

            # Create new version
            canvas = Canvas(
                customer_id=customer_id,
                canvas_id=canvas_id,
                canvas_version=new_version,
                canvas_name=draft_canvas.canvas_name,
                created_at=timestamp,
                updated_at=timestamp
            )

            # Save new version
            if not self.save_canvas(canvas, immutability_check=False):
                return None

            return new_version
        except Exception as e:
            self.logger.error(f"Error creating canvas version: {str(e)}")
            raise

    def create_new_canvas(self, customer_id: str, canvas_id: str, canvas_version: str, nodes: List[CanvasNodeSpec] = None, edges: List[CanvasEdgeSpec] = None) -> bool:
        """Create a new canvas with the given parameters.
        
        Args:
            customer_id: ID of the customer
            canvas_id: ID of the canvas
            canvas_version: Version of the canvas
            nodes: List of nodes to include in the canvas
            edges: List of edges to include in the canvas
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Initialize with empty lists if not provided
            nodes = nodes or []
            edges = edges or []
            
            # Create canvas definition
            canvas = CanvasDefinition(
                customer_id=customer_id,
                canvas_id=canvas_id,
                canvas_version=canvas_version,
                nodes=nodes,
                edges=edges,
                created_at=self._get_timestamp(),
                updated_at=self._get_timestamp()
            )
            
            # Save the canvas
            return self.save_canvas_definition(canvas)
        except Exception as e:
            self.logger.error(f"Error creating new canvas: {str(e)}")
            return False 