from typing import Dict, Any, List
from ..base_parser import BaseParser

from specs.data_model_spec import (
    DataModelNodeSpec,
    Attribute,
    Relationship,
    RelationshipType
)

class DataModelParser(BaseParser[DataModelNodeSpec]):
    @staticmethod
    def parse_attribute(attr_data: Dict[str, Any]) -> Attribute:
        return Attribute(
            name=attr_data["name"],
            type=attr_data["type"],
            required=BaseParser.parse_boolean(BaseParser.parse_optional_field(attr_data, "required", True))
        )

    @staticmethod
    def parse_relationship(rel_data: Dict[str, Any]) -> Relationship:
        return Relationship(
            target_model=rel_data["targetModel"],
            relationship_type=RelationshipType(rel_data["relationshipType"])
        )

    @staticmethod
    def parse(spec_data: Dict[str, Any]) -> DataModelNodeSpec:
        attributes = [
            DataModelParser.parse_attribute(attr)
            for attr in spec_data["attributes"]
        ]
        
        relationships = [
            DataModelParser.parse_relationship(rel)
            for rel in BaseParser.parse_optional_field(spec_data, "relationships", [])
        ]
        
        return DataModelNodeSpec(
            model_name=spec_data["modelName"],
            attributes=attributes,
            relationships=relationships
        ) 