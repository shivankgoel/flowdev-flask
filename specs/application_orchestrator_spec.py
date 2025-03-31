from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class NodeType(str, Enum):
    APPLICATION_LOGIC = 'applicationLogic'
    DATA_MODEL = 'dataModel'
    API_ENDPOINT = 'apiEndpoint'

@dataclass
class ComposedNode:
    node_id: str
    node_type: NodeType
    label: str

@dataclass
class ApplicationOrchestratorSpec:
    class_name: str
    composed_of: List[ComposedNode]
    description: Optional[str] = None 