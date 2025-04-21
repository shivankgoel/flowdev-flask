from dataclasses import dataclass
from typing import List
from src.api.models.dataplane_models import CodeFile


@dataclass
class ReasoningStep:
    reason: str


@dataclass
class CodeParserResponse:
    addedFiles: List[CodeFile]
    updatedFiles: List[CodeFile]
    deletedFiles: List[CodeFile]
    reasoningSteps: List[ReasoningStep]