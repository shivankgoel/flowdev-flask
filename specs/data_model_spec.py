from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class RelationshipType(str, Enum):
    ONE_TO_ONE = 'one-to-one'
    ONE_TO_MANY = 'one-to-many'
    MANY_TO_MANY = 'many-to-many'

@dataclass
class Attribute:
    name: str
    type: str
    required: Optional[bool] = False

@dataclass
class Relationship:
    target_model: str
    relationship_type: RelationshipType

@dataclass
class DataModelNodeSpec:
    model_name: str
    attributes: List[Attribute]
    relationships: Optional[List[Relationship]] = None
    validation_rules: Optional[List[str]] = None 