from pprint import pprint
from typing import Dict, Any
from .base import BaseAgent
from .prompts.layer_code_generation import LayerCodeGenerationPrompt
from .inference.openai_inference import OpenAIInference
from .layer_manager import LayerManager


class ChatGPTAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ChatGPTAgent",
            description="Generates code using OpenAI's ChatGPT API"
        )
        self.prompt_template = LayerCodeGenerationPrompt()
        self.llm = OpenAIInference()
        self.layer_manager = LayerManager()

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the input data to generate code using ChatGPT
        """
        response = {
            "status": "processing",
            "generated_code": {},
            "metadata": {}
        }

        try:
            # Add layer specification to manager
            layer_spec = input_data.get("layer_spec", {})
            print(f"Processing layer: {layer_spec}")

            self.layer_manager.add_layer(layer_spec)
            print(f"Layer order: {self.get_layer_order()}")
            
            # Get layer ID and parent code
            layer_id = layer_spec.get("layer_id")
            parent_code = self.layer_manager.get_parent_code(layer_id)
            print(f"Parent code for layer {layer_id}:\n{parent_code}")
            
            # Create the prompt using the template
            prompt = self.prompt_template.create_prompt(
                layer_spec=layer_spec,
                parent_code=parent_code
            )

            pprint(f"Prompt for layer {layer_id}:\n{prompt}")
            
            # Generate code using the LLM
            completion = await self.llm.generate(prompt)
            
            # Store the generated code
            self.layer_manager.set_generated_code(layer_id, completion)
            
            # Process the response
            response["generated_code"] = {
                layer_id: completion
            }
            response["metadata"] = {
                "layer_id": layer_id,
                "language": layer_spec.get("language", "python"),
                "artifact_type": layer_spec.get("artifact_type", "class"),
                "functionality_type": layer_spec.get("functionality_type", "unknown"),
                **self.llm.get_model_info()
            }
            response["status"] = "completed"

        except Exception as e:
            response["status"] = "error"
            response["error"] = str(e)

        return response

    def get_layer_order(self) -> list:
        """Get the order of layers to process based on dependencies"""
        return self.layer_manager.get_layer_order()

    def get_all_generated_code(self) -> Dict[int, str]:
        """Get all generated code for all layers"""
        return self.layer_manager.generated_code 