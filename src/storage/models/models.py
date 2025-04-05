from dataclasses import dataclass
from dataclasses_json import LetterCase, dataclass_json
from typing import Dict, Any, Optional, Union
from src.specs.api_endpoint_spec import ApiEndpointSpec
from src.specs.application_logic_spec import ApplicationLogicSpec
from src.specs.application_orchestrator_spec import ApplicationOrchestratorSpec
from src.specs.data_model_spec import DataModelNodeSpec
from src.specs.dynamodb_spec import DynamoDBTableSpec
from src.specs.s3_spec import S3BucketSpec
from src.specs.flow_canvas_spec import CanvasPosition

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CanvasDO:
    """Canvas metadata stored in DynamoDB."""
    canvas_name: str
    customer_id: str
    canvas_id: str
    canvas_version: str
    created_at: str
    updated_at: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CanvasNodeDO:
    """Essential node metadata stored in DynamoDB."""
    customer_id: str
    canvas_id: str
    node_id: str
    canvas_version: str
    type: str
    position: CanvasPosition
    # References to data in S3
    application_code_s3_uris: Optional[Dict[str, str]] = None  # language -> s3_uri
    infra_code_s3_uris: Optional[Dict[str, str]] = None  # language -> s3_uri
    # Node-specific data stored directly in DynamoDB
    data: Optional[Union[
        DynamoDBTableSpec,
        S3BucketSpec,
        ApplicationLogicSpec,
        DataModelNodeSpec,
        ApiEndpointSpec,
        ApplicationOrchestratorSpec
    ]] = None
    # Quick access metadata
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None  # Custom metadata key-value pairs
