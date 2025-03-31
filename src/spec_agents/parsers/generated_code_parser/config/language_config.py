from dataclasses import dataclass
from typing import Dict, List

@dataclass
class LanguageConfig:
    """Configuration for language-specific parsing rules."""
    import_patterns: List[str]
    class_pattern: str
    type_hint_pattern: str
    import_validation_pattern: str
    indentation_validation: bool

# Language-specific configurations
PYTHON_CONFIG = LanguageConfig(
    import_patterns=[
        r'^import\s+([^#\n]+)$',
        r'^from\s+([^#\n]+)\s+import\s+([^#\n]+)$'
    ],
    class_pattern=r'^class\s+(\w+)\s*\(?([^)]*)\)?\s*:',
    type_hint_pattern=r':\s*([^=]+)\s*=\s*',
    import_validation_pattern=r'^[a-zA-Z][a-zA-Z0-9_.]*$',
    indentation_validation=True
)

TYPESCRIPT_CONFIG = LanguageConfig(
    import_patterns=[
        r'^import\s+([^;]+);$',
        r'^import\s+{\s*([^}]+)\s*}\s+from\s+[\'"]([^\'"]+)[\'"];$'
    ],
    class_pattern=r'^class\s+(\w+)\s*{?',
    type_hint_pattern=r':\s*([^=]+)\s*=\s*',
    import_validation_pattern=r'^[a-zA-Z][a-zA-Z0-9_.]*$',
    indentation_validation=True
)

JAVA_CONFIG = LanguageConfig(
    import_patterns=[
        r'^package\s+([^;]+);$',
        r'^import\s+([^;]+);$',
        r'^import\s+static\s+([^;]+);$'
    ],
    class_pattern=r'^public\s+class\s+(\w+)\s*(?:extends\s+(\w+))?\s*(?:implements\s+([^;{]+))?\s*{?',
    type_hint_pattern=r'([^=]+)\s*=\s*',
    import_validation_pattern=r'^[a-zA-Z][a-zA-Z0-9_.]*$',
    indentation_validation=True
)

# Configuration mapping
LANGUAGE_CONFIGS: Dict[str, LanguageConfig] = {
    'python': PYTHON_CONFIG,
    'typescript': TYPESCRIPT_CONFIG,
    'java': JAVA_CONFIG
} 