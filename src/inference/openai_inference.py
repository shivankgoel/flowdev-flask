import os
import logging
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv
from . import BaseLLMInference

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class OpenAIInference(BaseLLMInference):
    def __init__(self, model: str = "gpt-4o-mini"):
        self.client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = model
        self.system_prompt = "You are an expert code generator. Generate clean, well-documented code following best practices."

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using OpenAI's API"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=kwargs.get("max_tokens", 2000)
            )
            answer = response.choices[0].message.content
            
            # Extract JSON content from markdown code blocks if present
            if "```json" in answer:
                start = answer.find("```json") + 7
                end = answer.find("```", start)
                if end != -1:
                    answer = answer[start:end].strip()
            
            logger.debug("OpenAI answer: %s", answer)
            return answer
        except Exception as e:
            raise Exception(f"Error generating code with OpenAI: {str(e)}")

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            "provider": "OpenAI",
            "model": self.model,
            "capabilities": ["code generation", "text completion"]
        } 