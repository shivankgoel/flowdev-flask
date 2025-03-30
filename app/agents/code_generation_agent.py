from typing import Dict, Optional
from app.agents.prompts.layer_code_generation import LayerCodeGenerationPrompt
from app.agents.parsers.code_generation_parser import CodeGenerationParser
from app.agents.chatgpt_agent import ChatGPTAgent

class CodeGenerationAgent:
    """Agent responsible for generating code for a specific layer"""
    
    def __init__(self, model: str = "gpt-4"):
        self.model = model
        self.inference = ChatGPTAgent(model)
        self.prompt = LayerCodeGenerationPrompt()
        self.parser = CodeGenerationParser()
    
    async def process(
        self,
        layer_spec: Dict,
        layer_id: str,
        feedback: Optional[Dict] = None
    ) -> Dict:
        """Generate code for a specific layer"""
        # Create prompt with optional feedback
        prompt_text = self.prompt.create_prompt(
            layer_spec=layer_spec,
            layer_id=layer_id,
            feedback=feedback
        )
        
        # Generate raw response
        raw_response = await self.inference.generate(prompt_text)
        
        # Parse response into structured format
        parsed_response = self.parser.parse_response(raw_response)
        
        # Extract generated code and metadata
        generated_code = parsed_response.get("generated_code", {})
        metadata = parsed_response.get("metadata", {})
        
        return {
            "status": parsed_response.get("status", "success"),
            "generated_code": generated_code,
            "layer_id": layer_id,
            "metadata": metadata
        } 