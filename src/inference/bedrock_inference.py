import os
import json
import logging
import boto3
from typing import Optional, List, Dict, Any
from botocore.config import Config
from . import BaseLLMInference
from .models.inference_models import InferenceResponse, ToolCall

logger = logging.getLogger(__name__)

class BedrockInference(BaseLLMInference):
    def __init__(self, model: str = "anthropic.claude-3-haiku-20240307-v1:0"):
        config = Config(retries={"max_attempts": 3})
        self.client = boto3.client(
            service_name="bedrock-runtime",  # 👈 Must match for converse support
            config=config,
            region_name=os.getenv("AWS_REGION", "us-east-1")
        )
        self.model = model
        self.system_prompt = "You are an expert code generator. Generate clean, well-documented code following best practices."

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "provider": "AWS Bedrock",
            "model": self.model,
            "api": "converse",
            "capabilities": ["code generation", "multi-turn conversation"],
            "max_tokens": 4096,
            "temperature": 0.7
        }

    async def generate(self, prompt: str) -> InferenceResponse:
        """Generate text using Bedrock Claude."""
        try:
            # Format request body for Claude
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 250,
                "stop_sequences": ["</generated_code>"]
            }

            # Invoke model
            response = self.client.invoke_model(
                modelId=self.model,
                body=json.dumps(request_body)
            )

            # Parse response
            response_body = json.loads(response['body'].read())
            logger.debug(f"Response: {response_body}")
            
            content = response_body['content'][0]['text']

            return InferenceResponse(text_response=content)

        except Exception as e:
            logger.error(f"Error generating text with Bedrock: {str(e)}", exc_info=True)
            return InferenceResponse(error=str(e))

