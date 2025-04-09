import json
import boto3
import logging
from typing import Dict, Any, Optional, List, Callable, TypeVar, cast
from datetime import datetime
from functools import wraps
from src.config import S3_BUCKET_NAME
from src.specs.flow_canvas_spec import ChatMessage, ChatThread
from botocore.exceptions import ClientError, BotoCoreError
from src.infra.config import S3Config
from src.infra.s3.client import S3ClientFactory
from src.infra.s3.manager import S3BucketManager

logger = logging.getLogger(__name__)

T = TypeVar('T')

class S3DAOError(Exception):
    """Base exception for S3DAO operations."""
    pass

class S3DAONotFoundError(S3DAOError):
    """Exception raised when a requested resource is not found."""
    pass

class S3DAOConnectionError(S3DAOError):
    """Exception raised when there are connection issues with S3."""
    pass

def handle_s3_errors(operation_name: str) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to handle common S3 operation errors."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'NoSuchBucket':
                    logger.error(f"Bucket {args[0].bucket_name} does not exist")
                    raise S3DAOError(f"Bucket {args[0].bucket_name} does not exist")
                elif error_code == 'AccessDenied':
                    logger.error(f"Access denied during {operation_name}")
                    raise S3DAOError(f"Access denied during {operation_name}")
                elif error_code == 'NoSuchKey':
                    logger.warning(f"Resource not found during {operation_name}")
                    raise S3DAONotFoundError(f"Resource not found during {operation_name}")
                else:
                    logger.error(f"Failed to {operation_name}: {str(e)}")
                    raise S3DAOError(f"Failed to {operation_name}: {str(e)}")
            except BotoCoreError as e:
                logger.error(f"Connection error during {operation_name}: {str(e)}")
                raise S3DAOConnectionError(f"Connection error during {operation_name}: {str(e)}")
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON during {operation_name}: {str(e)}")
                raise S3DAOError(f"Invalid JSON during {operation_name}: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error during {operation_name}: {str(e)}")
                raise S3DAOError(f"Unexpected error during {operation_name}: {str(e)}")
        return wrapper
    return decorator

class S3DAO:
    """Data Access Object for S3 operations. Handles code files and chat thread storage."""
    
    def __init__(self):
        config = S3Config()
        client_factory = S3ClientFactory(config)
        self.manager = S3BucketManager(client_factory)
        self.bucket_name = config.bucket_name

    def _get_file_extension(self, language: str) -> str:
        """Get file extension based on programming language."""
        extensions = {
            "python": ".py",
            "typescript": ".ts",
            "javascript": ".js",
            "java": ".java",
            "go": ".go",
            "rust": ".rs",
            "csharp": ".cs",
            "cpp": ".cpp",
            "c": ".c",
            "php": ".php",
            "ruby": ".rb",
            "swift": ".swift",
            "kotlin": ".kt",
            "scala": ".scala",
            "r": ".r",
            "matlab": ".m",
            "perl": ".pl",
            "haskell": ".hs",
            "elixir": ".ex",
            "clojure": ".clj",
            "erlang": ".erl",
            "lua": ".lua",
            "shell": ".sh",
            "sql": ".sql",
            "html": ".html",
            "css": ".css",
            "xml": ".xml",
            "json": ".json",
            "yaml": ".yaml",
            "markdown": ".md",
            "text": ".txt"
        }
        return extensions.get(language.lower(), ".txt")
    
    @handle_s3_errors("saving code")
    def save_code(
        self, 
        code: str, 
        customer_id: str, 
        canvas_id: str, 
        canvas_version: str, 
        node_id: str, 
        language: str
    ) -> str:
        """Save code to S3.
        
        Args:
            code: The code content to save
            customer_id: ID of the customer
            canvas_id: ID of the canvas
            canvas_version: Version of the canvas
            node_id: ID of the node
            language: Programming language of the code
            
        Returns:
            str: Success message
            
        Raises:
            S3DAOError: If there's an error saving the code
            S3DAOConnectionError: If there's a connection issue
        """
        try:
            extension = self._get_file_extension(language)
            code_key = f"{customer_id}/{canvas_id}/{canvas_version}/{node_id}/code{extension}"
            
            metadata = {
                "last_updated": datetime.now().isoformat(),
                "customer_id": customer_id,
                "canvas_id": canvas_id,
                "canvas_version": canvas_version,
                "node_id": node_id,
                "language": language
            }
            
            self.manager.client.put_object(
                Bucket=self.bucket_name,
                Key=code_key,
                Body=code,
                Metadata=metadata
            )
            
            logger.info(f"Successfully saved code for node {node_id}")
            return f"Code saved for node {node_id}"
        except Exception as e:
            logger.error(f"Error saving code: {str(e)}")
            raise S3DAOError(f"Failed to save code: {str(e)}")
    
    @handle_s3_errors("fetching code")
    def fetch_code(
        self, 
        customer_id: str, 
        canvas_id: str, 
        canvas_version: str, 
        node_id: str, 
        language: str
    ) -> Optional[str]:
        """Fetch code from S3.
        
        Args:
            customer_id: ID of the customer
            canvas_id: ID of the canvas
            canvas_version: Version of the canvas
            node_id: ID of the node
            language: Programming language of the code
            
        Returns:
            Optional[str]: The code content if found, None otherwise
            
        Raises:
            S3DAOError: If there's an error fetching the code
            S3DAONotFoundError: If the code file is not found
            S3DAOConnectionError: If there's a connection issue
        """
        try:
            extension = self._get_file_extension(language)
            code_key = f"{customer_id}/{canvas_id}/{canvas_version}/{node_id}/code{extension}"
            
            response = self.manager.client.get_object(
                Bucket=self.bucket_name,
                Key=code_key
            )
            return response['Body'].read().decode('utf-8')
        except self.manager.client.exceptions.NoSuchKey:
            logger.warning(f"Code file not found for node {node_id}")
            raise S3DAONotFoundError(f"Code file not found for node {node_id}")
        except Exception as e:
            logger.error(f"Error fetching code: {str(e)}")
            raise S3DAOError(f"Failed to fetch code: {str(e)}")

    @handle_s3_errors("saving message")
    def save_message(
        self, 
        customer_id: str, 
        canvas_id: str, 
        canvas_version: str, 
        node_id: str,
        message: ChatMessage
    ) -> None:
        """Save a message to a node's message history.
        
        Args:
            customer_id: ID of the customer
            canvas_id: ID of the canvas
            canvas_version: Version of the canvas
            node_id: ID of the node
            message: The message to save
            
        Raises:
            S3DAOError: If there's an error saving the message
            S3DAOConnectionError: If there's a connection issue
        """
        # Get existing message history
        history = self.get_node_message_history(customer_id, canvas_id, canvas_version, node_id)
        
        # Add new message to history
        history.messages.append(message)
        
        # Save updated history
        self._save_node_message_history(customer_id, canvas_id, canvas_version, node_id, history)
        
        logger.info(f"Successfully saved message for node {node_id}")
    
    @handle_s3_errors("fetching message history")
    def get_node_message_history(
        self,
        customer_id: str,
        canvas_id: str,
        canvas_version: str,
        node_id: str
    ) -> ChatThread:
        """Get a node's message history.
        
        Args:
            customer_id: ID of the customer
            canvas_id: ID of the canvas
            canvas_version: Version of the canvas
            node_id: ID of the node
            
        Returns:
            ChatHistory: The message history for the node
            
        Raises:
            S3DAOError: If there's an error fetching the history
            S3DAONotFoundError: If the history is not found
            S3DAOConnectionError: If there's a connection issue
        """
        history_key = f"{customer_id}/{canvas_id}/{canvas_version}/{node_id}/message_history.json"
        
        try:
            response = self.manager.client.get_object(
                Bucket=self.bucket_name,
                Key=history_key
            )
            history_data = json.loads(response['Body'].read().decode('utf-8'))
            return ChatThread.from_json(json.dumps(history_data))
        except S3DAONotFoundError:
            logger.info(f"No message history found for node {node_id}, returning empty history")
            return ChatThread(node_id=node_id, messages=[])
    
    @handle_s3_errors("saving message history")
    def _save_node_message_history(
        self,
        customer_id: str,
        canvas_id: str,
        canvas_version: str,
        node_id: str,
        history: ChatThread
    ) -> None:
        """Save a node's message history.
        
        Args:
            customer_id: ID of the customer
            canvas_id: ID of the canvas
            canvas_version: Version of the canvas
            node_id: ID of the node
            history: The message history to save
            
        Raises:
            S3DAOError: If there's an error saving the history
            S3DAOConnectionError: If there's a connection issue
        """
        history_key = f"{customer_id}/{canvas_id}/{canvas_version}/{node_id}/message_history.json"
        
        # Use automatic serialization from dataclasses-json
        self.manager.client.put_object(
            Bucket=self.bucket_name,
            Key=history_key,
            Body=history.to_json()
        )

    @handle_s3_errors("saving chat threads")
    def save_chat_threads(
        self,
        customer_id: str,
        canvas_id: str,
        canvas_version: str,
        node_id: str,
        chat_threads: List[ChatThread]
    ) -> None:
        """Save a list of chat threads for a node.
        
        Args:
            customer_id: ID of the customer
            canvas_id: ID of the canvas
            canvas_version: Version of the canvas
            node_id: ID of the node
            chat_threads: List of chat threads to save
            
        Raises:
            S3DAOError: If there's an error saving the chat threads
            S3DAOConnectionError: If there's a connection issue
        """
        threads_key = f"{customer_id}/{canvas_id}/{canvas_version}/{node_id}/chat_threads.json"
        
        # Convert list of chat threads to JSON
        threads_data = [thread.to_dict() for thread in chat_threads]
        
        self.manager.client.put_object(
            Bucket=self.bucket_name,
            Key=threads_key,
            Body=json.dumps(threads_data)
        )
        
        logger.info(f"Successfully saved {len(chat_threads)} chat threads for node {node_id}")

    @handle_s3_errors("fetching chat threads")
    def get_chat_threads(
        self,
        customer_id: str,
        canvas_id: str,
        canvas_version: str,
        node_id: str
    ) -> List[ChatThread]:
        """Get all chat threads for a node.
        
        Args:
            customer_id: ID of the customer
            canvas_id: ID of the canvas
            canvas_version: Version of the canvas
            node_id: ID of the node
            
        Returns:
            List[ChatThread]: List of chat threads for the node
            
        Raises:
            S3DAOError: If there's an error fetching the chat threads
            S3DAONotFoundError: If no chat threads are found
            S3DAOConnectionError: If there's a connection issue
        """
        threads_key = f"{customer_id}/{canvas_id}/{canvas_version}/{node_id}/chat_threads.json"
        
        try:
            response = self.manager.client.get_object(
                Bucket=self.bucket_name,
                Key=threads_key
            )
            threads_data = json.loads(response['Body'].read().decode('utf-8'))
            return [ChatThread.from_dict(thread_data) for thread_data in threads_data]
        except S3DAONotFoundError:
            logger.info(f"No chat threads found for node {node_id}, returning empty list")
            return []
        except Exception as e:
            logger.error(f"Error fetching chat threads: {str(e)}")
            raise S3DAOError(f"Failed to fetch chat threads: {str(e)}")

    @handle_s3_errors("saving chat thread")
    def save_chat_thread(
        self,
        customer_id: str,
        canvas_id: str,
        canvas_version: str,
        node_id: str,
        thread: ChatThread
    ) -> None:
        """Save a single chat thread for a node.
        
        Args:
            customer_id: ID of the customer
            canvas_id: ID of the canvas
            canvas_version: Version of the canvas
            node_id: ID of the node
            thread: The chat thread to save
            
        Raises:
            S3DAOError: If there's an error saving the chat thread
            S3DAOConnectionError: If there's a connection issue
        """
        # Get existing threads
        threads = self.get_chat_threads(customer_id, canvas_id, canvas_version, node_id)
        
        # Update or add the thread
        updated = False
        for i, existing_thread in enumerate(threads):
            if existing_thread.chat_thread_id == thread.chat_thread_id:
                threads[i] = thread
                updated = True
                break
        
        if not updated:
            threads.append(thread)
        
        # Save updated threads
        self.save_chat_threads(customer_id, canvas_id, canvas_version, node_id, threads)
        
        logger.info(f"Successfully saved chat thread {thread.chat_thread_id} for node {node_id}")

    @handle_s3_errors("fetching chat thread")
    def get_chat_thread(
        self,
        customer_id: str,
        canvas_id: str,
        canvas_version: str,
        node_id: str,
        thread_id: str
    ) -> Optional[ChatThread]:
        """Get a specific chat thread for a node.
        
        Args:
            customer_id: ID of the customer
            canvas_id: ID of the canvas
            canvas_version: Version of the canvas
            node_id: ID of the node
            thread_id: ID of the chat thread to fetch
            
        Returns:
            Optional[ChatThread]: The chat thread if found, None otherwise
            
        Raises:
            S3DAOError: If there's an error fetching the chat thread
            S3DAOConnectionError: If there's a connection issue
        """
        threads = self.get_chat_threads(customer_id, canvas_id, canvas_version, node_id)
        for thread in threads:
            if thread.chat_thread_id == thread_id:
                return thread
        return None

    @handle_s3_errors("getting object")
    def get_object(self, s3_uri: str) -> str:
        """Get an object from S3.
        
        Args:
            s3_uri: The S3 URI of the object to get
            
        Returns:
            str: The object content as a string
            
        Raises:
            S3DAOError: If there's an error getting the object
            S3DAONotFoundError: If the object is not found
            S3DAOConnectionError: If there's a connection issue
        """
        try:
            # Extract bucket and key from S3 URI
            if not s3_uri.startswith('s3://'):
                raise S3DAOError(f"Invalid S3 URI: {s3_uri}")
            
            parts = s3_uri[5:].split('/', 1)
            if len(parts) != 2:
                raise S3DAOError(f"Invalid S3 URI: {s3_uri}")
            
            bucket, key = parts
            
            response = self.manager.client.get_object(
                Bucket=bucket,
                Key=key
            )
            actual_content = response['Body'].read().decode('utf-8')
            return actual_content
        except Exception as e:
            logger.error(f"Error getting object from S3: {str(e)}")
            raise S3DAOError(f"Failed to get object from S3: {str(e)}")

    @handle_s3_errors("putting object")
    def put_object(self, s3_uri: str, content: str) -> bool:
        """Put an object in S3.
        
        Args:
            s3_uri: The S3 URI where to put the object
            content: The content to put in S3
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            S3DAOError: If there's an error putting the object
            S3DAOConnectionError: If there's a connection issue
        """
        try:
            # Extract bucket and key from S3 URI
            if not s3_uri.startswith('s3://'):
                raise S3DAOError(f"Invalid S3 URI: {s3_uri}")
            
            parts = s3_uri[5:].split('/', 1)
            if len(parts) != 2:
                raise S3DAOError(f"Invalid S3 URI: {s3_uri}")
            
            bucket, key = parts
            
            self.manager.client.put_object(
                Bucket=bucket,
                Key=key,
                Body=content
            )
            return True
        except Exception as e:
            logger.error(f"Error putting object to S3: {str(e)}")
            raise S3DAOError(f"Failed to put object to S3: {str(e)}")

    @handle_s3_errors("deleting object")
    def delete_object(self, s3_uri: str) -> bool:
        """Delete an object from S3.
        
        Args:
            s3_uri: The S3 URI of the object to delete
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            S3DAOError: If there's an error deleting the object
            S3DAOConnectionError: If there's a connection issue
        """
        try:
            # Extract bucket and key from S3 URI
            if not s3_uri.startswith('s3://'):
                raise S3DAOError(f"Invalid S3 URI: {s3_uri}")
            
            parts = s3_uri[5:].split('/', 1)
            if len(parts) != 2:
                raise S3DAOError(f"Invalid S3 URI: {s3_uri}")
            
            bucket, key = parts
            
            self.manager.client.delete_object(
                Bucket=bucket,
                Key=key
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting object from S3: {str(e)}")
            raise S3DAOError(f"Failed to delete object from S3: {str(e)}") 