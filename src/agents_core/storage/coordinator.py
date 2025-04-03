from typing import Optional, List, Dict
from datetime import datetime
from src.agents_core.storage.dynamodb.canvas_dao import CanvasDAO, Canvas
from src.agents_core.storage.dynamodb.node_dao import NodeDAO, NodeMetadata
from src.agents_core.storage.dynamodb.edge_dao import EdgeDAO, EdgeMetadata
from src.agents_core.storage.dynamodb.chat_thread_dao import ChatThreadDAO, ChatThreadMetadata
from src.agents_core.storage.s3_dao import S3DAO
from src.specs.flow_canvas_spec import (
    CanvasDefinition,
    CanvasNodeSpec,
    CanvasEdgeSpec,
    ChatThread,
    ChatMessage,
    ProgrammingLanguage
)

class StorageCoordinatorError(Exception):
    """Base exception for StorageCoordinator operations."""
    pass

class ImmutableVersionError(StorageCoordinatorError):
    """Exception raised when attempting to modify a non-draft version."""
    def __init__(self, version: str):
        self.version = version
        super().__init__(f"Cannot modify non-draft version: {version}")

class StorageCoordinator:
    """Coordinates storage operations between DynamoDB and S3 to provide complete objects."""
    
    def __init__(self):
        self.canvas_dao = CanvasDAO()
        self.node_dao = NodeDAO()
        self.edge_dao = EdgeDAO()
        self.chat_thread_dao = ChatThreadDAO()
        self.s3_dao = S3DAO()

    def _validate_version_mutable(self, version: str) -> None:
        """Validate that the version can be modified.
        
        Args:
            version: The version to validate
            
        Raises:
            ImmutableVersionError: If the version is not mutable
        """
        if version != "draft":
            raise ImmutableVersionError(version)

    def get_canvas(self, customer_id: str, canvas_id: str, canvas_version: str) -> Optional[CanvasDefinition]:
        """Get a complete canvas with all its nodes, edges, and chat threads.
        
        Args:
            customer_id: ID of the customer
            canvas_id: ID of the canvas
            canvas_version: Version of the canvas
            
        Returns:
            Optional[CanvasDefinitionSpec]: The complete canvas if found, None otherwise
        """
        # Get canvas metadata from DynamoDB
        canvas_metadata = self.canvas_dao.get_canvas(customer_id, canvas_id, canvas_version)
        if not canvas_metadata:
            return None

        # Get all nodes for the canvas
        nodes = []
        for node_metadata in self.node_dao.get_all_nodes_metadata(customer_id, canvas_id, canvas_version):
            # Get node code from S3 if available
            application_code = {}
            infra_code = {}
            
            if node_metadata.application_code_s3_uris:
                for lang, uri in node_metadata.application_code_s3_uris.items():
                    try:
                        code = self.s3_dao.fetch_code(customer_id, canvas_id, canvas_version, node_metadata.node_id, lang)
                        if code:
                            application_code[ProgrammingLanguage(lang)] = code
                    except Exception as e:
                        # Log error but continue with other languages
                        print(f"Error fetching application code for node {node_metadata.node_id}: {e}")

            if node_metadata.infra_code_s3_uris:
                for lang, uri in node_metadata.infra_code_s3_uris.items():
                    try:
                        code = self.s3_dao.fetch_code(customer_id, canvas_id, canvas_version, node_metadata.node_id, lang)
                        if code:
                            infra_code[ProgrammingLanguage(lang)] = code
                    except Exception as e:
                        # Log error but continue with other languages
                        print(f"Error fetching infra code for node {node_metadata.node_id}: {e}")

            # Create complete node spec
            node = CanvasNodeSpec(
                id=node_metadata.node_id,
                type=node_metadata.type,
                position=node_metadata.position,
                data=node_metadata.data,
                application_code=application_code,
                infra_code=infra_code,
                metadata=node_metadata.metadata
            )
            nodes.append(node)

        # Get all edges for the canvas
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

        # Create and return complete canvas spec
        return CanvasDefinition(
            customer_id=customer_id,
            canvas_id=canvas_id,
            canvas_version=canvas_version,
            nodes=nodes,
            edges=edges,
            created_at=canvas_metadata.created_at,
            updated_at=canvas_metadata.updated_at
        )

    def save_canvas(self, canvas: CanvasDefinition) -> bool:
        """Save a complete canvas, storing metadata in DynamoDB and large data in S3.
        
        Args:
            canvas: The complete canvas to save
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ImmutableVersionError: If attempting to modify a non-draft version
        """
        try:
            # Validate version is mutable
            self._validate_version_mutable(canvas.canvas_version)

            # Save canvas metadata
            canvas_metadata = Canvas(
                customer_id=canvas.customer_id,
                canvas_id=canvas.canvas_id,
                canvas_version=canvas.canvas_version,
                nodes=canvas.nodes,
                edges=canvas.edges,
                created_at=canvas.created_at,
                updated_at=canvas.updated_at
            )
            if not self.canvas_dao.put_canvas(canvas_metadata):
                return False

            # Save each node
            for node in canvas.nodes:
                # Save node metadata
                node_metadata = NodeMetadata(
                    customer_id=canvas.customer_id,
                    canvas_id=canvas.canvas_id,
                    node_id=node.id,
                    canvas_version=canvas.canvas_version,
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
                            customer_id=canvas.customer_id,
                            canvas_id=canvas.canvas_id,
                            canvas_version=canvas.canvas_version,
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
                            customer_id=canvas.customer_id,
                            canvas_id=canvas.canvas_id,
                            canvas_version=canvas.canvas_version,
                            node_id=node.id,
                            language=lang.value
                        )
                        if not node_metadata.infra_code_s3_uris:
                            node_metadata.infra_code_s3_uris = {}
                        node_metadata.infra_code_s3_uris[lang.value] = s3_uri

                if not self.node_dao.put_node_metadata(node_metadata):
                    return False

            # Save each edge
            for edge in canvas.edges:
                edge_metadata = EdgeMetadata(
                    customer_id=canvas.customer_id,
                    canvas_id=canvas.canvas_id,
                    edge_id=edge.id,
                    canvas_version=canvas.canvas_version,
                    source=edge.source,
                    target=edge.target,
                    edge_type=edge.edge_type,
                    data=edge.data
                )
                if not self.edge_dao.put_edge(edge_metadata):
                    return False

            return True

        except ImmutableVersionError as e:
            raise e
        except Exception as e:
            print(f"Error saving canvas: {e}")
            return False

    def get_node_chat_threads(self, customer_id: str, canvas_id: str, canvas_version: str, node_id: str) -> List[ChatThread]:
        """Get all chat threads for a node, combining metadata from DynamoDB and messages from S3.
        
        Args:
            customer_id: ID of the customer
            canvas_id: ID of the canvas
            canvas_version: Version of the canvas
            node_id: ID of the node
            
        Returns:
            List[ChatThread]: List of chat threads for the node
        """
        threads = []
        for thread_metadata in self.chat_thread_dao.get_all_chat_threads_metadata(customer_id, node_id, canvas_version):
            # Get messages from S3
            try:
                history = self.s3_dao.get_node_message_history(
                    customer_id=customer_id,
                    canvas_id=canvas_id,
                    canvas_version=canvas_version,
                    node_id=node_id
                )
                
                thread = ChatThread(
                    chat_thread_id=thread_metadata.thread_id,
                    created_at=thread_metadata.created_at,
                    updated_at=thread_metadata.last_message_timestamp,
                    messages=history.messages
                )
                threads.append(thread)
            except Exception as e:
                print(f"Error fetching messages for thread {thread_metadata.thread_id}: {e}")
                continue

        return threads

    def save_chat_thread(self, customer_id: str, canvas_id: str, canvas_version: str, node_id: str, thread: ChatThread) -> bool:
        """Save a chat thread, storing metadata in DynamoDB and messages in S3.
        
        Args:
            customer_id: ID of the customer
            canvas_id: ID of the canvas
            canvas_version: Version of the canvas
            node_id: ID of the node
            thread: The chat thread to save
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ImmutableVersionError: If attempting to modify a non-draft version
        """
        try:
            # Validate version is mutable
            self._validate_version_mutable(canvas_version)

            # Save thread metadata to DynamoDB
            thread_metadata = ChatThreadMetadata(
                customer_id=customer_id,
                node_id=node_id,
                thread_id=thread.chat_thread_id,
                version=canvas_version,
                s3_uri=f"{customer_id}/{canvas_id}/{canvas_version}/{node_id}/message_history.json",
                message_count=len(thread.messages),
                last_message_timestamp=thread.updated_at,
                created_at=thread.created_at
            )
            if not self.chat_thread_dao.put_chat_thread_metadata(thread_metadata):
                return False

            # Save messages to S3
            for message in thread.messages:
                self.s3_dao.save_message(
                    customer_id=customer_id,
                    canvas_id=canvas_id,
                    canvas_version=canvas_version,
                    node_id=node_id,
                    message=message
                )

            return True

        except ImmutableVersionError as e:
            raise e
        except Exception as e:
            print(f"Error saving chat thread: {e}")
            return False 