from typing import Dict, Any, List
from ..base_parser import BaseParser

from specs.s3_spec import (
    S3BucketSpec,
    S3InfraSpec,
    S3EncryptionType,
    S3StorageClass
)

class S3Parser(BaseParser[S3BucketSpec]):
    @staticmethod
    def parse_infra_spec(data: Dict[str, Any]) -> S3InfraSpec:
        return S3InfraSpec(
            encryption=S3EncryptionType(data["encryption"]),
            storage_class=S3StorageClass(data["storage_class"]),
            versioning=BaseParser.parse_boolean(data["versioning"]),
            lifecycle_rules=BaseParser.parse_optional_field(data, "lifecycle_rules", default=[])
        )

    @staticmethod
    def parse(spec_data: Dict[str, Any]) -> S3BucketSpec:
        return S3BucketSpec(
            name=BaseParser.parse_required_field(spec_data, "name"),
            infra_spec=S3Parser.parse_infra_spec(spec_data["infra_spec"]),
            file_path_prefix=BaseParser.parse_optional_field(spec_data, "file_path_prefix"),
            description=BaseParser.parse_optional_field(spec_data, "description")
        ) 