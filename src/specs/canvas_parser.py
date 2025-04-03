from typing import Dict, Any, List, Union
from dataclasses import dataclass
from datetime import datetime

from .flow_canvas_spec import (
    CanvasDefinition,
    CanvasNodeSpec,
    CanvasPosition,
    CanvasEdgeSpec,
    EdgeDataSpec,
    ProgrammingLanguage,
    EdgeType
)
from .dynamodb_spec import (
    DynamoDBTableSpec,
    DynamoDBAttribute,
    DynamoDBAttributeType,
    DynamoDBInfraSpec,
    DynamoDBBillingMode
)
from .s3_spec import (
    S3BucketSpec,
    S3InfraSpec,
    S3EncryptionType,
    S3StorageClass
)
from .data_model_spec import (
    DataModelNodeSpec,
    Attribute,
    Relationship
)
from .application_logic_spec import (
    ApplicationLogicSpec,
    ApplicationLogicFunctionSpec,
    FunctionInput,
    FunctionOutput
)
from .api_endpoint_spec import (
    ApiEndpointSpec,
    ApiEndpointType
)
from .application_orchestrator_spec import (
    ApplicationOrchestratorSpec,
    ComposedNode,
    NodeType
)

@dataclass
class CanvasParser:
    @staticmethod
    def parse_dynamodb_spec(spec_data: Dict[str, Any]) -> DynamoDBTableSpec:
        attributes = [
            DynamoDBAttribute(
                name=attr["name"],
                type=DynamoDBAttributeType(attr["type"])
            )
            for attr in spec_data["attributes"]
        ]
        
        infra_spec = None
        if "infra_spec" in spec_data:
            infra_spec = DynamoDBInfraSpec(
                billing_mode=DynamoDBBillingMode(spec_data["infra_spec"]["billing_mode"]),
                encryption=spec_data["infra_spec"]["encryption"]
            )
            
        return DynamoDBTableSpec(
            name=spec_data["name"],
            attributes=attributes,
            hash_key=spec_data["hash_key"],
            range_key=spec_data.get("range_key"),
            infra_spec=infra_spec
        )

    @staticmethod
    def parse_s3_spec(spec_data: Dict[str, Any]) -> S3BucketSpec:
        infra_spec = S3InfraSpec(
            versioning=spec_data["infra_spec"]["versioning"],
            encryption=S3EncryptionType(spec_data["infra_spec"]["encryption"]),
            storage_class=S3StorageClass(spec_data["infra_spec"]["storage_class"])
        )
        
        return S3BucketSpec(
            name=spec_data["name"],
            file_path_prefix=spec_data.get("file_path_prefix"),
            description=spec_data.get("description"),
            infra_spec=infra_spec
        )

    @staticmethod
    def parse_data_model_spec(spec_data: Dict[str, Any]) -> DataModelNodeSpec:
        attributes = [
            Attribute(
                name=attr["name"],
                type=attr["type"],
                required=attr.get("required", False)
            )
            for attr in spec_data["attributes"]
        ]
        
        relationships = [
            Relationship(
                target_model=rel["targetModel"],
                relationship_type=rel["relationshipType"]
            )
            for rel in spec_data.get("relationships", [])
        ]
        
        return DataModelNodeSpec(
            model_name=spec_data["modelName"],
            attributes=attributes,
            relationships=relationships
        )

    @staticmethod
    def parse_application_logic_spec(spec_data: Dict[str, Any]) -> ApplicationLogicSpec:
        def parse_function(func_data: Dict[str, Any]) -> ApplicationLogicFunctionSpec:
            return ApplicationLogicFunctionSpec(
                function_name=func_data["functionName"],
                description=func_data["description"],
                inputs=[FunctionInput(**input_data) for input_data in func_data["inputs"]],
                outputs=[FunctionOutput(**output_data) for output_data in func_data["outputs"]],
                depends_on=func_data["dependsOn"]
            )

        return ApplicationLogicSpec(
            class_name=spec_data["className"],
            private_attributes=spec_data["privateAttributes"],
            public_attributes=spec_data["publicAttributes"],
            private_functions=[parse_function(func) for func in spec_data["privateFunctions"]],
            public_functions=[parse_function(func) for func in spec_data["publicFunctions"]]
        )

    @staticmethod
    def parse_api_endpoint_spec(spec_data: Dict[str, Any]) -> ApiEndpointSpec:
        return ApiEndpointSpec(
            path=spec_data["path"],
            method=spec_data["method"],
            required_query_params=spec_data["requiredQueryParams"],
            optional_query_params=spec_data["optionalQueryParams"],
            endpoint_type=ApiEndpointType(spec_data["endpointType"]),
            description=spec_data.get("description")
        )

    @staticmethod
    def parse_application_orchestrator_spec(spec_data: Dict[str, Any]) -> ApplicationOrchestratorSpec:
        composed_nodes = [
            ComposedNode(
                node_id=node["nodeId"],
                node_type=NodeType(node["nodeType"]),
                label=node["label"]
            )
            for node in spec_data["composedOf"]
        ]
        
        return ApplicationOrchestratorSpec(
            class_name=spec_data["className"],
            composed_of=composed_nodes,
            description=spec_data.get("description")
        )

    @staticmethod
    def parse_node_data(node_data: Dict[str, Any]) -> Union[
        DynamoDBTableSpec,
        S3BucketSpec,
        ApplicationLogicSpec,
        DataModelNodeSpec,
        ApiEndpointSpec,
        ApplicationOrchestratorSpec
    ]:
        """Parse node data based on its type."""
        node_type = node_data.get('type')
        
        if node_type == 'dynamodb':
            return CanvasParser.parse_dynamodb_spec(node_data)
        elif node_type == 's3':
            return CanvasParser.parse_s3_spec(node_data)
        elif node_type == 'data_model':
            return CanvasParser.parse_data_model_spec(node_data)
        elif node_type == 'application_logic':
            return CanvasParser.parse_application_logic_spec(node_data)
        elif node_type == 'api_endpoint':
            return CanvasParser.parse_api_endpoint_spec(node_data)
        elif node_type == 'application_orchestrator':
            return CanvasParser.parse_application_orchestrator_spec(node_data)
        else:
            raise ValueError(f"Unknown node type: {node_type}")

    @staticmethod
    def parse_canvas_definition(json_data: Dict[str, Any]) -> CanvasDefinition:
        nodes = [
            CanvasNodeSpec(
                id=node["id"],
                type=node["type"],
                position=CanvasPosition(**node["position"]),
                data=CanvasParser.parse_node_data(node["data"])
            )
            for node in json_data["nodes"]
        ]
        
        edges = [
            CanvasEdgeSpec(
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