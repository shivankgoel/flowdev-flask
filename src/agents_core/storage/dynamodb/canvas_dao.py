from typing import Optional, List
from datetime import datetime
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from boto3.dynamodb.conditions import Key
import logging
from src.agents_core.storage.dynamodb.base_dao import BaseDynamoDBDAO
from src.infra.dynamodb.tables import CANVAS_TABLE

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Canvas:
    """Canvas metadata stored in DynamoDB."""
    canvas_name: str
    customer_id: str
    canvas_id: str
    canvas_version: str
    created_at: str
    updated_at: str

class CanvasDAO(BaseDynamoDBDAO[Canvas]):
    """DAO for canvas operations. All canvas data is stored directly in DynamoDB."""
    
    def __init__(self):
        super().__init__(CANVAS_TABLE.table_name)
        self.logger = logging.getLogger(__name__)

    def getCanvasFromItem(self, item: dict) -> Canvas:
        """Convert a DynamoDB item to a Canvas object."""
        extracted_canvas_id = item['canvas_id_and_version'].split('#')[0]
        extracted_canvas_version = item['canvas_id_and_version'].split('#')[1]
        return Canvas(
            canvas_name=item['canvas_name'],
            customer_id=item['customer_id'],
            canvas_id=extracted_canvas_id,
            canvas_version=extracted_canvas_version,
            created_at=item['created_at'],
            updated_at=item['updated_at']
        )

    def get_canvas(self, customer_id: str, canvas_id: str, version: str) -> Optional[Canvas]:
        """Get a canvas by ID and version."""
        try:
            item = self._get_item({
                'customer_id': customer_id,
                'canvas_id_and_version': f"{canvas_id}#{version}"
            })
            if not item:
                return None
            return self.getCanvasFromItem(item)
        except Exception as e:
            self.logger.error(f"Error getting canvas: {str(e)}")
            raise

    def put_canvas(self, canvas: Canvas) -> bool:
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

    def get_all_canvases(self, customer_id: str) -> List[Canvas]:
        """Get all canvases for a customer."""
        try:
            items = self._query_items(
                'customer_id = :cid',
                {':cid': customer_id}
            )
            return [self.getCanvasFromItem(item) for item in items]
        except Exception as e:
            self.logger.error(f"Error getting all canvases: {str(e)}")
            raise

    def delete_canvas(self, customer_id: str, canvas_id: str, version: str) -> bool:
        """Delete a canvas."""
        try:
            return self._delete_item({
                'customer_id': customer_id,
                'canvas_id_and_version': f"{canvas_id}#{version}"
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