from typing import Optional, List, Dict
from datetime import datetime
from boto3.dynamodb.conditions import Key
import logging
from src.storage.models.models import CanvasDO
from src.storage.dynamodb.base_dao import BaseDynamoDBDAO
from src.infra.dynamodb.tables import CANVAS_TABLE

"""
CANVAS_TABLE = TableDefinition(
    table_name="flow_canvas",
    partition_key="customer_id",
    sort_key="canvas_id_and_version",  # Format: canvas_id#version
    attributes=[
        {"AttributeName": "customer_id", "AttributeType": "S"},
        {"AttributeName": "canvas_id_and_version", "AttributeType": "S"}
    ],
    gsis=[]  # No GSIs needed as main index supports all required patterns
)
"""

class CanvasDAO(BaseDynamoDBDAO[CanvasDO]):
    """DAO for canvas operations. All canvas data is stored directly in DynamoDB."""
    
    def __init__(self):
        super().__init__(CANVAS_TABLE.table_name)
        self.logger = logging.getLogger(__name__)

    def get_canvas_from_item(self, item: dict) -> CanvasDO:
        """Convert a DynamoDB item to a Canvas object."""
        extracted_canvas_id = item['canvas_id_and_version'].split('#')[0]
        extracted_canvas_version = item['canvas_id_and_version'].split('#')[1]
        return CanvasDO(
            canvas_name=item['canvas_name'],
            customer_id=item['customer_id'],
            canvas_id=extracted_canvas_id,
            canvas_version=extracted_canvas_version,
            created_at=item['created_at'],
            updated_at=item['updated_at']
        )

    def get_canvas(self, customer_id: str, canvas_id: str, canvas_version: str) -> Optional[CanvasDO]:
        """Get a canvas by ID and version."""
        try:
            item = self._get_item({
                'customer_id': customer_id,
                'canvas_id_and_version': f"{canvas_id}#{canvas_version}"
            })
            if not item:
                return None
            return self.get_canvas_from_item(item)
        except Exception as e:
            self.logger.error(f"Error getting canvas: {str(e)}")
            raise

    def save_canvas(self, canvas: CanvasDO) -> bool:
        """Save a canvas."""
        try:
            canvas.updated_at = datetime.now().isoformat()
            if not canvas.created_at:
                canvas.created_at = canvas.updated_at

            return self._put_item({
                'customer_id': canvas.customer_id,
                'canvas_id_and_version': f"{canvas.canvas_id}#{canvas.canvas_version}",
                'canvas_name': canvas.canvas_name,
                'created_at': canvas.created_at,
                'updated_at': canvas.updated_at,
            })
        except Exception as e:
            self.logger.error(f"Error saving canvas: {str(e)}")
            return False

    def get_all_canvases(self, customer_id: str) -> List[CanvasDO]:
        """Get all canvases for a customer."""
        try:
            items = self._query_items(
                'customer_id = :cid',
                {':cid': customer_id}
            )
            return [self.get_canvas_from_item(item) for item in items]
        except Exception as e:
            self.logger.error(f"Error getting all canvases: {str(e)}")
            raise

    def get_unique_canvases(self, customer_id: str) -> List[CanvasDO]:
        try:
            items = self._query_items(
                'customer_id = :cid',
                {':cid': customer_id}
            )
            # Group by canvas_id and take the latest version
            canvas_map: Dict[str, CanvasDO] = {}
            for item in items:
                canvas = self.get_canvas_from_item(item)
                existing = canvas_map.get(canvas.canvas_id)
                if not existing or canvas.canvas_version == "draft" or (
                    canvas.canvas_version != "draft" and 
                    existing.canvas_version == "draft"
                ):
                    canvas_map[canvas.canvas_id] = canvas
            return list(canvas_map.values())
        except Exception as e:
            self.logger.error(f"Error getting unique canvases: {str(e)}")
            raise

    def delete_canvas(self, customer_id: str, canvas_id: str, canvas_version: str) -> bool:
        """Delete a canvas."""
        try:
            return self._delete_item({
                'customer_id': customer_id,
                'canvas_id_and_version': f"{canvas_id}#{canvas_version}"
            })
        except Exception as e:
            self.logger.error(f"Error deleting canvas: {str(e)}")
            return False

    def list_canvas_versions(self, customer_id: str, canvas_id: str) -> List[str]:
        """List all versions of a canvas."""
        try:
            response = self.table.query(
                KeyConditionExpression=Key('customer_id').eq(customer_id) & 
                Key('canvas_id_and_version').begins_with(f"{canvas_id}#")
            )
            versions = []
            for item in response.get('Items', []):
                version = item['canvas_id_and_version'].split('#')[1]
                versions.append(version)
            return versions
        except Exception as e:
            self.logger.error(f"Error listing canvas versions: {str(e)}")
            raise