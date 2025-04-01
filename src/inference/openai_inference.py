import os
import logging
from typing import Optional, List, Dict, Any
from openai import AsyncOpenAI
from dotenv import load_dotenv
from . import BaseLLMInference
from .models.inference_models import InferenceResponse, ToolCall

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class OpenAIInference(BaseLLMInference):
    def __init__(self):
        """Initialize OpenAI client."""
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4-turbo-preview"

    async def generate(self, prompt: str) -> InferenceResponse:
        """Generate text using OpenAI."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert code generator. Generate clean, well-documented code following best practices."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4096,
                stop=["</generated_code>"]
            )

            content = response.choices[0].message.content
            return InferenceResponse(text_response=content)

        except Exception as e:
            logger.error(f"Error generating text with OpenAI: {str(e)}", exc_info=True)
            return InferenceResponse(error=str(e))

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        return {
            "provider": "openai",
            "model": self.model,
            "max_tokens": 4096,
            "temperature": 0.7
        } 