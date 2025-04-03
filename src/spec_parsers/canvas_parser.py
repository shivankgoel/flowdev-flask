from typing import Dict, Any
from .base_parser import BaseParser

from specs.flow_canvas_spec import (
    CanvasDefinition,
    CanvasNodeDefinition,
    CanvasPosition,
    NodeDataSpec,
    CanvasEdgeDefinition,
    EdgeDataSpec,
    ProgrammingLanguage
)

from .node_parsers.dynamodb_parser import DynamoDBParser
from .node_parsers.s3_parser import S3Parser
from .node_parsers.data_model_parser import DataModelParser
from .node_parsers.application_logic_parser import ApplicationLogicParser
from .node_parsers.application_orchestrator_parser import ApplicationOrchestratorParser
from .node_parsers.api_endpoint_parser import ApiEndpointParser

class CanvasParser(BaseParser[CanvasDefinition]):
    @staticmethod
    def parse_node_data(node_data: Dict[str, Any], node_type: str) -> NodeDataSpec:
        spec_data = node_data["spec"]
        node_type = node_type.lower()
        
        if node_type == "dynamodbtable":
            spec = DynamoDBParser.parse(spec_data)
        elif node_type == "s3bucket":
            spec = S3Parser.parse(spec_data)
        elif node_type == "datamodel":
            spec = DataModelParser.parse(spec_data)
        elif node_type == "applicationlogic":
            spec = ApplicationLogicParser.parse(spec_data)
        elif node_type == "apiendpoint":
            spec = ApiEndpointParser.parse(spec_data)
        elif node_type == "applicationorchestrator":
            spec = ApplicationOrchestratorParser.parse(spec_data)
        else:
            raise ValueError(f"Unknown node type: {node_type}")
            
        return NodeDataSpec(spec=spec)

    @staticmethod
    def parse_canvas_definition(json_data: Dict[str, Any]) -> CanvasDefinition:
        nodes = [
            CanvasNodeDefinition(
                id=node["id"],
                type=node["type"],
                position=CanvasPosition(**node["position"]),
                data=CanvasParser.parse_node_data(node["data"], node["type"])
            )
            for node in json_data["nodes"]
        ]
        
        edges = [
            CanvasEdgeDefinition(
                id=edge["id"],
                source=edge["source"],
                target=edge["target"],
                arrow_head_type=edge["arrowHeadType"],
                data=EdgeDataSpec(**edge["data"])
            )
            for edge in json_data["edges"]
        ]
        
        return CanvasDefinition(
            canvas_id=json_data["canvasId"],
            nodes=nodes,
            edges=edges,
            version=json_data["version"],
            created_at=json_data["createdAt"],
            updated_at=json_data["updatedAt"],
            programming_language=ProgrammingLanguage(json_data["programmingLanguage"].lower())
        ) 