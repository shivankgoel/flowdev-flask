from dataclasses import dataclass
from typing import List, Optional, Union, Dict, Any
from enum import Enum
from dataclasses_json import dataclass_json, LetterCase
from .dynamodb_spec import DynamoDBTableSpec
from .s3_spec import S3BucketSpec
from .application_logic_spec import ApplicationLogicSpec
from .data_model_spec import DataModelNodeSpec
from .api_endpoint_spec import ApiEndpointSpec
from .application_orchestrator_spec import ApplicationOrchestratorSpec
from src.api.models.dataplane_models import ProgrammingLanguage

class MessageContentType(str, Enum):
    TEXT = 'text'

class ChatMessageRole(str, Enum):
    USER = 'user'
    ASSISTANT = 'assistant'

class EdgeType(str, Enum):
    DEPENDENCY = 'dependency'

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CanvasPosition:
    x: float
    y: float

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class EdgeDataSpec:
    label: Optional[str] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CanvasEdgeSpec:
    id: str
    source: str
    target: str
    edge_type: EdgeType
    data: Optional[EdgeDataSpec] = None

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class MessageContent:
    content_type: MessageContentType
    text: Optional[str] = None

class ChatMessageSourceType(str, Enum):
    HUMAN = "human"
    SELF = "self"
    CANVAS_NODE = "canvas_node"

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ChatMessage:
    timestamp: str
    role: ChatMessageRole
    source_type: ChatMessageSourceType
    contents: List[MessageContent]
    source_id: Optional[str] = None  # e.g., node id

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ChatThread:
    chat_thread_id: str
    messages: List[ChatMessage]
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CanvasNodeSpec:
    id: str
    type: str
    position: CanvasPosition
    data: Union[
        DynamoDBTableSpec,
        S3BucketSpec,
        ApplicationLogicSpec,
        DataModelNodeSpec,
        ApiEndpointSpec,
        ApplicationOrchestratorSpec
    ]
    application_code: Optional[Dict[ProgrammingLanguage, str]] = None
    infra_code: Optional[Dict[ProgrammingLanguage, str]] = None
    metadata: Optional[Dict[str, str]] = None
    chat_threads: Optional[List[ChatThread]] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CanvasDefinition:
    customer_id: str
    canvas_id: str
    canvas_version: str
    nodes: List[CanvasNodeSpec]
    edges: List[CanvasEdgeSpec]
    created_at: str
    updated_at: str
