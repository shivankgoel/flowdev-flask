from typing import TypeVar, Generic, Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
from src.infra.config import DynamoDBConfig
from src.infra.dynamodb.client import DynamoDBClientFactory
from src.infra.dynamodb.manager import DynamoDBTableManager

logger = logging.getLogger(__name__)

class DynamoDBDAOError(Exception):
    """Base exception for DynamoDBDAO operations."""
    pass

class DynamoDBDAONotFoundError(DynamoDBDAOError):
    """Exception raised when a requested resource is not found."""
    pass

class DynamoDBDAOConnectionError(DynamoDBDAOError):
    """Exception raised when there are connection issues with DynamoDB."""
    pass

T = TypeVar('T')

@dataclass
class BaseDynamoDBDAO(Generic[T]):
    """Base class for all DynamoDB DAOs."""
    
    def __init__(self, table_name: str):
        config = DynamoDBConfig()
        client_factory = DynamoDBClientFactory(config)
        self.manager = DynamoDBTableManager(client_factory)
        self.table = self.manager.resource.Table(table_name)
        self.logger = logging.getLogger(__name__)

    def _serialize(self, obj: T) -> Dict[str, Any]:
        """Serialize a dataclass object to a dictionary."""
        return asdict(obj)

    def _deserialize(self, data: Dict[str, Any], cls: type[T]) -> T:
        """Deserialize a dictionary to a dataclass object."""
        return cls(**data)

    def _get_item(self, key: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Get an item from the table."""
        try:
            response = self.table.get_item(Key=key)
            if 'Item' not in response:
                return None
            return response['Item']
        except Exception as e:
            self.logger.error(f"Error getting item: {str(e)}")
            raise DynamoDBDAOError(f"Failed to get item: {str(e)}")

    def _put_item(self, item: Dict[str, Any]) -> bool:
        """Put an item in the table."""
        try:
            self.table.put_item(Item=item)
            return True
        except Exception as e:
            self.logger.error(f"Error putting item: {str(e)}")
            raise DynamoDBDAOError(f"Failed to put item: {str(e)}")

    def _delete_item(self, key: Dict[str, str]) -> bool:
        """Delete an item from the table."""
        try:
            self.table.delete_item(Key=key)
            return True
        except Exception as e:
            self.logger.error(f"Error deleting item: {str(e)}")
            raise DynamoDBDAOError(f"Failed to delete item: {str(e)}")

    def _query_items(self, key_condition_expression: str, expression_attribute_values: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query items from the table."""
        try:
            response = self.table.query(
                KeyConditionExpression=key_condition_expression,
                ExpressionAttributeValues=expression_attribute_values
            )
            return response.get('Items', [])
        except Exception as e:
            self.logger.error(f"Error querying items: {str(e)}")
            raise DynamoDBDAOError(f"Failed to query items: {str(e)}") 