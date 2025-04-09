from typing import List, Optional
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from enum import Enum


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class S3EncryptionType(str, Enum):
    NONE = 'NONE'
    AES256 = 'AES256'
    AWS_KMS = 'AWS_KMS'


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class S3StorageClass(str, Enum):
    STANDARD = 'STANDARD'
    INTELLIGENT_TIERING = 'INTELLIGENT_TIERING'
    STANDARD_IA = 'STANDARD_IA'
    GLACIER = 'GLACIER'
    DEEP_ARCHIVE = 'DEEP_ARCHIVE'


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class S3InfraConfig:
    versioning: bool
    encryption: S3EncryptionType
    storage_class: S3StorageClass
    lifecycle_rules: Optional[List[str]] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class S3BucketNodeConfig:
    name: str
    infra_spec: S3InfraConfig
    file_path_prefix: Optional[str] = None
    description: Optional[str] = None