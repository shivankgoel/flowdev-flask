from typing import Optional, List, Dict, Any
from src.agents_core.storage.dynamodb.chat_thread_dao import ChatThreadDAO, ChatThreadMetadata
from src.agents_core.storage.s3_dao import S3DAO
from src.specs.flow_canvas_spec import ChatThread, ChatMessage
from .base_coordinator import BaseCoordinator, StorageCoordinatorError, ImmutableVersionError
from datetime import datetime

class ChatThreadCoordinator(BaseCoordinator):
    """Coordinates chat thread operations between DynamoDB and S3."""
    
    def __init__(self):
        self.chat_thread_dao = ChatThreadDAO()
        self.s3_dao = S3DAO()

    def get_chat_thread(
        self, 
        customer_id: str, 
        canvas_id: str, 
        canvas_version: str, 
        node_id: str, 
        thread_id: str
    ) -> Optional[ChatThread]:
        """Get a complete chat thread with all its messages."""
        # Get chat thread metadata from DynamoDB
        thread_metadata = self.chat_thread_dao.get_chat_thread_metadata(
            customer_id, canvas_id, node_id, thread_id, canvas_version
        )
        if not thread_metadata:
            return None

        # Get thread from S3
        try:
            thread = self.s3_dao.get_chat_thread(
                customer_id, canvas_id, canvas_version, node_id, thread_id
            )
            if thread:
                return ChatThread(
                    chat_thread_id=thread_id,
                    messages=thread.messages,
                    created_at=thread.created_at,
                    updated_at=thread.updated_at
                )
        except Exception as e:
            self.logger.error(f"Error fetching chat thread {thread_id}: {str(e)}")
        
        return None

    def get_all_chat_threads(
        self, 
        customer_id: str, 
        canvas_id: str, 
        canvas_version: str, 
        node_id: str
    ) -> List[ChatThread]:
        """Get all chat threads for a node."""
        try:
            return self.s3_dao.get_chat_threads(
                customer_id, canvas_id, canvas_version, node_id
            )
        except Exception as e:
            self.logger.error(f"Error fetching chat threads for node {node_id}: {str(e)}")
            return []

    def save_chat_thread(
        self, 
        thread: ChatThread, 
        customer_id: str, 
        canvas_id: str, 
        canvas_version: str
    ) -> bool:
        """Save a complete chat thread."""
        try:
            # Validate version is mutable
            self._validate_version_mutable(canvas_version)

            # Save thread to S3
            self.s3_dao.save_chat_thread(
                customer_id, canvas_id, canvas_version, node_id, thread
            )

            # Save chat thread metadata
            thread_metadata = ChatThreadMetadata(
                customer_id=customer_id,
                canvas_id=canvas_id,
                node_id=node_id,
                thread_id=thread.chat_thread_id,
                version=canvas_version,
                message_count=len(thread.messages),
                created_at=thread.created_at,
                last_updated=thread.updated_at
            )

            return self.chat_thread_dao.put_chat_thread_metadata(thread_metadata)

        except ImmutableVersionError as e:
            raise e
        except Exception as e:
            self.logger.error(f"Error saving chat thread: {str(e)}")
            return False

    def add_message(
        self, 
        customer_id: str, 
        canvas_id: str, 
        canvas_version: str, 
        node_id: str, 
        thread_id: str, 
        message: ChatMessage
    ) -> bool:
        """Add a message to a chat thread."""
        try:
            # Validate version is mutable
            self._validate_version_mutable(canvas_version)

            # Get existing thread
            thread = self.s3_dao.get_chat_thread(
                customer_id, canvas_id, canvas_version, node_id, thread_id
            )
            if not thread:
                return False

            # Add message to thread
            thread.messages.append(message)
            thread.updated_at = datetime.now().isoformat()

            # Save updated thread
            self.s3_dao.save_chat_thread(
                customer_id, canvas_id, canvas_version, node_id, thread
            )

            # Update metadata
            thread_metadata = self.chat_thread_dao.get_chat_thread_metadata(
                customer_id, canvas_id, node_id, thread_id, canvas_version
            )
            if thread_metadata:
                thread_metadata.message_count += 1
                thread_metadata.last_message_timestamp = datetime.now().isoformat()
                return self.chat_thread_dao.put_chat_thread_metadata(thread_metadata)

            return False

        except ImmutableVersionError as e:
            raise e
        except Exception as e:
            self.logger.error(f"Error adding message to chat thread: {str(e)}")
            return False

    def delete_chat_thread(
        self, 
        customer_id: str, 
        canvas_id: str, 
        canvas_version: str, 
        node_id: str, 
        thread_id: str
    ) -> bool:
        """Delete a chat thread and its messages."""
        try:
            # Validate version is mutable
            self._validate_version_mutable(canvas_version)

            # Delete thread from S3
            self.s3_dao.delete_chat_thread(
                customer_id, canvas_id, canvas_version, node_id, thread_id
            )

            # Delete thread metadata from DynamoDB
            return self.chat_thread_dao.delete_chat_thread_metadata(
                customer_id, canvas_id, node_id, thread_id, canvas_version
            )

        except Exception as e:
            self.logger.error(f"Error deleting chat thread: {str(e)}")
            return False 