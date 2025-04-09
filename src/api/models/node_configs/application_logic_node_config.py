from typing import List, Dict
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
    function_name: str
    description: str
    inputs: List[FunctionInput]
    outputs: List[FunctionOutput]
    depends_on: List[str]


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ApplicationLogicNodeConfig:
    class_name: str
    private_attributes: List[Dict[str, str]]
    public_attributes: List[Dict[str, str]]
    private_functions: List[ApplicationLogicFunctionSpec]
    public_functions: List[ApplicationLogicFunctionSpec] 