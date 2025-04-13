from dataclasses import dataclass
from typing import List
from src.api.models.dataplane_models import CodeFile


@dataclass
class CodeParserResponse:
    files: List[CodeFile]