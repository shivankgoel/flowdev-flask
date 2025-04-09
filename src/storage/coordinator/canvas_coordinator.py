from typing import Optional, List, Tuple
from src.storage.dynamodb.canvas_dao import CanvasDAO
from src.storage.s3.s3_dao import S3DAO
from src.storage.models.models import CanvasDO, CanvasDefinitionDO
from src.api.models.node_models import CanvasNodeType
from src.api.models.node_configs.dynamodb_node_config import (
    DynamoDbNodeConfig,
    DynamoDBAttributeType,
    DynamoDBBillingMode,
    DynamoDBInfraConfig
)
from src.api.models.json_encoder import EnumEncoder
from .base_coordinator import BaseCoordinator
import json
import uuid
from src.api.models.canvas_models import CanvasNode, CanvasEdge

class CanvasCoordinator(BaseCoordinator):
    """Coordinates canvas operations between DynamoDB and S3."""
    
    def __init__(self):
        super().__init__()
        self.canvas_dao = CanvasDAO()
        self.s3_dao = S3DAO()

    def get_canvas(self, customer_id: str, canvas_id: str, canvas_version: str) -> Tuple[Optional[CanvasDO], Optional[CanvasDefinitionDO]]:
        try:
            canvas_do = self.canvas_dao.get_canvas(customer_id, canvas_id, canvas_version)
            if not canvas_do:
                return None, None
                
            # Fetch the canvas definition from S3 if URI exists
            canvas_definition = None
            if canvas_do.canvas_definition_s3_uri:
                canvas_definition = self._get_canvas_definition(canvas_do.canvas_definition_s3_uri)
            
            return canvas_do, canvas_definition
        except Exception as e:
            self.logger.error(f"Error getting canvas: {str(e)}")
            return None, None

    def _get_canvas_definition(self, s3_uri: str) -> Optional[CanvasDefinitionDO]:
        try:
            definition_json = self.s3_dao.get_object(s3_uri)
            if not definition_json:
                self.logger.error("Empty JSON data received from S3")
                return None
                
            try:
                # Parse JSON data
                data = json.loads(definition_json)
                
                # Deserialize nodes and edges
                nodes = [CanvasNode(**node) for node in data.get('nodes', [])]
                edges = [CanvasEdge(**edge) for edge in data.get('edges', [])]
                
                # Create CanvasDefinitionDO with deserialized objects
                return CanvasDefinitionDO(nodes=nodes, edges=edges)
            except Exception as e:
                self.logger.error(f"Error deserializing canvas definition JSON: {str(e)}")
                self.logger.error(f"JSON content: {definition_json}")
                return None
        except Exception as e:
            self.logger.error(f"Error getting canvas definition from S3: {str(e)}")
            return None

    def save_canvas(self, canvas_do: CanvasDO, canvas_definition: Optional[CanvasDefinitionDO] = None) -> bool:
        try:
            if canvas_definition:
                # Debug logging
                print(f"Canvas definition nodes: {canvas_definition.nodes}")
                print(f"First node type: {type(canvas_definition.nodes[0]) if canvas_definition.nodes else 'No nodes'}")
                
                # Ensure default values are set for nodes
                for node in canvas_definition.nodes:
                    print(f"Node: {node}")
                    print(f"Node type: {type(node)}")
                    print(f"Node attributes: {dir(node)}")
                    if not node.nodeType:
                        node.nodeType = CanvasNodeType.DYNAMO_DB
                    if node.nodeConfig and isinstance(node.nodeConfig, DynamoDbNodeConfig):
                        # Set default values for DynamoDB node config
                        for attr in node.nodeConfig.attributes:
                            if not attr.type:
                                attr.type = DynamoDBAttributeType.STRING
                        if not node.nodeConfig.infraSpec:
                            node.nodeConfig.infraSpec = DynamoDBInfraConfig(
                                billingMode=DynamoDBBillingMode.PAY_PER_REQUEST,
                                encryption=True
                            )
                        elif not node.nodeConfig.infraSpec.billingMode:
                            node.nodeConfig.infraSpec.billingMode = DynamoDBBillingMode.PAY_PER_REQUEST

                # Generate S3 URI for the canvas definition
                s3_uri = f"s3://{self.s3_dao.bucket_name}/canvas-definitions/{canvas_do.customer_id}/{canvas_do.canvas_id}/{canvas_do.canvas_version}.json"
                
                # Convert canvas definition to JSON using custom encoder
                definition_json = json.dumps(canvas_definition, cls=EnumEncoder)
                print(f"Definition JSON: {definition_json}")
                
                # Save canvas definition to S3
                if not self.s3_dao.put_object(s3_uri, definition_json):
                    return False
                
                # Update canvas DO with S3 URI
                canvas_do.canvas_definition_s3_uri = s3_uri
            else:
                # If no definition provided, clear the S3 URI
                canvas_do.canvas_definition_s3_uri = None
            
            # Save canvas metadata to DynamoDB
            print(f"Saving canvas: {canvas_do}")
            return self.canvas_dao.save_canvas(canvas_do)
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
            # Get canvas to find S3 URI
            canvas_do = self.canvas_dao.get_canvas(customer_id, canvas_id, canvas_version)
            if canvas_do and canvas_do.canvas_definition_s3_uri:
                # Delete canvas definition from S3 if URI exists
                self.s3_dao.delete_object(canvas_do.canvas_definition_s3_uri)
            
            # Delete canvas metadata from DynamoDB
            return self.canvas_dao.delete_canvas(customer_id, canvas_id, canvas_version)
        except Exception as e:
            self.logger.error(f"Error deleting canvas: {str(e)}")
            raise

    def list_canvas_versions(self, customer_id: str, canvas_id: str) -> List[str]:
        try:
            return self.canvas_dao.list_canvas_versions(customer_id, canvas_id)
        except Exception as e:
            self.logger.error(f"Error listing canvas versions: {str(e)}")
            raise

    def create_canvas_version(self, customer_id: str, canvas_id: str) -> Optional[str]:
        try:
            draft_canvas, draft_definition = self.get_canvas(customer_id, canvas_id, "draft")
            if not draft_canvas:
                self.logger.error(f"Draft canvas not found for {canvas_id}.")
                return None

            new_version = str(uuid.uuid4())
            timestamp = self._get_timestamp()

            # Create the new CanvasDO with the draft definition
            canvas_do = CanvasDO(
                canvas_name=draft_canvas.canvas_name,
                customer_id=customer_id,
                canvas_id=canvas_id,
                canvas_version=new_version,
                created_at=timestamp,
                updated_at=timestamp,
                canvas_definition_s3_uri=None  # Will be set in save_canvas
            )

            # Save the canvas with the draft definition
            if not self.save_canvas(canvas_do, draft_definition):
                return None

            return new_version
        except Exception as e:
            self.logger.error(f"Error creating canvas version: {str(e)}")
            raise

    def create_new_canvas(self, customer_id: str, canvas_id: str, canvas_version: str, canvas_name: str, canvas_definition: Optional[CanvasDefinitionDO] = None) -> bool:
        try:
            timestamp = self._get_timestamp()
            
            canvas_do = CanvasDO(
                canvas_name=canvas_name,
                customer_id=customer_id,
                canvas_id=canvas_id,
                canvas_version=canvas_version,
                created_at=timestamp,
                updated_at=timestamp,
                canvas_definition_s3_uri=None  # Will be set in save_canvas if definition exists
            )
            
            return self.save_canvas(canvas_do, canvas_definition)
        except Exception as e:
            self.logger.error(f"Error creating new canvas: {str(e)}")
            return False 