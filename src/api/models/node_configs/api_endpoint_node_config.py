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
    api_key_location: Optional[ApiKeyLocation] = None
    oauth_flow: Optional[str] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RequestBody:
    description: Optional[str] = None
    schema: Dict[str, Union[str, int, bool, object]] = None
    content_type: Optional[ContentType] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ResponseBody:
    status_code: int
    body: Dict[str, Union[str, int, bool, object]]
    content_type: Optional[ContentType] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ApiEndpointNodeConfig:
    path: str
    method: Literal['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
    required_query_params: List[str]
    optional_query_params: List[str]
    content_type: Optional[ContentType] = None
    request_body: Optional[RequestBody] = None
    headers: Optional[Dict[str, str]] = None
    response_body: Optional[ResponseBody] = None
    authentication_config: Optional[AuthenticationConfig] = None
    description: Optional[str] = None
    endpoint_type: ApiEndpointType = ApiEndpointType.NON_STREAMING 