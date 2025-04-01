from typing import Dict, Any
from src.specs.dynamodb_spec import DynamoDBTableSpec
from src.specs.flow_canvas_spec import CanvasDefinitionSpec
from ..dynamodb_prompts import PROMPTS
from ..utils.spec_formatters import CanvasToPrompt, NodeSpecToPrompt, DynamoDBTableToPrompt

class DynamoDBPromptFormatter:
    """Formatter for DynamoDB prompts."""
    
    def format_prompt(
        self,
        spec: DynamoDBTableSpec,
        language: str,
        current_node_id: str,
        canvas: CanvasDefinitionSpec,
        instruction_source: str = "",
        instructions: str = "",
        previous_code: str = ""
    ) -> str:
        """Format the prompt for DynamoDB code generation."""
        if not isinstance(spec, DynamoDBTableSpec):
            raise ValueError("Spec must be of type DynamoDBTableSpec")
            
        # Get the prompt template for the language
        prompt_template = PROMPTS.get(language.lower())
        if not prompt_template:
            raise ValueError(f"Unsupported language: {language}")
            
        # Format the current node definition
        current_node = canvas.nodes.get(current_node_id)
        if not current_node:
            raise ValueError(f"Node with id {current_node_id} not found in canvas")
            
        current_node_definition = NodeSpecToPrompt.format(current_node)
        
        # Format the complete canvas definition
        canvas_definition = CanvasToPrompt.format(canvas)
        
        # Format the prompt with all sections
        return prompt_template.format(
            current_node_id=current_node_id,
            instruction_source=instruction_source,
            instructions=instructions,
            canvas_definition=canvas_definition,
            current_node_definition=current_node_definition,
            previous_code=previous_code
        ) 