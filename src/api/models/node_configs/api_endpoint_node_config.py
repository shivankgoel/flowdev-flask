from typing import Dict, List, Optional, Union, Literal
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from enum import Enum


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ApiEndpointType(str, Enum):
    NON_STREAMING = 'non-streaming'
    STREAMING_SSE = 'streaming-sse'
    BI_DIRECTIONAL_STREAMING = 'bi-directional-streaming'
    LONG_POLLING = 'long-polling'
    GRAPHQL_SUBSCRIPTION = 'graphql-subscription'


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AuthType(str, Enum):
    API_KEY = 'API_KEY'
    OAUTH = 'OAuth'
    NONE = 'None'


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ApiKeyLocation(str, Enum):
    HEADER = 'header'
    QUERY = 'query'


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ContentType(str, Enum):
    JSON = 'application/json'
    XML = 'application/xml'
    TEXT = 'text/plain'
    MULTIPART = 'multipart/form-data'


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AuthenticationConfig:
    type: AuthType
    description: Optional[str] = None
    apiKeyLocation: Optional[ApiKeyLocation] = None
    oauthFlow: Optional[str] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RequestBody:
    description: Optional[str] = None
    schema: Dict[str, Union[str, int, bool, object]] = None
    contentType: Optional[ContentType] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ResponseBody:
    statusCode: int
    body: Dict[str, Union[str, int, bool, object]]
    contentType: Optional[ContentType] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ApiEndpointNodeConfig:
    path: str
    method: Literal['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
    requiredQueryParams: List[str]
    optionalQueryParams: List[str]
    contentType: Optional[ContentType] = None
    requestBody: Optional[RequestBody] = None
    headers: Optional[Dict[str, str]] = None
    responseBody: Optional[ResponseBody] = None
    authenticationConfig: Optional[AuthenticationConfig] = None
    description: Optional[str] = None
    endpointType: ApiEndpointType = ApiEndpointType.NON_STREAMING 