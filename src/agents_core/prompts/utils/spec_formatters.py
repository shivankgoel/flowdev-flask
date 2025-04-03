from typing import Dict, Any, List, Union
from src.specs.flow_canvas_spec import CanvasDefinition, CanvasNodeSpec
from src.specs.dynamodb_spec import DynamoDBTableSpec
from src.specs.s3_spec import S3BucketSpec
from src.specs.data_model_spec import DataModelNodeSpec
from src.specs.application_logic_spec import ApplicationLogicSpec
from src.specs.api_endpoint_spec import ApiEndpointSpec
from src.specs.application_orchestrator_spec import ApplicationOrchestratorSpec

class CanvasToPrompt:
    """Utility class to format CanvasDefinitionSpec into prompt text."""
    
    @staticmethod
    def format(canvas: CanvasDefinition) -> str:
        """Format canvas definition into a detailed prompt section."""
        sections = [
            f"Programming Language: {canvas.programming_language.value}",
            f"Total Nodes: {len(canvas.nodes)}",
            f"Total Edges: {len(canvas.edges)}",
            "\nNode Details:"
        ]
        
        # Add details for each node
        for node in canvas.nodes:
            node_section = NodeSpecToPrompt.format(node)
            sections.append(node_section)
        
        return "\n".join(sections)

class NodeSpecToPrompt:
    """Utility class to format CanvasNodeSpec into prompt text."""
    
    @staticmethod
    def format(node: CanvasNodeSpec) -> str:
        """Format node specification into a detailed prompt section."""
        sections = [
            f"\nNode ID: {node.id}",
            f"Type: {node.type}",
            f"Position: x={node.position.x}, y={node.position.y}"
        ]
        
        # Format node data based on type
        data_section = NodeSpecToPrompt._format_node_data(node.data)
        sections.append(data_section)
        
        return "\n".join(sections)
    
    @staticmethod
    def _format_node_data(data: Union[
        DynamoDBTableSpec,
        S3BucketSpec,
        ApplicationLogicSpec,
        DataModelNodeSpec,
        ApiEndpointSpec,
        ApplicationOrchestratorSpec
    ]) -> str:
        """Format node data into a detailed prompt section."""
        if isinstance(data, DynamoDBTableSpec):
            return DynamoDBTableToPrompt.format(data)
        elif isinstance(data, S3BucketSpec):
            return f"S3 Bucket: {data.name}"
        elif isinstance(data, ApplicationLogicSpec):
            return f"Application Logic: {data.class_name}"
        elif isinstance(data, DataModelNodeSpec):
            return f"Data Model: {data.model_name}"
        elif isinstance(data, ApiEndpointSpec):
            return f"API Endpoint: {data.path}"
        elif isinstance(data, ApplicationOrchestratorSpec):
            return f"Application Orchestrator: {data.class_name}"
        else:
            return "Unknown node data type"

class DynamoDBTableToPrompt:
    """Utility class to format DynamoDBTableSpec into prompt text."""
    
    @staticmethod
    def format(spec: DynamoDBTableSpec) -> str:
        """Format DynamoDB table specification into a detailed prompt section."""
        sections = [
            f"DynamoDB Table: {spec.name}",
            f"Hash Key: {spec.hash_key}",
            f"Range Key: {spec.range_key if spec.range_key else 'None'}"
        ]
        
        # Add attributes
        sections.append("\nAttributes:")
        for attr in spec.attributes:
            sections.append(f"- {attr.name}: {attr.type.value}")
        
        return "\n".join(sections) 