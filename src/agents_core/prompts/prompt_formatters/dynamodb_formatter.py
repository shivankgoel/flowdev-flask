from typing import Dict, Any
from src.specs.dynamodb_spec import DynamoDBTableSpec
from ..dynamodb_prompts import PROMPTS

class DynamoDBPromptFormatter:
    """Formatter for DynamoDB prompts."""
    
    def format_prompt(self, spec: DynamoDBTableSpec, language: str) -> str:
        """Format the prompt with table specifications."""
        if not isinstance(spec, DynamoDBTableSpec):
            raise ValueError("Invalid spec type")

        # Get language-specific prompt template
        prompt_template = PROMPTS.get(language.lower())
        if not prompt_template:
            raise ValueError(f"Unsupported language: {language}")

        # Format attributes section
        attributes_section = "\n".join(
            f"- {attr.name}: {str(attr.type)}"
            for attr in spec.attributes
        )

        # Format range key section
        range_key_section = f"Range Key: {spec.range_key}" if spec.range_key else ""

        # Format infrastructure section
        infra_section = ""
        if spec.infra_spec:
            infra_section = f"""
Infrastructure:
- Billing Mode: {str(spec.infra_spec.billing_mode)}
- Encryption: {spec.infra_spec.encryption}"""

        return prompt_template.format(
            name=spec.name,
            hash_key=spec.hash_key,
            range_key_section=range_key_section,
            attributes_section=attributes_section,
            infra_section=infra_section
        ) 