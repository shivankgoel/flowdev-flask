from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class S3EncryptionType(str, Enum):
    NONE = 'NONE'
    AES256 = 'AES256'
    AWS_KMS = 'AWS_KMS'

class S3StorageClass(str, Enum):
    STANDARD = 'STANDARD'
    INTELLIGENT_TIERING = 'INTELLIGENT_TIERING'
    STANDARD_IA = 'STANDARD_IA'
    GLACIER = 'GLACIER'
    DEEP_ARCHIVE = 'DEEP_ARCHIVE'

@dataclass
class S3InfraSpec:
    versioning: bool
    encryption: S3EncryptionType
    storage_class: S3StorageClass
    lifecycle_rules: Optional[List[str]] = None

@dataclass
class S3BucketSpec:
    name: str
    infra_spec: S3InfraSpec
    file_path_prefix: Optional[str] = None
    description: Optional[str] = None 