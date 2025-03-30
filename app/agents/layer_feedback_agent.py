from typing import Dict, Optional
from app.agents.prompts.layer_feedback import LayerFeedbackPrompt
from app.agents.parsers.layer_feedback_parser import LayerFeedbackParser
from app.agents.chatgpt_agent import ChatGPTAgent

class LayerFeedbackAgent:
    """Agent responsible for providing feedback on a specific layer"""
    
    def __init__(self, model: str = "gpt-4"):
        self.model = model
        self.inference = ChatGPTAgent(model)
        self.prompt = LayerFeedbackPrompt()
        self.parser = LayerFeedbackParser()
    
    async def process(
        self,
        layer_spec: Dict,
        generated_code: Dict,
        layer_id: str,
        parent_code: Optional[Dict] = None
    ) -> Dict:
        """Provide feedback on a specific layer"""
        # Create prompt with optional parent code
        prompt_text = self.prompt.create_prompt(
            layer_spec=layer_spec,
            generated_code=generated_code,
            layer_id=layer_id,
            parent_code=parent_code
        )
        
        # Generate raw response
        raw_response = await self.inference.generate(prompt_text)
        
        # Parse response into structured format
        parsed_response = self.parser.parse_feedback(raw_response)
        
        return {
            "status": "success",
            "layer_id": layer_id,
            "feedback": parsed_response
        } 