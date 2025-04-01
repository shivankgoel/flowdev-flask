import re
import logging
from .models.parser_models import ParsedCode

logger = logging.getLogger(__name__)

class DynamoDBParser:
    """Parser for DynamoDB code generation responses."""
    
    def parse(self, response: str, language: str) -> ParsedCode:
        """Extract code from XML tags in the response."""
        try:
            # First try to find complete code within XML tags
            match = re.search(r'<generated_code>(.*?)</generated_code>', response, re.DOTALL)
            if match:
                code = match.group(1).strip()
                logger.debug(f"Successfully parsed code from XML tags for {language}")
                return ParsedCode(code=code, language=language)
            
            # If no complete match, try to find code after opening tag
            # This handles cases where the LLM cut off before the closing tag
            match = re.search(r'<generated_code>(.*)', response, re.DOTALL)
            if match:
                code = match.group(1).strip()
                logger.debug(f"Successfully parsed code from partial XML tags for {language}")
                return ParsedCode(code=code, language=language)
                
            logger.error(f"No code found in XML tags for {language}")
            raise ValueError("No code found in XML tags")
            
        except Exception as e:
            logger.error(f"Error parsing code for {language}: {str(e)}")
            raise ValueError(f"Failed to parse code: {str(e)}") 