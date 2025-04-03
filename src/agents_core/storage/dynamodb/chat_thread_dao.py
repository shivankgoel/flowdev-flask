from typing import Optional, List, Dict
from datetime import datetime
from src.agents_core.storage.dynamodb.base_dao import BaseDynamoDBDAO
from src.infra.dynamodb.tables import CHAT_THREADS_TABLE

class ChatThreadMetadata:
    """Metadata for a chat thread stored in DynamoDB."""
    def __init__(
        self,
        customer_id: str,
        canvas_id: str,
        node_id: str,
        thread_id: str,
        version: str,
        message_count: int = 0,
        last_message_timestamp: Optional[str] = None,
        created_at: Optional[str] = None,
        last_updated: Optional[str] = None
    ):
        self.customer_id = customer_id
        self.canvas_id = canvas_id
        self.node_id = node_id
        self.thread_id = thread_id
        self.version = version
        self.message_count = message_count
        self.last_message_timestamp = last_message_timestamp or datetime.now().isoformat()
        self.created_at = created_at or datetime.now().isoformat()
        self.last_updated = last_updated or datetime.now().isoformat()

class ChatThreadDAO(BaseDynamoDBDAO):
    """DAO for chat thread metadata operations. The actual messages are stored in S3."""
    
    def __init__(self):
        super().__init__(CHAT_THREADS_TABLE.table_name)

    def get_chat_thread_metadata(
        self, 
        customer_id: str, 
        canvas_id: str,
        node_id: str, 
        thread_id: str, 
        version: str
    ) -> Optional[ChatThreadMetadata]:
        """Get chat thread metadata by ID.
        
        Args:
            customer_id: ID of the customer
            canvas_id: ID of the canvas
            node_id: ID of the node
            thread_id: ID of the thread
            version: Version of the canvas
            
        Returns:
            Optional[ChatThreadMetadata]: The chat thread metadata if found, None otherwise
        """
        item = self._get_item({
            'customer_id_and_canvas_id': f"{customer_id}#{canvas_id}",
            'version_and_node_id_and_thread_id': f"{version}#{node_id}#{thread_id}"
        })
        if not item:
            return None
        return self._deserialize(item['data'], ChatThreadMetadata)

    def put_chat_thread_metadata(self, metadata: ChatThreadMetadata) -> bool:
        """Save chat thread metadata.
        
        Args:
            metadata: The chat thread metadata to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        metadata.last_updated = datetime.now().isoformat()
        return self._put_item({
            'customer_id_and_canvas_id': f"{metadata.customer_id}#{metadata.canvas_id}",
            'version_and_node_id_and_thread_id': f"{metadata.version}#{metadata.node_id}#{metadata.thread_id}",
            'data': self._serialize(metadata),
            'last_updated': metadata.last_updated
        })

    def get_all_chat_threads_metadata(
        self, 
        customer_id: str, 
        canvas_id: str,
        node_id: str, 
        version: str
    ) -> List[ChatThreadMetadata]:
        """Get all chat thread metadata for a node.
        
        Args:
            customer_id: ID of the customer
            canvas_id: ID of the canvas
            node_id: ID of the node
            version: Version of the canvas
            
        Returns:
            List[ChatThreadMetadata]: List of chat thread metadata objects
        """
        items = self._query_items(
            'customer_id_and_canvas_id = :key AND begins_with(version_and_node_id_and_thread_id, :prefix)',
            {
                ':key': f"{customer_id}#{canvas_id}",
                ':prefix': f"{version}#{node_id}#"
            }
        )
        return [self._deserialize(item['data'], ChatThreadMetadata) for item in items]

    def update_message_count(self, metadata: ChatThreadMetadata, increment: int = 1) -> bool:
        """Update the message count for a chat thread.
        
        Args:
            metadata: The chat thread metadata to update
            increment: Amount to increment the message count by (default: 1)
            
        Returns:
            bool: True if successful, False otherwise
        """
        metadata.message_count += increment
        metadata.last_message_timestamp = datetime.now().isoformat()
        return self.put_chat_thread_metadata(metadata)

    def delete_chat_thread_metadata(
        self, 
        customer_id: str, 
        canvas_id: str,
        node_id: str, 
        thread_id: str, 
        version: str
    ) -> bool:
        """Delete chat thread metadata.
        
        Args:
            customer_id: ID of the customer
            canvas_id: ID of the canvas
            node_id: ID of the node
            thread_id: ID of the thread
            version: Version of the canvas
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self._delete_item({
            'customer_id_and_canvas_id': f"{customer_id}#{canvas_id}",
            'version_and_node_id_and_thread_id': f"{version}#{node_id}#{thread_id}"
        }) 