import re
from .models.parser_models import ParsedCode

class DynamoDBParser:
    """Parser for DynamoDB code generation responses."""
    
    def parse(self, response: str, language: str) -> ParsedCode:
        """Extract code from XML tags in the response."""
        match = re.search(r'<generated_code>(.*?)</generated_code>', response, re.DOTALL)
        if not match:
            raise ValueError("No code found in XML tags")
            
        code = match.group(1).strip()
        return ParsedCode(code=code, language=language) 