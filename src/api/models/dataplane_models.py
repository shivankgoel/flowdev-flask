from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from typing import Optional, Dict, Any, List

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ProgrammingLanguage:
    name: str
    version: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class GenerateCodeRequest:
    canvasId: str
    canvasVersion: str
    nodeId: str
    programmingLanguage: ProgrammingLanguage

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CodeFile:
    nodeId: str
    filePath: str
    code: str
    programmingLanguage: ProgrammingLanguage

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class GenerateCodeResponse:
    files: List[CodeFile]
