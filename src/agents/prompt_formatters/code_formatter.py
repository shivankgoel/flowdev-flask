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
from src.api.models.dataplane_models import CodeFile
from typing import List

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

    def format_previous_code(self, node: CanvasNode, previous_code: List[CodeFile]) -> str:
        node_code_files = []
        if previous_code:
            for file in previous_code:
                if file.nodeId == node.nodeId:
                    node_code_files.append(file)
        
        if not node_code_files:
            return ""

        """
        Generate a string in the following format:
        <PreviousCodeFiles>
            <CodeFile>
                <FilePath>src/folder1/folder2/fileName1.fileExtension</FilePath>
                <Code>code for the file including imports</Code>
            </CodeFile>
            <CodeFile>
                <FilePath>src/folder1/folder3/fileName2.fileExtension</FilePath>
                <Code>code for the file including imports</Code>
            </CodeFile>
        </PreviousCodeFiles>
        """

        previous_code_string = "<PreviousCodeFiles>\n"
        for file in node_code_files:
            previous_code_string += f"<CodeFile>\n<FilePath>{file.filePath}</FilePath>\n<Code>{file.code}</Code>\n</CodeFile>\n"
        previous_code_string += "</PreviousCodeFiles>\n"
        return previous_code_string
    
    def format_prompt(
        self,
        node: CanvasNode,
        canvas: CanvasDefinitionDO,
        language: ProgrammingLanguage,
        invoke_agent_request: InvokeAgentRequest,
        previous_code: List[CodeFile]
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

        previous_code_str = self.format_previous_code(node, previous_code)

        component_name = ""
        if node.nodeType == CanvasNodeType.DYNAMO_DB:
            component_name = f"{node.nodeConfig.get('name', 'DynamoDB')}Table"
        elif node.nodeType == CanvasNodeType.S3_BUCKET:
            component_name = f"{node.nodeConfig.get('name', 'S3')}Bucket"
        elif node.nodeType == CanvasNodeType.APPLICATION_LOGIC:
            component_name = f"{node.nodeConfig.get('className', 'Application')}ApplicationLogic"
        elif node.nodeType == CanvasNodeType.DATA_MODEL:
            component_name = f"{node.nodeConfig.get('modelName', 'DataModel')}DataModel"
        elif node.nodeType == CanvasNodeType.API_ENDPOINT:
            component_name = f"{node.nodeConfig.get('endpointName', 'Api')}ApiEndpoint"
        elif node.nodeType == CanvasNodeType.APPLICATION_ORCHESTRATOR:
            component_name = f"{node.nodeConfig.get('orchestratorName', 'Orchestrator')}ApplicationOrchestrator"

        # Remove any spaces from the component name
        component_name = component_name.replace(" ", "")

        formatted_prompt = template.format(
            component_name=component_name,
            current_node_id=node.nodeId,
            instruction_source=invoke_agent_request.query_source.value,
            instruction=invoke_agent_request.query,
            canvas_definition=json.dumps(canvas.to_dict()),
            current_node_definition=json.dumps(node.to_dict()),
            previous_code=previous_code_str,
            language=language.name,
            language_version=language_version
        )
        print(formatted_prompt)
        return formatted_prompt