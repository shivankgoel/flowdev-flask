import json
from enum import Enum
from dataclasses import dataclass, is_dataclass
from typing import Any

class EnumEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, Enum):
            return obj.value
        if is_dataclass(obj):
            return obj.__dict__
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        return super().default(obj) 