from typing import List, Optional
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from enum import Enum


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DynamoDBAttributeType(str, Enum):
    STRING = "String"
    NUMBER = "Number"

    def __str__(self):
        return self.value

    def __json__(self):
        return self.value


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DynamoDBBillingMode(str, Enum):
    PAY_PER_REQUEST = "PAY_PER_REQUEST"
    PROVISIONED = "PROVISIONED"

    def __str__(self):
        return self.value

    def __json__(self):
        return self.value


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DynamoDBAttributeConfig:
    name: str
    type: DynamoDBAttributeType

    @classmethod
    def from_json(cls, json_str: str) -> 'DynamoDBAttributeConfig':
        import json
        data = json.loads(json_str)
        if isinstance(data.get('type'), dict) and not data['type']:
            # If type is an empty object, set a default value
            data['type'] = 'String'  # Default to String if empty
        return cls.from_dict(data)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DynamoDBInfraConfig:
    billingMode: DynamoDBBillingMode
    encryption: bool

    @classmethod
    def from_json(cls, json_str: str) -> 'DynamoDBInfraConfig':
        import json
        data = json.loads(json_str)
        if isinstance(data.get('billingMode'), dict) and not data['billingMode']:
            # If billingMode is an empty object, set a default value
            data['billingMode'] = 'PAY_PER_REQUEST'  # Default to PAY_PER_REQUEST if empty
        return cls.from_dict(data)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DynamoDbNodeConfig:
    name: str
    attributes: List[DynamoDBAttributeConfig]
    hashKey: str
    rangeKey: Optional[str] = None
    infraSpec: Optional[DynamoDBInfraConfig] = None 