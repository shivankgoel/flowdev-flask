from typing import Dict, Any, List
from ..base_parser import BaseParser

from specs.dynamodb_spec import (
    DynamoDBTableSpec,
    DynamoDBAttribute,
    DynamoDBAttributeType,
    DynamoDBInfraSpec,
    DynamoDBBillingMode
)

class DynamoDBParser(BaseParser[DynamoDBTableSpec]):
    @staticmethod
    def parse_attribute(attr_data: Dict[str, Any]) -> DynamoDBAttribute:
        return DynamoDBAttribute(
            name=BaseParser.parse_required_field(attr_data, "name"),
            type=DynamoDBAttributeType(attr_data["type"])
        )

    @staticmethod
    def parse_infra_spec(data: Dict[str, Any]) -> DynamoDBInfraSpec:
        return DynamoDBInfraSpec(
            billing_mode=DynamoDBBillingMode(data["billing_mode"]),
            encryption=BaseParser.parse_boolean(data["encryption"])
        )

    @staticmethod
    def parse(spec_data: Dict[str, Any]) -> DynamoDBTableSpec:
        return DynamoDBTableSpec(
            name=BaseParser.parse_required_field(spec_data, "name"),
            attributes=BaseParser.parse_list(spec_data, "attributes", DynamoDBParser.parse_attribute),
            hash_key=BaseParser.parse_required_field(spec_data, "hash_key"),
            range_key=BaseParser.parse_required_field(spec_data, "range_key"),
            infra_spec=DynamoDBParser.parse_infra_spec(spec_data["infra_spec"])
        ) 