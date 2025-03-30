from typing import Dict, List
from app.agents.prompts.overall_feedback import OverallFeedbackPrompt
from app.agents.parsers.overall_feedback_parser import OverallFeedbackParser
from app.agents.chatgpt_agent import ChatGPTAgent

class OverallFeedbackAgent:
    """Agent responsible for providing overall system feedback"""
    
    def __init__(self, model: str = "gpt-4"):
        self.model = model
        self.inference = ChatGPTAgent(model)
        self.prompt = OverallFeedbackPrompt()
        self.parser = OverallFeedbackParser()
    
    async def process(
        self,
        layer_specs: List[Dict],
        generated_layers: List[Dict],
        layer_feedback: List[Dict]
    ) -> Dict:
        """Provide overall system feedback"""
        # Create prompt with all layer information
        prompt_text = self.prompt.create_prompt(
            layer_specs=layer_specs,
            generated_layers=generated_layers,
            layer_feedback=layer_feedback
        )
        
        # Generate raw response
        raw_response = await self.inference.generate(prompt_text)
        
        # Parse response into structured format
        parsed_response = self.parser.parse_feedback(raw_response)
        
        return {
            "status": "success",
            "feedback": parsed_response
        } 