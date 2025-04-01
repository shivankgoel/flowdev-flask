from typing import Dict, Any, List
from src.specs.flow_canvas_spec import CanvasDefinitionSpec, CanvasNodeSpec, NodeDataSpec
from src.specs.dynamodb_spec import DynamoDBTableSpec

class CanvasToPrompt:
    """Utility class to format CanvasDefinitionSpec into prompt text."""
    
    @staticmethod
    def format(canvas: CanvasDefinitionSpec) -> str:
        """Format canvas definition into a detailed prompt section."""
        sections = [
            f"Programming Language: {canvas.programming_language.value}",
            f"Total Nodes: {len(canvas.nodes)}",
            f"Total Edges: {len(canvas.edges)}",
            "\nNode Details:"
        ]
        
        # Add details for each node
        for node_id, node in canvas.nodes.items():
            node_section = NodeSpecToPrompt.format(node)
            sections.append(f"\nNode {node_id}:")
            sections.append(node_section)
            
        # Add edge information
        if canvas.edges:
            sections.append("\nEdge Connections:")
            for edge in canvas.edges:
                sections.append(f"- {edge.source} -> {edge.target}")
                
        return "\n".join(sections)

class NodeSpecToPrompt:
    """Utility class to format CanvasNodeSpec into prompt text."""
    
    @staticmethod
    def format(node: CanvasNodeSpec) -> str:
        """Format node specification into a detailed prompt section."""
        sections = [
            f"Type: {node.type}",
            f"Position: {node.position}",
            f"Data: {NodeSpecToPrompt._format_node_data(node.data)}"
        ]
        return "\n".join(sections)
    
    @staticmethod
    def _format_node_data(data: NodeDataSpec) -> str:
        """Format node data into prompt text."""
        if isinstance(data.spec, DynamoDBTableSpec):
            return DynamoDBTableToPrompt.format(data.spec)
        return str(data.spec)  # Fallback for unknown spec types

class DynamoDBTableToPrompt:
    """Utility class to format DynamoDBTableSpec into prompt text."""
    
    @staticmethod
    def format(spec: DynamoDBTableSpec) -> str:
        """Format DynamoDB table spec into a detailed prompt section."""
        sections = [
            f"Table Name: {spec.name}",
            f"Hash Key: {spec.hash_key}",
        ]
        
        if spec.range_key:
            sections.append(f"Range Key: {spec.range_key}")
            
        if spec.attributes:
            sections.append("\nAttributes:")
            for attr in spec.attributes:
                sections.append(f"- {attr.name}: {attr.type}")
                
        return "\n".join(sections) 