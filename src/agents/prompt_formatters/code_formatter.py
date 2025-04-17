from src.agents.prompts.dynamodb_prompts import DDB_PROMPTS
from src.agents.prompts.s3_prompts import S3_PROMPTS
from src.agents.prompts.data_model_prompts import DATA_MODEL_PROMPTS
from src.agents.prompts.api_endpoint_prompts import API_ENDPOINT_PROMPTS
from src.agents.prompts.application_logic_prompts import APPLICATION_LOGIC_PROMPTS
from src.agents.prompts.application_orchestrator_prompts import APPLICATION_ORCHESTRATOR_PROMPTS
from src.api.models.node_models import CanvasNode, CanvasNodeType
from src.storage.models.models import CanvasDefinitionDO
from src.api.models.dataplane_models import ProgrammingLanguage
from src.agents.models.agent_models import InvokeAgentRequest

import json

class CodePromptFormatter:
    """Formatter for DynamoDB prompts."""

    def get_prompt_template(self, node: CanvasNode, language: ProgrammingLanguage) -> str:
        if node.nodeType == CanvasNodeType.DYNAMO_DB:
            return DDB_PROMPTS.get(language.name.lower())
        elif node.nodeType == CanvasNodeType.S3_BUCKET:
            return S3_PROMPTS.get(language.name.lower())
        elif node.nodeType == CanvasNodeType.APPLICATION_LOGIC:
            return APPLICATION_LOGIC_PROMPTS.get(language.name.lower())
        elif node.nodeType == CanvasNodeType.DATA_MODEL:
            return DATA_MODEL_PROMPTS.get(language.name.lower())
        elif node.nodeType == CanvasNodeType.API_ENDPOINT:
            return API_ENDPOINT_PROMPTS.get(language.name.lower())
        elif node.nodeType == CanvasNodeType.APPLICATION_ORCHESTRATOR:
            return APPLICATION_ORCHESTRATOR_PROMPTS.get(language.name.lower())
        else:
            raise ValueError(f"Unsupported node type: {node.nodeType}")
    
    def format_prompt(
        self,
        node: CanvasNode,
        canvas: CanvasDefinitionDO,
        language: ProgrammingLanguage,
        invoke_agent_request: InvokeAgentRequest,
        previous_code: str = ""
    ) -> str:
        """Format the prompt for code generation."""
        template = self.get_prompt_template(node, language)
        if not template:
            raise ValueError(f"Unsupported language: {language}")

        # Set language version based on language
        language_version = {
            "python": "3.9",
            "java": "17",
            "typescript": "5.0"
        }.get(language.name.lower(), "latest")

        formatted_prompt = template.format(
            current_node_id=node.nodeId,
            instruction_source=invoke_agent_request.query_source.value,
            instruction=invoke_agent_request.query,
            canvas_definition=json.dumps(canvas.to_dict()),
            current_node_definition=json.dumps(node.to_dict()),
            previous_code=previous_code,
            language=language.name,
            language_version=language_version
        )
        print(formatted_prompt)
        return formatted_prompt