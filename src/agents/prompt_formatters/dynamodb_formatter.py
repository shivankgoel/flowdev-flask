from src.agents.prompts.dynamodb_prompts import DDB_PROMPTS
from src.api.models.node_models import CanvasNode
from src.storage.models.models import CanvasDefinitionDO
from src.api.models.dataplane_models import ProgrammingLanguage
from src.agents.models.agent_models import InvokeAgentRequest
import json

class DynamoDBPromptFormatter:
    """Formatter for DynamoDB prompts."""
    
    def format_prompt(
        self,
        node: CanvasNode,
        canvas: CanvasDefinitionDO,
        language: ProgrammingLanguage,
        invoke_agent_request: InvokeAgentRequest,
        previous_code: str = ""
    ) -> str:
        """Format the prompt for code generation."""
        template = DDB_PROMPTS.get(language.name.lower())
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