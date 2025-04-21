import re
import logging
from typing import List, Optional
from dataclasses import dataclass
from ..models.parser_models import CodeFile, CodeParserResponse, ReasoningStep
from src.api.models.dataplane_models import ProgrammingLanguage

logger = logging.getLogger(__name__)


class CodeParser:
    """Parser for code generation responses."""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
    
    def _parse_reasoning(self, response: str) -> List[ReasoningStep]:
        """Extract reasoning steps from XML tags."""
        reasoning_steps = []
        reasoning_match = re.search(r'<Reasoning>(.*?)</Reasoning>', response, re.DOTALL)
        if reasoning_match:
            step_matches = re.finditer(r'<Step>(.*?)</Step>', reasoning_match.group(1), re.DOTALL)
            for match in step_matches:
                reason_match = re.search(r'<Reason>(.*?)</Reason>', match.group(1), re.DOTALL)
                if reason_match:
                    reasoning_steps.append(ReasoningStep(reason=reason_match.group(1).strip()))
        return reasoning_steps
    
    def parse(self, response: str, language: ProgrammingLanguage) -> CodeParserResponse:
        """Extract code files and reasoning from XML tags."""
        try:
            # Initialize lists for different types of files
            added_files = []
            updated_files = []
            deleted_files = []

            # Parse reasoning steps
            reasoning_steps = self._parse_reasoning(response)

            # Parse new code files
            new_code_files_match = re.search(r'<NewCodeFiles>(.*?)</NewCodeFiles>', response, re.DOTALL)
            if new_code_files_match:
                code_file_matches = re.finditer(r'<CodeFile>(.*?)</CodeFile>', new_code_files_match.group(1), re.DOTALL)
                for match in code_file_matches:
                    file_path_match = re.search(r'<FilePath>(.*?)</FilePath>', match.group(1), re.DOTALL)
                    code_match = re.search(r'<Code>(.*?)</Code>', match.group(1), re.DOTALL)
                    if file_path_match and code_match:
                        added_files.append(CodeFile(
                            nodeId=self.node_id,
                            filePath=file_path_match.group(1).strip(),
                            code=code_match.group(1).strip(),
                            programmingLanguage=language
                        ))

            # Parse updated code files
            updated_code_files_match = re.search(r'<UpdatedCodeFiles>(.*?)</UpdatedCodeFiles>', response, re.DOTALL)
            if updated_code_files_match:
                code_file_matches = re.finditer(r'<CodeFile>(.*?)</CodeFile>', updated_code_files_match.group(1), re.DOTALL)
                for match in code_file_matches:
                    file_path_match = re.search(r'<FilePath>(.*?)</FilePath>', match.group(1), re.DOTALL)
                    code_match = re.search(r'<Code>(.*?)</Code>', match.group(1), re.DOTALL)
                    if file_path_match and code_match:
                        updated_files.append(CodeFile(
                            nodeId=self.node_id,
                            filePath=file_path_match.group(1).strip(),
                            code=code_match.group(1).strip(),
                            programmingLanguage=language
                        ))

            # Parse deleted code files
            deleted_code_files_match = re.search(r'<DeletedCodeFiles>(.*?)</DeletedCodeFiles>', response, re.DOTALL)
            if deleted_code_files_match:
                code_file_matches = re.finditer(r'<CodeFile>(.*?)</CodeFile>', deleted_code_files_match.group(1), re.DOTALL)
                for match in code_file_matches:
                    file_path_match = re.search(r'<FilePath>(.*?)</FilePath>', match.group(1), re.DOTALL)
                    code_match = re.search(r'<Code>(.*?)</Code>', match.group(1), re.DOTALL)
                    if file_path_match and code_match:
                        deleted_files.append(CodeFile(
                            nodeId=self.node_id,
                            filePath=file_path_match.group(1).strip(),
                            code=code_match.group(1).strip(),
                            programmingLanguage=language
                        ))

            # Log if no files were found
            if not (added_files or updated_files or deleted_files):
                logger.warning(f"No code files found in XML tags for {language}")

            print("Reasoning steps:")
            for step in reasoning_steps:
                print(step.reason)
            
            return CodeParserResponse(
                addedFiles=added_files,
                updatedFiles=updated_files,
                deletedFiles=deleted_files,
                reasoningSteps=reasoning_steps
            )
            
        except Exception as e:
            logger.error(f"Error parsing response for {language}: {str(e)}")
            raise ValueError(f"Failed to parse response: {str(e)}") 