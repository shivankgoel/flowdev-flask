from dataclasses import dataclass
from dataclasses_json import LetterCase, dataclass_json
from typing import List, Optional
from src.api.models.canvas_models import CanvasNode, CanvasEdge
from src.api.models.dataplane_models import CodeFile

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CanvasDO:
    """Canvas metadata stored in DynamoDB."""
    canvas_name: str
    customer_id: str
    canvas_id: str
    canvas_version: str
    created_at: str
    updated_at: str
    canvas_definition_s3_uri: Optional[str] = None  # S3 URI pointing to the canvas definition
    canvas_code_s3_uri: Optional[str] = None  # S3 URI pointing to the canvas code


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CanvasDefinitionDO:
    """Canvas definition stored in S3."""
    nodes: List[CanvasNode]
    edges: List[CanvasEdge]


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CodeDO:
    """Code stored in S3."""
    files: List[CodeFile]