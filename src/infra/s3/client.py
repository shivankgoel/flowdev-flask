import boto3
from typing import Any
from src.infra.config import S3Config

class S3ClientFactory:
    def __init__(self, config: S3Config):
        self.config = config
        self._resource = None
        self._client = None

    @property
    def resource(self) -> Any:
        if self._resource is None:
            self._resource = boto3.resource(
                's3',
                region_name=self.config.region,
                endpoint_url=self.config.endpoint_url
            )
        return self._resource

    @property
    def client(self) -> Any:
        if self._client is None:
            self._client = boto3.client(
                's3',
                region_name=self.config.region,
                endpoint_url=self.config.endpoint_url
            )
        return self._client 