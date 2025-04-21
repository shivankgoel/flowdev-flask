from src.agents.coordinator.agent_coordinator import AgentCoordinator
from src.storage.coordinator.canvas_coordinator import CanvasCoordinator
from src.storage.coordinator.base_coordinator import BaseCoordinator, StorageCoordinatorError
from src.api.models.dataplane_models import GenerateCodeRequest, GenerateCodeResponse, CodeFile
from typing import List
from src.storage.s3.s3_dao import S3DAO
from src.storage.models.models import CodeDO
from src.api.models.dataplane_models import ApplyCodeChangesRequest, GetCodeRequest
import json
from src.storage.s3.s3_dao import S3DAONotFoundError

class DataplaneCoordinator(BaseCoordinator):
    """Coordinates dataplane operations for code generation."""
    
    def __init__(self):
        super().__init__()
        self.agent_coordinator = AgentCoordinator()
        self.canvas_coordinator = CanvasCoordinator()
        self.s3_dao = S3DAO()

    def get_s3_uri(self, customer_id: str, canvas_id: str, canvas_version: str) -> str:
        return f"s3://{self.s3_dao.bucket_name}/canvas-code/{customer_id}/{canvas_id}/{canvas_version}.json"


    async def get_code_by_request(self, customer_id: str, request: GetCodeRequest) -> CodeDO:
        canvas_id = request.canvasId
        canvas_version = request.canvasVersion
        code_s3_uri = self.get_s3_uri(customer_id, canvas_id, canvas_version)
        return await self.get_code_by_uri(code_s3_uri)

    async def get_code_by_uri(self, code_s3_uri: str) -> CodeDO:
        try:
            code_json = self.s3_dao.get_object(code_s3_uri)
            if not code_json:
                self.logger.info(f"No code found at {code_s3_uri}, returning empty CodeDO")
                return CodeDO(files=[])
            
            code_dict = json.loads(code_json)
            code_do = CodeDO(**code_dict)
            final_files = []
            for file_dict in code_do.files:
                if isinstance(file_dict, dict):
                    file = CodeFile(**file_dict)
                else:
                    file = file_dict
                final_files.append(file)
            code_do.files = final_files
            return code_do
        except S3DAONotFoundError:
            self.logger.info(f"No code found at {code_s3_uri}, returning empty CodeDO")
            return CodeDO(files=[])
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing JSON from S3: {str(e)}")
            return CodeDO(files=[])
        except Exception as e:
            self.logger.error(f"Error getting code from S3: {str(e)}")
            return CodeDO(files=[])

    async def apply_code_changes(self, customer_id: str, request: ApplyCodeChangesRequest) -> bool:
        try:
            canvas_id = request.canvasId
            canvas_version = request.canvasVersion
            
            if not request.codeChange:
                raise ValueError("No code change provided")

            canvas_do, canvas_definition = self.canvas_coordinator.get_canvas(
                customer_id,
                request.canvasId,
                request.canvasVersion
            )

            if not canvas_do or not canvas_definition:
                raise StorageCoordinatorError(f"Canvas not found: {request.canvasId} version {request.canvasVersion}")
                
                
            # Get file lists from request - these are now guaranteed to be CodeFile objects
            added_files = request.codeChange.addedFiles or []
            updated_files = request.codeChange.updatedFiles or []
            deleted_files = request.codeChange.deletedFiles or []

            # Get existing code files
            existing_code_do = await self.get_code_by_request(customer_id, GetCodeRequest(canvasId=canvas_id, canvasVersion=canvas_version))
            if not existing_code_do:
                existing_code_do = CodeDO(files=[])

            # Create sets of file paths for faster lookup
            deleted_paths = {f.filePath for f in deleted_files}
            updated_paths = {f.filePath for f in updated_files}
            added_paths = {f.filePath for f in added_files}

            # Process existing files
            final_files = []
            for file in existing_code_do.files:
                if file.filePath not in deleted_paths and file.filePath not in updated_paths:
                    final_files.append(file)

            # Add updated and new files
            final_files.extend(updated_files)
            final_files.extend(added_files)

            # Create new code DO and save to S3
            code_do = CodeDO(files=final_files)
            code_s3_uri = self.save_code_to_s3(customer_id, canvas_id, canvas_version, code_do)
            
            # Verify the save was successful
            if not code_s3_uri:
                raise StorageCoordinatorError("Failed to save code to S3")

            canvas_do.canvas_code_s3_uri = code_s3_uri
            self.canvas_coordinator.update_canvas(canvas_do)

            return True
        except Exception as e:
            self.logger.exception(f"Error applying code changes: {str(e)}")
            raise StorageCoordinatorError(f"Failed to apply code changes: {str(e)}")

    def save_code(self, code_s3_uri: str, code_do: CodeDO) -> bool:
        return self.s3_dao.put_object(code_s3_uri, code_do.to_json())

    def save_code_to_s3(
        self,
        customer_id: str,
        canvas_id: str,
        canvas_version: str,
        code_do: CodeDO
    ) -> str:
        s3_uri = self.get_s3_uri(customer_id, canvas_id, canvas_version)
        self.logger.info(f"Saving code to S3 at {s3_uri}")
        self.save_code(s3_uri, code_do)
        return s3_uri

    def merge_existing_and_new_code(
        self,
        node_id: str,
        old_code_files: List[CodeFile],
        new_code_files: List[CodeFile],
    ) -> GenerateCodeResponse:
        if not old_code_files:
            old_code_files = []
        old_code_for_current_node = []
        for file in old_code_files:
            if file.nodeId == node_id:
                old_code_for_current_node.append(file)
        added_files = [] # files that exist in new code but not in old code
        updated_files = [] # files that exist in both old and new code
        deleted_files = [] # files that exist in old code but not in new code
        for new_file in new_code_files:
            if new_file.filePath not in [file.filePath for file in old_code_for_current_node]:
                added_files.append(new_file)
            else:
                updated_files.append(new_file)
        for old_file in old_code_for_current_node:
            if old_file.filePath not in [file.filePath for file in new_code_files]:
                deleted_files.append(old_file)
        return GenerateCodeResponse (
            addedFiles=added_files,
            updatedFiles=updated_files,
            deletedFiles=deleted_files
        )

    async def generate_code(
        self,
        customer_id: str,
        request: GenerateCodeRequest
    ) -> GenerateCodeResponse:
        try:
            # Get canvas and node information
            canvas_do, canvas_definition = self.canvas_coordinator.get_canvas(
                customer_id,
                request.canvasId,
                request.canvasVersion
            )

            existing_code_do = await self.get_code_by_request(
                customer_id, 
                GetCodeRequest(canvasId=request.canvasId, canvasVersion=request.canvasVersion)
            )
            
            if not canvas_do or not canvas_definition:
                raise StorageCoordinatorError(f"Canvas not found: {request.canvasId} version {request.canvasVersion}")
            
            # Find the target node
            target_node = None
            for node in canvas_definition.nodes:
                if node.nodeId == request.nodeId:
                    target_node = node
                    break
            
            if not target_node:
                raise StorageCoordinatorError(f"Node not found: {request.nodeId}")

            # Get the code for the target node
            existing_code: List[CodeFile] = existing_code_do.files

            # Generate code using agent coordinator
            response = await self.agent_coordinator.generate_code(
                node=target_node,
                canvas=canvas_definition,
                language=request.programmingLanguage,
                existing_code=existing_code,
                inference_provider="bedrock"  # Default to Bedrock for now
            )

            # Merge existing and new code
            return GenerateCodeResponse(
                addedFiles=response.code_parser_response.addedFiles,
                updatedFiles=response.code_parser_response.updatedFiles,
                deletedFiles=response.code_parser_response.deletedFiles
            )

        except Exception as e:
            self.logger.error(f"Error generating code: {str(e)}")
            return {
                "error": str(e),
                "status_code": 500
            }
