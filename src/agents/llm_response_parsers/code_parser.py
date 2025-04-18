import re
import logging
from ..models.parser_models import CodeFile
from src.api.models.dataplane_models import ProgrammingLanguage
from src.agents.models.parser_models import CodeParserResponse
logger = logging.getLogger(__name__)

class CodeParser:
    """Parser for code generation responses."""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
    
    def parse(self, response: str, language: ProgrammingLanguage) -> CodeParserResponse:
        """Extract code files and thoughts from XML tags."""
        try:
            # Extract all code files
            code_files = []
            all_code_files_match = re.search(r'<AllCodeFiles>(.*?)</AllCodeFiles>', response, re.DOTALL)
            if all_code_files_match:
                code_file_matches = re.finditer(r'<CodeFile>(.*?)</CodeFile>', all_code_files_match.group(1), re.DOTALL)
                for match in code_file_matches:
                    file_path_match = re.search(r'<FilePath>(.*?)</FilePath>', match.group(1), re.DOTALL)
                    code_match = re.search(r'<Code>(.*?)</Code>', match.group(1), re.DOTALL)
                    if file_path_match and code_match:
                        code_files.append(CodeFile(
                            nodeId=self.node_id,
                            filePath=file_path_match.group(1).strip(),
                            code=code_match.group(1).strip(),
                            programmingLanguage=language
                        ))
            
            if not code_files:
                logger.error(f"No code files found in XML tags for {language}")
                return CodeParserResponse(files=[])
                
            return CodeParserResponse(files=code_files)
            
        except Exception as e:
            logger.error(f"Error parsing response for {language}: {str(e)}")
            raise ValueError(f"Failed to parse response: {str(e)}") 