from src.agents.prompts.dynamodb_prompts import DDB_PROMPTS
from src.agents.prompts.s3_prompts import S3_PROMPTS
from src.agents.prompts.custom_service_prompts import CUSTOM_SERVICE_PROMPTS
from src.agents.prompts.api_service_prompts import API_SERVICE_PROMPTS
from src.agents.prompts.canvas_prompts import CANVAS_PROMPTS
from src.api.models.node_models import CanvasNode, CanvasNodeType
from src.storage.models.models import CanvasDefinitionDO, CanvasDO
from src.api.models.dataplane_models import ProgrammingLanguage
from src.agents.models.agent_models import InvokeAgentRequest
from src.api.models.dataplane_models import CodeFile
from typing import List
import json

class CodePromptFormatter:
    """Formatter for code generation prompts."""

    def get_prompt_template(self, node: CanvasNode, language: ProgrammingLanguage) -> str:
        """Get the appropriate prompt template based on node type and language."""
        if node.nodeType == CanvasNodeType.DYNAMO_DB:
            return DDB_PROMPTS.get(language.name.lower())
        elif node.nodeType == CanvasNodeType.S3_BUCKET:
            return S3_PROMPTS.get(language.name.lower())
        elif node.nodeType == CanvasNodeType.CUSTOM_SERVICE:
            return CUSTOM_SERVICE_PROMPTS.get(language.name.lower())
        elif node.nodeType == CanvasNodeType.API_SERVICE:
            return API_SERVICE_PROMPTS.get(language.name.lower())
        else:
            raise ValueError(f"Unsupported node type: {node.nodeType}")

    def format_node_code(self, node: CanvasNode, previous_code: List[CodeFile]) -> str:
        """Format existing code for a node."""
        node_code_files = []
        if previous_code:
            for file in previous_code:
                if file.nodeId == node.nodeId:
                    node_code_files.append(file)
        return node_code_files

    def format_code_for_node(self, node: CanvasNode, previous_code: List[CodeFile]) -> str:
        """Format code files into XML structure for a node."""
        node_code_files = []
        if previous_code:
            for file in previous_code:
                if file.nodeId == node.nodeId:
                    node_code_files.append(file)
        
        if not node_code_files:
            return ""

        code_string = "<ExistingCodeFiles>\n"
        code_string += f"<NodeId>{node.nodeId}</NodeId>\n"
        code_string += f"<NodeName>{node.nodeName}</NodeName>\n"
        for file in node_code_files:
            code_string += f"<CodeFile>\n<FilePath>{file.filePath}</FilePath>\n<Code>{file.code}</Code>\n</CodeFile>\n"
        code_string += "</ExistingCodeFiles>\n"
        return code_string

    def format_code_for_canvas(self, canvas: CanvasDO, previous_code: List[CodeFile]) -> str:
        """Format code files into XML structure for a canvas."""
        canvas_code_files = []
        if previous_code:
            for file in previous_code:
                if file.nodeId == canvas.canvas_id:
                    canvas_code_files.append(file)
        
        if not canvas_code_files:
            return ""

        code_string = "<ExistingCodeFiles>\n"
        code_string += f"<NodeId>{canvas.canvas_id}</NodeId>\n"
        code_string += f"<NodeName>{canvas.canvas_name}</NodeName>\n"
        for file in canvas_code_files:
            code_string += f"<CodeFile>\n<FilePath>{file.filePath}</FilePath>\n<Code>{file.code}</Code>\n</CodeFile>\n"
        code_string += "</ExistingCodeFiles>\n"
        return code_string

    def find_dependency_nodes(self, node: CanvasNode, canvas: CanvasDefinitionDO) -> List[CanvasNode]:
        """Find all nodes that the current node depends on."""
        dependencies = []
        current_node_id = node.nodeId
        for edge in canvas.edges:
            if edge.target == current_node_id:
                dependencies.append(edge.source)

        dependency_nodes = []
        for node in canvas.nodes:
            if node.nodeId in dependencies:
                dependency_nodes.append(node)
        return dependency_nodes

    def get_project_structure(self, existing_code: List[CodeFile]) -> str:
        """Generate a string representation of the project structure."""
        structure = ""
        for file in existing_code:
            structure += f"{file.filePath}\n"
        return structure
    
    def format_prompt(
        self,
        node: CanvasNode,
        canvas_definition: CanvasDefinitionDO,
        language: ProgrammingLanguage,
        invoke_agent_request: InvokeAgentRequest,
        existing_code: List[CodeFile]
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

        current_node_code = self.format_code_for_node(node, existing_code)
        dependencies_nodes = self.find_dependency_nodes(node, canvas_definition)
        dependency_codes = ""
        for dependency_node in dependencies_nodes:
            dependency_codes += self.format_code_for_node(dependency_node, existing_code)
            dependency_codes += "\n\n"

        formatted_prompt = template.format(
            node_id=node.nodeId,
            node_name=node.nodeName,
            current_node_id=node.nodeId,
            instruction_source=invoke_agent_request.query_source.value,
            instruction=invoke_agent_request.query,
            canvas_definition=json.dumps(canvas_definition.to_dict()),
            node_definition=json.dumps(node.to_dict()),
            existing_code=current_node_code,
            dependent_components_code=dependency_codes,
            language=language.name,
            language_version=language_version
        )
        return formatted_prompt

    def format_canvas_prompt(
        self,
        canvas: CanvasDO,
        canvas_definition: CanvasDefinitionDO,
        language: ProgrammingLanguage,
        invoke_agent_request: InvokeAgentRequest,
        existing_code: List[CodeFile]
    ) -> str:
        """Format the prompt for canvas-level code generation."""
        template = CANVAS_PROMPTS.get(language.name.lower())
        if not template:
            raise ValueError(f"Unsupported language: {language}")

        # Set language version based on language
        language_version = {
            "python": "3.9",
            "java": "17",
            "typescript": "5.0"
        }.get(language.name.lower(), "latest")

        current_canvas_code = self.format_code_for_canvas(canvas, existing_code)
        project_structure = self.get_project_structure(existing_code)

        formatted_prompt = template.format(
            node_id=canvas.canvas_id,
            node_name=canvas.canvas_name,
            instruction_source=invoke_agent_request.query_source.value,
            instruction=invoke_agent_request.query,
            canvas_definition=json.dumps(canvas_definition.to_dict()),
            existing_code=current_canvas_code,
            project_structure=project_structure,
            language=language.name,
            language_version=language_version
        )
        return formatted_prompt