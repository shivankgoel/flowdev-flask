from typing import List, Optional
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from enum import Enum


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class OrchestratorNodeType(str, Enum):
    APPLICATION_LOGIC = 'applicationLogic'
    DATA_MODEL = 'dataModel'
    API_ENDPOINT = 'apiEndpoint'


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ComposedNode:
    nodeId: str
    nodeType: OrchestratorNodeType
    label: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ApplicationOrchestratorNodeConfig:
    className: str
    composedOf: List[ComposedNode]
    description: Optional[str] = None 