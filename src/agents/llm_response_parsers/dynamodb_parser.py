import re
import logging
from ..models.parser_models import ParsedResponse

logger = logging.getLogger(__name__)

class DynamoDBParser:
    """Parser for DynamoDB code generation responses."""
    
    def parse(self, response: str, language: str) -> ParsedResponse:
        """Extract code, thoughts, and response from XML tags."""
        try:
            # Extract code
            code_match = re.search(r'<generated_code>(.*?)</generated_code>', response, re.DOTALL)
            if not code_match:
                logger.error(f"No code found in XML tags for {language}")
                raise ValueError("No code found in XML tags")
            code = code_match.group(1).strip()
            
            # Extract thoughts
            thoughts_match = re.search(r'<assistant_thoughts>(.*?)</assistant_thoughts>', response, re.DOTALL)
            thoughts = thoughts_match.group(1).strip() if thoughts_match else ""
            
            # Extract response
            response_match = re.search(r'<assistant_response>(.*?)</assistant_response>', response, re.DOTALL)
            response_text = response_match.group(1).strip() if response_match else ""
            
            logger.debug(f"Successfully parsed response for {language}")
            return ParsedResponse(
                code=code,
                code_language=language,
                response=response_text,
                thoughts=thoughts,
                error=""
            )
            
        except Exception as e:
            logger.error(f"Error parsing response for {language}: {str(e)}")
            raise ValueError(f"Failed to parse response: {str(e)}") 