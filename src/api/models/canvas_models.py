from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CreateCanvasRequest:
    """Request model for creating a new canvas."""
    canvas_name: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CreateCanvasResponse:
    """Canvas metadata stored in DynamoDB."""
    canvas_id: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class UpdateCanvasRequest:
    """Request model for updating a canvas."""
    canvas_id: str
    canvas_name: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class UpdateCanvasResponse:
    """Response model for canvas update."""
    canvas_id: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class GetCanvasRequest:
    """Request model for getting a canvas."""
    canvas_id: str
    canvas_version: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class GetCanvasResponse:
    """Response model for getting a canvas."""
    canvas_id: str
    canvas_version: str
    canvas_name: str
    created_at: str
    updated_at: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DeleteCanvasRequest:
    """Request model for deleting a canvas."""
    canvas_id: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DeleteCanvasResponse:
    """Canvas metadata stored in DynamoDB."""
    canvas_id: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ListCanvasRequest:
    """Request model for listing canvases."""
    pass

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ListCanvasResponseItem:
    canvas_id: str
    canvas_name: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ListCanvasResponse:
    """Response model for listing canvases."""
    canvases: List[ListCanvasResponseItem]  # List of {canvas_id, canvas_name}


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CreateCanvasVersionRequest:
    """Request model for creating a new canvas version."""
    canvas_id: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CreateCanvasVersionResponse:
    """Response model for creating a new canvas version."""
    canvas_id: str
    canvas_version: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ListCanvasVersionsRequest:
    """Request model for listing canvas versions."""
    canvas_id: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ListCanvasVersionsResponseItem:
    canvas_id: str
    canvas_version: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ListCanvasVersionsResponse:
    """Response model for listing canvas versions."""
    canvas_versions: List[ListCanvasVersionsResponseItem]  # List of {canvas_version, created_at}


