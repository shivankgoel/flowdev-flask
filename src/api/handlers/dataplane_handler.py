from typing import Dict, Any
from src.api.models.dataplane_models import GenerateCodeRequest, GenerateCodeResponse
from src.storage.coordinator.dataplane_coordinator import DataplaneCoordinator

class DataplaneApiHandler:
    def __init__(self):
        self.coordinator = DataplaneCoordinator()

    async def generate_code(self, customer_id: str, request: GenerateCodeRequest) -> GenerateCodeResponse:
        try:
            response = await self.coordinator.generate_code(customer_id, request)
            return response
        except Exception as e:
            return {
                "error": str(e),
                "status_code": 500
            } 