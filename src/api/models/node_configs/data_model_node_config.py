from typing import List, Optional
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from enum import Enum


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RelationshipType(str, Enum):
    ONE_TO_ONE = 'one-to-one'
    ONE_TO_MANY = 'one-to-many'
    MANY_TO_MANY = 'many-to-many'


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Attribute:
    name: str
    type: str
    required: Optional[bool] = False


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Relationship:
    target_model: str
    relationship_type: RelationshipType


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DataModelNodeConfig:
    model_name: str
    attributes: List[Attribute]
    relationships: Optional[List[Relationship]] = None
    validation_rules: Optional[List[str]] = None 