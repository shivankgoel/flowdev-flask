from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class FunctionInput:
    name: str
    type: str

@dataclass
class FunctionOutput:
    name: str
    type: str

@dataclass
class ApplicationLogicFunctionSpec:
    function_name: str
    description: str
    inputs: List[FunctionInput]
    outputs: List[FunctionOutput]
    depends_on: List[str]

@dataclass
class ApplicationLogicSpec:
    class_name: str
    private_attributes: List[Dict[str, str]]
    public_attributes: List[Dict[str, str]]
    private_functions: List[ApplicationLogicFunctionSpec]
    public_functions: List[ApplicationLogicFunctionSpec] 