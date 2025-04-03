import boto3
from typing import Any
from src.infra.config import DynamoDBConfig

class DynamoDBClientFactory:
    def __init__(self, config: DynamoDBConfig):
        self.config = config
        self._resource = None
        self._client = None

    @property
    def resource(self) -> Any:
        if self._resource is None:
            self._resource = boto3.resource(
                'dynamodb',
                region_name=self.config.region,
                endpoint_url=self.config.endpoint_url
            )
        return self._resource

    @property
    def client(self) -> Any:
        if self._client is None:
            self._client = boto3.client(
                'dynamodb',
                region_name=self.config.region,
                endpoint_url=self.config.endpoint_url
            )
        return self._client 