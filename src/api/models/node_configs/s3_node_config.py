from typing import List
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class S3BucketDirectory:
    path: str
    description: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class S3BucketNodeConfig:
    directories: List[S3BucketDirectory]