from typing import List, Dict, Optional
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class FunctionInput:
    name: str
    type: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class FunctionOutput:
    name: str
    type: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ApplicationLogicFunctionSpec:
    functionName: str
    description: str
    inputs: List[FunctionInput]
    outputs: List[FunctionOutput]
    dependsOn: List[str]
    logic: Optional[str] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ApplicationLogicNodeConfig:
    className: str
    description: Optional[str] = None
    privateAttributes: List[Dict[str, str]] = None
    publicAttributes: List[Dict[str, str]] = None
    privateFunctions: List[ApplicationLogicFunctionSpec] = None
    publicFunctions: List[ApplicationLogicFunctionSpec] = None
    
    def __post_init__(self):
        if self.privateAttributes is None:
            self.privateAttributes = []
        if self.publicAttributes is None:
            self.publicAttributes = []
        if self.privateFunctions is None:
            self.privateFunctions = []
        if self.publicFunctions is None:
            self.publicFunctions = [] 