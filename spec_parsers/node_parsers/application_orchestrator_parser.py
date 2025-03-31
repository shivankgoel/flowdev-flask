from typing import Dict, Any
from ..base_parser import BaseParser

from specs.application_orchestrator_spec import (
    ApplicationOrchestratorSpec,
    ComposedNode,
    NodeType
)

class ApplicationOrchestratorParser(BaseParser[ApplicationOrchestratorSpec]):
    @staticmethod
    def parse_composed_node(node_data: Dict[str, Any]) -> ComposedNode:
        return ComposedNode(
            node_id=node_data["nodeId"],
            node_type=NodeType(node_data["nodeType"]),
            label=node_data["label"]
        )

    @staticmethod
    def parse(spec_data: Dict[str, Any]) -> ApplicationOrchestratorSpec:
        composed_nodes = [
            ApplicationOrchestratorParser.parse_composed_node(node)
            for node in spec_data["composedOf"]
        ]
        
        return ApplicationOrchestratorSpec(
            class_name=spec_data["className"],
            composed_of=composed_nodes,
            description=BaseParser.parse_optional_field(spec_data, "description")
        ) 