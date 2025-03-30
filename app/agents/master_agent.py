from typing import Dict, List, Optional
from app.agents.code_generation_agent import CodeGenerationAgent
from app.agents.layer_feedback_agent import LayerFeedbackAgent
from app.agents.overall_feedback_agent import OverallFeedbackAgent
from app.agents.layer_types import get_layer_type

class MasterAgent:
    """Master agent that orchestrates the code generation process"""
    
    def __init__(self, model: str = "gpt-4"):
        self.model = model
        self.code_generation_agent = CodeGenerationAgent(model)
        self.layer_feedback_agent = LayerFeedbackAgent(model)
        self.overall_feedback_agent = OverallFeedbackAgent(model)
    
    async def process(
        self,
        layer_specs: List[Dict],
        layer_dependencies: Optional[Dict[str, str]] = None
    ) -> Dict:
        """Process layer specifications and generate code"""
        layer_dependencies = layer_dependencies or {}
        generated_layers = []
        layer_feedback = []
        
        # Generate code for each layer in dependency order
        for layer_spec in layer_specs:
            layer_id = layer_spec["layer_id"]
            layer_type = layer_spec["layer_type"]
            
            # Get parent code if layer has dependencies
            parent_code = None
            if layer_id in layer_dependencies:
                parent_id = layer_dependencies[layer_id]
                parent_layer = next(
                    (layer for layer in generated_layers if layer["layer_id"] == parent_id),
                    None
                )
                if parent_layer:
                    parent_code = parent_layer["generated_code"]
            
            # Generate code for layer
            generation_result = await self.code_generation_agent.process(
                layer_spec=layer_spec,
                layer_id=layer_id,
                feedback=None
            )
            
            if generation_result["status"] != "success":
                raise Exception(f"Failed to generate code for layer {layer_id}")
            
            # Get feedback on generated code
            feedback_result = await self.layer_feedback_agent.process(
                layer_spec=layer_spec,
                generated_code=generation_result["generated_code"],
                layer_id=layer_id,
                parent_code=parent_code
            )
            
            # Store results
            generated_layers.append({
                "layer_id": layer_id,
                "layer_type": layer_type,
                "generated_code": generation_result["generated_code"],
                "metadata": generation_result["metadata"]
            })
            
            layer_feedback.append({
                "layer_id": layer_id,
                "feedback": feedback_result["feedback"]
            })
        
        # Get overall system feedback
        overall_feedback = await self.overall_feedback_agent.process(
            layer_specs=layer_specs,
            generated_layers=generated_layers,
            layer_feedback=layer_feedback
        )
        
        return {
            "status": "success",
            "generated_layers": generated_layers,
            "layer_feedback": layer_feedback,
            "overall_feedback": overall_feedback["feedback"]
        } 