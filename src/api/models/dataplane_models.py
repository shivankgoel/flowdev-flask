from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from typing import Optional, Dict, Any, List
from .node_models import CanvasNode
from .edge_models import CanvasEdge
from enum import Enum

class LanguageName(str, Enum):
    PYTHON = "Python"
    JAVA = "Java"
    TYPESCRIPT = "TypeScript"
    JAVASCRIPT = "JavaScript"
    GO = "Go"
    RUST = "Rust"
    KOTLIN = "Kotlin"
    SWIFT = "Swift"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            value = value.lower()
            for member in cls:
                if member.value.lower() == value:
                    return member
        return None

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ProgrammingLanguage:
    name: LanguageName
    version: str

    def __post_init__(self):
        if isinstance(self.name, str):
            self.name = LanguageName(self.name)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProgrammingLanguage':
        if isinstance(data, dict):
            return cls(
                name=LanguageName(data['name']),
                version=data['version']
            )
        return data

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name.value,
            'version': self.version
        }

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CodeFile:
    nodeId: str
    filePath: str
    code: str
    programmingLanguage: ProgrammingLanguage


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class GetCodeRequest:
    canvasId: str
    canvasVersion: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class GetCodeResponse:
    files: List[CodeFile]

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class GenerateCodeRequest:
    canvasId: str
    canvasVersion: str
    nodeId: str
    programmingLanguage: ProgrammingLanguage

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class GenerateCodeResponse:
    addedFiles: List[CodeFile]
    updatedFiles: List[CodeFile]
    deletedFiles: List[CodeFile]

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CodeChange:
    addedFiles: List[CodeFile]
    updatedFiles: List[CodeFile]
    deletedFiles: List[CodeFile]

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ApplyCodeChangesRequest:
    canvasId: str
    canvasVersion: str
    codeChange: CodeChange

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ApplyCodeChangesResponse:
    success: bool
