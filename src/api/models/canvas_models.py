from typing import List, Optional
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from .node_models import CanvasNode
from .edge_models import CanvasEdge

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CreateCanvasRequest:
    """Request model for creating a new canvas."""
    canvasName: str
    nodes: Optional[List[CanvasNode]] = None
    edges: Optional[List[CanvasEdge]] = None

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CreateCanvasResponse:
    """Canvas metadata stored in DynamoDB."""
    canvasId: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class UpdateCanvasRequest:
    """Request model for updating a canvas."""
    canvasId: str
    canvasName: str
    nodes: Optional[List[CanvasNode]] = None
    edges: Optional[List[CanvasEdge]] = None

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class UpdateCanvasResponse:
    """Response model for canvas update."""
    canvasId: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class GetCanvasRequest:
    """Request model for getting a canvas."""
    canvasId: str
    canvasVersion: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class GetCanvasResponse:
    """Response model for getting a canvas."""
    canvasId: str
    canvasVersion: str
    canvasName: str
    createdAt: str
    updatedAt: str
    nodes: Optional[List[CanvasNode]] = None
    edges: Optional[List[CanvasEdge]] = None

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DeleteCanvasRequest:
    """Request model for deleting a canvas."""
    canvasId: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DeleteCanvasResponse:
    """Canvas metadata stored in DynamoDB."""
    canvasId: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ListCanvasRequest:
    """Request model for listing canvases."""
    pass

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ListCanvasResponseItem:
    canvasId: str
    canvasName: str
    canvasVersion: str
    createdAt: str
    updatedAt: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ListCanvasResponse:
    """Response model for listing canvases."""
    canvases: List[ListCanvasResponseItem]  # List of {canvasId, canvasName}

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CreateCanvasVersionRequest:
    """Request model for creating a new canvas version."""
    canvasId: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CreateCanvasVersionResponse:
    """Response model for creating a new canvas version."""
    canvasId: str
    canvasVersion: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ListCanvasVersionsRequest:
    """Request model for listing canvas versions."""
    canvasId: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ListCanvasVersionsResponseItem:
    canvasId: str
    canvasVersion: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ListCanvasVersionsResponse:
    """Response model for listing canvas versions."""
    canvasVersions: List[ListCanvasVersionsResponseItem]  # List of {canvasVersion, createdAt}


