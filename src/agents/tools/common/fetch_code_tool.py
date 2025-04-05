import logging
from typing import Dict, Any
from src.specs.flow_canvas_spec import CanvasDefinition
from src.storage.s3_dao import S3DAO
from src.agents_core.tools.common.tool_model import ToolDefinition, ToolParameter, ToolParameterType, ToolResponse

logger = logging.getLogger(__name__)

class FetchCodeTool:
    """Tool for fetching code from other nodes."""
    
    def __init__(
        self,
        canvas: CanvasDefinition,
        current_node_id: str,
        s3_dao: S3DAO
    ):
        self.canvas = canvas
        self.current_node_id = current_node_id
        self.s3_dao = s3_dao
        
        # Define the tool for LLM consumption
        self.tool_definition = ToolDefinition(
            name="fetch_node_code",
            description="Fetch the code from another node in the canvas. Returns the code if found.",
            parameters=[
                ToolParameter(
                    name="target_node_id",
                    type=ToolParameterType.STRING,
                    description="The ID of the node to fetch code from"
                )
            ],
            handler=self.__call__
        )
         
    async def __call__(self, args: Dict[str, Any]) -> ToolResponse:
        """Fetch code from another node."""
        try:
            # Validate arguments
            validation_error = self.tool_definition.validate_args(args)
            if validation_error:
                return ToolResponse.error_response(validation_error)
                
            target_node_id = args["target_node_id"]
                
            # Validate target node exists
            if target_node_id not in self.canvas.nodes:
                return ToolResponse.error_response(f"Target node {target_node_id} not found in canvas")
                
            # Fetch the code
            code = self.s3_dao.fetch_code(
                customer_id=self.canvas.customer_id,
                canvas_id=self.canvas.canvas_id,
                canvas_version=self.canvas.canvas_version,
                node_id=target_node_id,
                language=self.canvas.programming_language.value
            )
            
            if not code:
                return ToolResponse.error_response(f"No code found for node {target_node_id}")
                
            return ToolResponse.success_response(
                message=f"Successfully fetched code from node {target_node_id}",
                data={"code": code}
            )
            
        except Exception as e:
            logger.error(f"Error fetching code: {str(e)}")
            return ToolResponse.error_response(f"Failed to fetch code: {str(e)}") 