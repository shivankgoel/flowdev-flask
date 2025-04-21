from typing import List, Literal
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ApiEndpoint:
    path: str
    method: Literal['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
    description: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AuthServiceNodeConfig:
    apiEndpoints: List[ApiEndpoint]