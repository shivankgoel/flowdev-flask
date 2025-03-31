from dataclasses import dataclass
from typing import List, Optional, Union
from enum import Enum
from .dynamodb_spec import DynamoDBTableSpec
from .s3_spec import S3BucketSpec
from .application_logic_spec import ApplicationLogicSpec

@dataclass
class CanvasPosition:
    x: float
    y: float

@dataclass
class NodeDataSpec:
    spec: Union[DynamoDBTableSpec, S3BucketSpec, ApplicationLogicSpec]

@dataclass
class CanvasNodeSpec:
    id: str
    type: str
    position: CanvasPosition
    data: NodeDataSpec

@dataclass
class EdgeDataSpec:
    label: Optional[str] = None

@dataclass
class CanvasEdgeSpec:
    id: str
    source: str
    target: str
    arrow_head_type: str
    data: EdgeDataSpec

class ProgrammingLanguage(str, Enum):
    PYTHON = 'python'
    JAVA = 'java'
    TYPESCRIPT = 'typescript'

@dataclass
class CanvasDefinitionSpec:
    canvas_id: str
    nodes: List[CanvasNodeSpec]
    edges: List[CanvasEdgeSpec]
    version: str
    created_at: str
    updated_at: str
    programming_language: ProgrammingLanguage 