from typing import Dict, Any
from src.api.models.dataplane_models import GenerateCodeRequest, GenerateCodeResponse, ApplyCodeChangesRequest, ApplyCodeChangesResponse, GetCodeRequest, GetCodeResponse
from src.storage.coordinator.dataplane_coordinator import DataplaneCoordinator
from src.storage.models.models import CodeDO

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

    async def apply_code_changes(self, customer_id: str, request: ApplyCodeChangesRequest) -> ApplyCodeChangesResponse:
        try:
            response = await self.coordinator.apply_code_changes(customer_id, request)
            return ApplyCodeChangesResponse(success=True)
        except Exception as e:
            return {
                "error": str(e),
                "status_code": 500
            }

    async def get_code(self, customer_id: str, request: GetCodeRequest) -> GetCodeResponse:
        try:
            code_do: CodeDO = await self.coordinator.get_code_by_request(customer_id, request)
            if not code_do:
                return GetCodeResponse(files=[])
            return GetCodeResponse(
                files=code_do.files
            )
        except Exception as e:
            return {
                "error": str(e),
                "status_code": 500
            }