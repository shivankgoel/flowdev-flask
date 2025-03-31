from typing import Dict, Any
from ..base_parser import BaseParser

from specs.api_endpoint_spec import (
    ApiEndpointSpec,
    ApiEndpointType
)

class ApiEndpointParser(BaseParser[ApiEndpointSpec]):
    @staticmethod
    def parse(spec_data: Dict[str, Any]) -> ApiEndpointSpec:
        return ApiEndpointSpec(
            path=spec_data["path"],
            method=spec_data["method"],
            required_query_params=spec_data["requiredQueryParams"],
            optional_query_params=spec_data["optionalQueryParams"],
            endpoint_type=ApiEndpointType(spec_data["endpointType"]),
            description=BaseParser.parse_optional_field(spec_data, "description")
        ) 