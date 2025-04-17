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
    targetModel: str
    relationshipType: RelationshipType


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DataModelNodeConfig:
    modelName: str
    attributes: List[Attribute]
    relationships: Optional[List[Relationship]] = None
    validationRules: Optional[List[str]] = None 