from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class DynamoDBAttributeType(str, Enum):
    STRING = "String"
    NUMBER = "Number"

class DynamoDBBillingMode(str, Enum):
    PAY_PER_REQUEST = "PAY_PER_REQUEST"
    PROVISIONED = "PROVISIONED"

@dataclass
class DynamoDBAttribute:
    name: str
    type: DynamoDBAttributeType

@dataclass
class DynamoDBInfraSpec:
    billing_mode: DynamoDBBillingMode
    encryption: bool

@dataclass
class DynamoDBTableSpec:
    name: str
    attributes: List[DynamoDBAttribute]
    hash_key: str
    range_key: Optional[str] = None
    infra_spec: Optional[DynamoDBInfraSpec] = None 