from typing import Dict, Any, TypeVar, Generic, Optional, List, Union
from dataclasses import dataclass

T = TypeVar('T')

class BaseParser(Generic[T]):
    @staticmethod
    def parse_optional_field(data: Dict[str, Any], field: str, default: Any = None) -> Any:
        """Helper method to parse optional fields from JSON data."""
        return data.get(field, default)

    @staticmethod
    def parse_required_field(data: Dict[str, Any], field: str) -> Any:
        """Helper method to parse required fields from JSON data."""
        if field not in data:
            raise ValueError(f"Required field '{field}' not found in data")
        return data[field]

    @staticmethod
    def parse_list(data: Dict[str, Any], field: str, parser_func, default: list = None) -> list:
        """Helper method to parse list fields from JSON data."""
        if default is None:
            default = []
        return [parser_func(item) for item in data.get(field, default)]

    @staticmethod
    def parse_boolean(value: Any) -> bool:
        """Handle both JavaScript and Python boolean values"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() == 'true'
        return bool(value) 