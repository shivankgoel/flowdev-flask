from typing import Optional, List
from src.storage.dynamodb.canvas_dao import CanvasDAO
from src.storage.s3.s3_dao import S3DAO
from src.storage.models.models import CanvasDO
from .base_coordinator import BaseCoordinator
import uuid

class CanvasCoordinator(BaseCoordinator):
    """Coordinates canvas operations between DynamoDB and S3."""
    
    def __init__(self):
        super().__init__()
        self.canvas_dao = CanvasDAO()
        self.s3_dao = S3DAO()

    def get_canvas(self, customer_id: str, canvas_id: str, canvas_version: str) -> Optional[CanvasDO]:
        try:
            return self.canvas_dao.get_canvas(customer_id, canvas_id, canvas_version)
        except Exception as e:
            self.logger.error(f"Error getting canvas: {str(e)}")
            return None

    def save_canvas(self, canvas: CanvasDO) -> bool:
        try:
            return self.canvas_dao.save_canvas(canvas)
        except Exception as e:
            self.logger.error(f"Error saving canvas: {str(e)}")
            return False

    def get_all_canvases(self, customer_id: str) -> List[CanvasDO]:
        try:
            return self.canvas_dao.get_all_canvases(customer_id)
        except Exception as e:
            self.logger.error(f"Error getting all canvases: {str(e)}")
            raise

    def get_unique_canvases(self, customer_id: str) -> List[CanvasDO]:
        try:
            return self.canvas_dao.get_unique_canvases(customer_id)
        except Exception as e:
            self.logger.error(f"Error getting unique canvases: {str(e)}")
            raise

    def delete_canvas_all_versions(self, customer_id: str, canvas_id: str) -> bool:
        try:
            all_versions = self.list_canvas_versions(customer_id, canvas_id)
            for version in all_versions:
                self.delete_canvas(customer_id, canvas_id, version)
            return True
        except Exception as e:
            self.logger.error(f"Error deleting canvas all versions: {str(e)}")
            raise

    def delete_canvas(self, customer_id: str, canvas_id: str, canvas_version: str) -> bool:
        try:
            return self.canvas_dao.delete_canvas(customer_id, canvas_id, canvas_version)
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
            draft_canvas = self.get_canvas(customer_id, canvas_id, "draft")
            if not draft_canvas:
                return None

            new_version = str(uuid.uuid4())
            timestamp = self._get_timestamp()

            canvas_do = CanvasDO(
                canvas_name=draft_canvas.canvas_name,
                customer_id=customer_id,
                canvas_id=canvas_id,
                canvas_version=new_version,
                created_at=timestamp,
                updated_at=timestamp
            )

            if not self.save_canvas(canvas_do):
                return None

            return new_version
        except Exception as e:
            self.logger.error(f"Error creating canvas version: {str(e)}")
            raise

    def create_new_canvas(self, customer_id: str, canvas_id: str, canvas_version: str, canvas_name: str) -> bool:
        try:
            timestamp = self._get_timestamp()
            
            canvas_do = CanvasDO(
                canvas_name=canvas_name,
                customer_id=customer_id,
                canvas_id=canvas_id,
                canvas_version=canvas_version,
                created_at=timestamp,
                updated_at=timestamp
            )
            
            return self.save_canvas(canvas_do)
        except Exception as e:
            self.logger.error(f"Error creating new canvas: {str(e)}")
            return False 