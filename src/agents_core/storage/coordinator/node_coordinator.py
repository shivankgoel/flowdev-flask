from typing import Optional, Dict, Any
from src.agents_core.storage.dynamodb.node_dao import NodeDAO, NodeMetadata
from src.agents_core.storage.s3_dao import S3DAO
from src.specs.flow_canvas_spec import (
    CanvasNodeSpec,
    ProgrammingLanguage
)
from .base_coordinator import BaseCoordinator, StorageCoordinatorError, ImmutableVersionError

class NodeCoordinator(BaseCoordinator):
    """Coordinates node operations between DynamoDB and S3."""
    
    def __init__(self):
        self.node_dao = NodeDAO()
        self.s3_dao = S3DAO()

    def get_node(self, customer_id: str, canvas_id: str, canvas_version: str, node_id: str) -> Optional[CanvasNodeSpec]:
        """Get a complete node with its code.
        
        Args:
            customer_id: ID of the customer
            canvas_id: ID of the canvas
            canvas_version: Version of the canvas
            node_id: ID of the node
            
        Returns:
            Optional[CanvasNodeSpec]: The complete node if found, None otherwise
        """
        # Get node metadata from DynamoDB
        node_metadata = self.node_dao.get_node_metadata(customer_id, canvas_id, canvas_version, node_id)
        if not node_metadata:
            return None

        # Get node code from S3 if available
        application_code = {}
        infra_code = {}
        
        if node_metadata.application_code_s3_uris:
            for lang, uri in node_metadata.application_code_s3_uris.items():
                try:
                    code = self.s3_dao.fetch_code(customer_id, canvas_id, canvas_version, node_id, lang)
                    if code:
                        application_code[ProgrammingLanguage(lang)] = code
                except Exception as e:
                    # Log error but continue with other languages
                    print(f"Error fetching application code for node {node_id}: {e}")

        if node_metadata.infra_code_s3_uris:
            for lang, uri in node_metadata.infra_code_s3_uris.items():
                try:
                    code = self.s3_dao.fetch_code(customer_id, canvas_id, canvas_version, node_id, lang)
                    if code:
                        infra_code[ProgrammingLanguage(lang)] = code
                except Exception as e:
                    # Log error but continue with other languages
                    print(f"Error fetching infra code for node {node_id}: {e}")

        # Create and return complete node spec
        return CanvasNodeSpec(
            id=node_metadata.node_id,
            type=node_metadata.type,
            position=node_metadata.position,
            data=node_metadata.data,
            application_code=application_code,
            infra_code=infra_code,
            metadata=node_metadata.metadata
        )

    def save_node(self, node: CanvasNodeSpec, customer_id: str, canvas_id: str, canvas_version: str) -> bool:
        """Save a complete node, storing metadata in DynamoDB and code in S3.
        
        Args:
            node: The complete node to save
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

            # Save node metadata
            node_metadata = NodeMetadata(
                customer_id=customer_id,
                canvas_id=canvas_id,
                node_id=node.id,
                canvas_version=canvas_version,
                type=node.type,
                position=node.position,
                data=node.data,
                metadata=node.metadata
            )

            # Save application code to S3 if present
            if node.application_code:
                for lang, code in node.application_code.items():
                    s3_uri = self.s3_dao.save_code(
                        code=code,
                        customer_id=customer_id,
                        canvas_id=canvas_id,
                        canvas_version=canvas_version,
                        node_id=node.id,
                        language=lang.value
                    )
                    if not node_metadata.application_code_s3_uris:
                        node_metadata.application_code_s3_uris = {}
                    node_metadata.application_code_s3_uris[lang.value] = s3_uri

            # Save infrastructure code to S3 if present
            if node.infra_code:
                for lang, code in node.infra_code.items():
                    s3_uri = self.s3_dao.save_code(
                        code=code,
                        customer_id=customer_id,
                        canvas_id=canvas_id,
                        canvas_version=canvas_version,
                        node_id=node.id,
                        language=lang.value
                    )
                    if not node_metadata.infra_code_s3_uris:
                        node_metadata.infra_code_s3_uris = {}
                    node_metadata.infra_code_s3_uris[lang.value] = s3_uri

            return self.node_dao.put_node_metadata(node_metadata)

        except ImmutableVersionError as e:
            raise e
        except Exception as e:
            print(f"Error saving node: {e}")
            return False

    def update_node_position(self, customer_id: str, canvas_id: str, canvas_version: str, node_id: str, position: Dict[str, float]) -> bool:
        """Update a node's position.
        
        Args:
            customer_id: ID of the customer
            canvas_id: ID of the canvas
            canvas_version: Version of the canvas
            node_id: ID of the node
            position: New position coordinates
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ImmutableVersionError: If attempting to modify a non-draft version
        """
        try:
            # Validate version is mutable
            self._validate_version_mutable(canvas_version)
            return self.node_dao.update_node_position(customer_id, canvas_id, canvas_version, node_id, position)
        except ImmutableVersionError as e:
            raise e
        except Exception as e:
            print(f"Error updating node position: {e}")
            return False

    def update_node_data(self, customer_id: str, canvas_id: str, canvas_version: str, node_id: str, data: Dict[str, Any]) -> bool:
        """Update a node's data.
        
        Args:
            customer_id: ID of the customer
            canvas_id: ID of the canvas
            canvas_version: Version of the canvas
            node_id: ID of the node
            data: New node data
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ImmutableVersionError: If attempting to modify a non-draft version
        """
        try:
            # Validate version is mutable
            self._validate_version_mutable(canvas_version)
            return self.node_dao.update_node_data(customer_id, canvas_id, canvas_version, node_id, data)
        except ImmutableVersionError as e:
            raise e
        except Exception as e:
            print(f"Error updating node data: {e}")
            return False

    def delete_node(self, customer_id: str, canvas_id: str, canvas_version: str, node_id: str) -> bool:
        """Delete a node and its associated resources."""
        try:
            # Validate version is mutable
            self._validate_version_mutable(canvas_version)

            # Get node metadata to find S3 URIs
            node_metadata = self.node_dao.get_node(customer_id, canvas_id, canvas_version, node_id)
            if not node_metadata:
                return False

            # Delete application code from S3 if present
            if node_metadata.get('application_code_s3_uris'):
                for lang, uri in node_metadata['application_code_s3_uris'].items():
                    try:
                        self.s3_dao.delete_code(customer_id, canvas_id, canvas_version, node_id, lang)
                    except Exception as e:
                        self.logger.error(f"Error deleting application code for node {node_id}: {str(e)}")

            # Delete infrastructure code from S3 if present
            if node_metadata.get('infra_code_s3_uris'):
                for lang, uri in node_metadata['infra_code_s3_uris'].items():
                    try:
                        self.s3_dao.delete_code(customer_id, canvas_id, canvas_version, node_id, lang)
                    except Exception as e:
                        self.logger.error(f"Error deleting infrastructure code for node {node_id}: {str(e)}")

            # Delete node metadata from DynamoDB
            return self.node_dao.delete_node(customer_id, canvas_id, canvas_version, node_id)
        except Exception as e:
            self.logger.error(f"Error deleting node: {str(e)}")
            raise 