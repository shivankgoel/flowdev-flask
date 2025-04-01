import os
import json
import logging
import boto3
from typing import Dict, Any
from botocore.config import Config
from . import BaseLLMInference

logger = logging.getLogger(__name__)

class BedrockInference(BaseLLMInference):
    def __init__(self, model: str = "anthropic.claude-3-sonnet-20240229-v1:0"):
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
            "capabilities": ["code generation", "multi-turn conversation"]
        }

    async def generate(self, prompt: str, **kwargs) -> str:
        try:
            response = self.client.converse(
                modelId=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [{"text": prompt}]
                    }
                ],
                system=[
                    {
                        "text": self.system_prompt
                    }
                ],
                inferenceConfig={
                    "maxTokens": kwargs.get("max_tokens", 2000),
                    "temperature": kwargs.get("temperature", 0.7),
                    "topP": kwargs.get("top_p", 1.0)
                }
            )

            # Extract text blocks from the output
            output_message = response["output"]["message"]
            text_blocks = [
                block["text"]
                for block in output_message.get("content", [])
                if "text" in block
            ]
            answer = "\n".join(text_blocks)

            logger.debug("Bedrock Converse response: %s", answer)
            return answer

        except Exception as e:
            logger.exception("Bedrock Converse API call failed")
            raise Exception(f"Error generating code with Bedrock Converse API: {str(e)}") from e

