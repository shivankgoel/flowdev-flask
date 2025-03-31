from dataclasses import dataclass
from typing import Dict, List, Optional, Union, Literal
from enum import Enum

class ApiEndpointType(str, Enum):
    NON_STREAMING = 'non-streaming'
    STREAMING_SSE = 'streaming-sse'
    BI_DIRECTIONAL_STREAMING = 'bi-directional-streaming'
    LONG_POLLING = 'long-polling'
    GRAPHQL_SUBSCRIPTION = 'graphql-subscription'

class AuthType(str, Enum):
    API_KEY = 'API_KEY'
    OAUTH = 'OAuth'
    NONE = 'None'

class ApiKeyLocation(str, Enum):
    HEADER = 'header'
    QUERY = 'query'

class ContentType(str, Enum):
    JSON = 'application/json'
    XML = 'application/xml'
    TEXT = 'text/plain'
    MULTIPART = 'multipart/form-data'

@dataclass
class AuthenticationConfig:
    type: AuthType
    description: Optional[str] = None
    api_key_location: Optional[ApiKeyLocation] = None
    oauth_flow: Optional[str] = None

@dataclass
class RequestBody:
    description: Optional[str] = None
    schema: Dict[str, Union[str, int, bool, object]] = None
    content_type: Optional[ContentType] = None

@dataclass
class ResponseBody:
    status_code: int
    body: Dict[str, Union[str, int, bool, object]]
    content_type: Optional[ContentType] = None

@dataclass
class ApiEndpointSpec:
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