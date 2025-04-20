from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from typing import Optional, Dict, Any, List
from .node_models import CanvasNode
from .edge_models import CanvasEdge

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ProgrammingLanguage:
    name: str
    version: str

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
