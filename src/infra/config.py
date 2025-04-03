from dataclasses import dataclass
from typing import Optional
from enum import Enum

class BillingMode(str, Enum):
    PROVISIONED = "PROVISIONED"
    PAY_PER_REQUEST = "PAY_PER_REQUEST"

@dataclass
class DynamoDBConfig:
    region: str = "us-east-1"
    endpoint_url: str = None  # For local development
    billing_mode: BillingMode = BillingMode.PAY_PER_REQUEST
    # These are only used if billing_mode is PROVISIONED
    read_capacity_units: int = 5
    write_capacity_units: int = 5

@dataclass
class S3Config:
    region: str = "us-east-1"
    endpoint_url: str = None  # For local development
    bucket_name: str = "flow-canvas-data"
    # Prefixes for different types of data
    canvas_prefix: str = "canvases/"
    node_prefix: str = "nodes/"
    edge_prefix: str = "edges/"
    chat_prefix: str = "chats/"

@dataclass
class InfrastructureConfig:
    dynamodb: DynamoDBConfig 