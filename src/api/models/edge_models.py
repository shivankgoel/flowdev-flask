from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from enum import Enum

class CanvasEdgeType(str, Enum):
    COMPOSITION = "composition"

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CanvasEdge:
    edgeType: CanvasEdgeType
    source: str
    target: str