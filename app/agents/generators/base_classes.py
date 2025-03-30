"""Base class generators for different layer types"""

from typing import Dict, Any, List
import os
from ..config.layer_types import get_layer_config

class BaseClassGenerator:
    """Base class for generating base classes"""
    
    def __init__(self, layer_type: str):
        self.layer_type = layer_type
        self.config = get_layer_config(layer_type)
    
    def generate_base_class(self) -> str:
        """Generate the base class code"""
        raise NotImplementedError("Subclasses must implement generate_base_class")

class DynamoDBDAOGenerator(BaseClassGenerator):
    """Generator for DynamoDBDAO base class"""
    
    def __init__(self):
        super().__init__("dao")
    
    def generate_base_class(self) -> str:
        """Generate the DynamoDBDAO base class"""
        return f"""from typing import Dict, Any, Optional, List
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

class DynamoDBDAO:
    \"\"\"Base class for DynamoDB DAO implementations\"\"\"
    
    def __init__(self, table_name: str, partition_key: str, sort_key: Optional[str] = None):
        self.table_name = table_name
        self.partition_key = partition_key
        self.sort_key = sort_key
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)
    
    def create_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"Create a new item in DynamoDB\"\"\"
        try:
            response = self.table.put_item(
                Item=item,
                ReturnValues='ALL_OLD'
            )
            logger.info(f"Created item in {self.table_name}")
            return response.get('Attributes', {})
        except ClientError as e:
            logger.error(f"Error creating item: {e}")
            raise
    
    def get_item(self, key: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"Get an item from DynamoDB\"\"\"
        try:
            response = self.table.get_item(Key=key)
            item = response.get('Item')
            if not item:
                logger.warning(f"Item not found in {self.table_name}")
                return {}
            return item
        except ClientError as e:
            logger.error(f"Error getting item: {e}")
            raise
    
    def update_item(self, key: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"Update an item in DynamoDB\"\"\"
        try:
            update_expression = "SET " + ", ".join([f"#{k} = :{k}" for k in updates.keys()])
            expression_attribute_names = {{f"#{k}": k for k in updates.keys()}}
            expression_attribute_values = {{f":{k}": v for k, v in updates.items()}}
            
            response = self.table.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues='ALL_NEW'
            )
            logger.info(f"Updated item in {self.table_name}")
            return response.get('Attributes', {})
        except ClientError as e:
            logger.error(f"Error updating item: {e}")
            raise
    
    def delete_item(self, key: Dict[str, Any]) -> None:
        \"\"\"Delete an item from DynamoDB\"\"\"
        try:
            self.table.delete_item(Key=key)
            logger.info(f"Deleted item from {self.table_name}")
        except ClientError as e:
            logger.error(f"Error deleting item: {e}")
            raise
    
    def query_items(self, query_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        \"\"\"Query items from DynamoDB\"\"\"
        try:
            response = self.table.query(**query_params)
            items = response.get('Items', [])
            logger.info(f"Queried {len(items)} items from {self.table_name}")
            return items
        except ClientError as e:
            logger.error(f"Error querying items: {e}")
            raise"""

class BaseServiceGenerator(BaseClassGenerator):
    """Generator for BaseService class"""
    
    def __init__(self):
        super().__init__("service")
    
    def generate_base_class(self) -> str:
        """Generate the BaseService class"""
        return f"""from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BaseService:
    \"\"\"Base class for service layer implementations\"\"\"
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"Create a new resource\"\"\"
        raise NotImplementedError("Subclasses must implement create")
    
    def get(self, resource_id: str) -> Dict[str, Any]:
        \"\"\"Get a resource by ID\"\"\"
        raise NotImplementedError("Subclasses must implement get")
    
    def update(self, resource_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"Update a resource\"\"\"
        raise NotImplementedError("Subclasses must implement update")
    
    def delete(self, resource_id: str) -> None:
        \"\"\"Delete a resource\"\"\"
        raise NotImplementedError("Subclasses must implement delete")
    
    def list(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        \"\"\"List resources with optional filters\"\"\"
        raise NotImplementedError("Subclasses must implement list")"""

class BaseControllerGenerator(BaseClassGenerator):
    """Generator for BaseController class"""
    
    def __init__(self):
        super().__init__("controller")
    
    def generate_base_class(self) -> str:
        """Generate the BaseController class"""
        return f"""from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

class BaseController:
    \"\"\"Base class for API controllers\"\"\"
    
    def __init__(self):
        self.router = APIRouter()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._setup_routes()
    
    def _setup_routes(self):
        \"\"\"Setup API routes\"\"\"
        raise NotImplementedError("Subclasses must implement _setup_routes")
    
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"Create a new resource\"\"\"
        raise NotImplementedError("Subclasses must implement create")
    
    async def get(self, resource_id: str) -> Dict[str, Any]:
        \"\"\"Get a resource by ID\"\"\"
        raise NotImplementedError("Subclasses must implement get")
    
    async def update(self, resource_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"Update a resource\"\"\"
        raise NotImplementedError("Subclasses must implement update")
    
    async def delete(self, resource_id: str) -> None:
        \"\"\"Delete a resource\"\"\"
        raise NotImplementedError("Subclasses must implement delete")
    
    async def list(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        \"\"\"List resources with optional filters\"\"\"
        raise NotImplementedError("Subclasses must implement list")"""

def generate_base_class(layer_type: str) -> str:
    """Generate base class code for a specific layer type"""
    generators = {
        "dao": DynamoDBDAOGenerator,
        "service": BaseServiceGenerator,
        "controller": BaseControllerGenerator
    }
    
    if layer_type not in generators:
        raise ValueError(f"Unknown layer type: {layer_type}")
    
    generator = generators[layer_type]()
    return generator.generate_base_class() 