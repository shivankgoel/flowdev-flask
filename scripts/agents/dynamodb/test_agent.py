#!/usr/bin/env python3

import os
import sys
import argparse
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(project_root)

from specs.dynamodb_spec import DynamoDBTableSpec, DynamoDBAttribute
from specs.flow_canvas_spec import ProgrammingLanguage
from spec_agents.dynamodb_agent import DynamoDBAgent
from inference import InferenceClient

class AttributeType(Enum):
    """Supported DynamoDB attribute types."""
    STRING = "String"
    NUMBER = "Number"
    BINARY = "Binary"
    BOOLEAN = "Boolean"
    NULL = "Null"
    LIST = "List"
    MAP = "Map"
    STRING_SET = "StringSet"
    NUMBER_SET = "NumberSet"
    BINARY_SET = "BinarySet"

@dataclass
class TestConfig:
    """Configuration for testing the DynamoDB agent."""
    table_name: str
    primary_key: str
    attributes: List[DynamoDBAttribute]
    programming_language: ProgrammingLanguage
    max_retries: int = 3
    retry_delay: float = 1.0
    observation_callback: Optional[callable] = None

def create_dynamodb_spec(config: TestConfig) -> DynamoDBTableSpec:
    """Create a DynamoDBTableSpec from the test configuration."""
    return DynamoDBTableSpec(
        table_name=config.table_name,
        primary_key=config.primary_key,
        attributes=config.attributes
    )

def observation_callback(observation):
    """Callback function to print observations during code generation."""
    print(f"\n[Step: {observation.step.value}]")
    print(f"Time: {observation.timestamp}")
    print("Details:")
    for key, value in observation.details.items():
        print(f"  {key}: {value}")
    if observation.error:
        print(f"Error: {observation.error}")

def parse_attributes(attributes_str: str) -> List[DynamoDBAttribute]:
    """Parse attribute string into list of DynamoDBAttribute objects."""
    attributes = []
    for attr_str in attributes_str.split(','):
        name, type_str = attr_str.split(':')
        try:
            attr_type = AttributeType[type_str.upper()]
        except KeyError:
            print(f"Error: Invalid attribute type '{type_str}'. Must be one of: {', '.join(attr.name for attr in AttributeType)}")
            sys.exit(1)
        attributes.append(DynamoDBAttribute(name=name.strip(), type=attr_type.value))
    return attributes

def main():
    parser = argparse.ArgumentParser(description='Test DynamoDB Agent')
    parser.add_argument('--table-name', required=True, help='Name of the DynamoDB table')
    parser.add_argument('--primary-key', required=True, help='Name of the primary key')
    parser.add_argument('--attributes', required=True, help='Comma-separated list of attributes in format "name:type"')
    parser.add_argument('--language', required=True, choices=['java', 'python', 'typescript'], help='Programming language')
    parser.add_argument('--max-retries', type=int, default=3, help='Maximum number of retries')
    parser.add_argument('--retry-delay', type=float, default=1.0, help='Delay between retries in seconds')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')

    args = parser.parse_args()

    # Create test configuration
    config = TestConfig(
        table_name=args.table_name,
        primary_key=args.primary_key,
        attributes=parse_attributes(args.attributes),
        programming_language=ProgrammingLanguage(args.language),
        max_retries=args.max_retries,
        retry_delay=args.retry_delay,
        observation_callback=observation_callback if args.verbose else None
    )

    # Create DynamoDB spec
    spec = create_dynamodb_spec(config)

    # Initialize inference client and agent
    inference_client = InferenceClient()  # You'll need to implement this
    agent = DynamoDBAgent(
        inference_client=inference_client,
        max_retries=config.max_retries,
        retry_delay=config.retry_delay,
        observation_callback=config.observation_callback
    )

    try:
        # Generate code
        print(f"\nGenerating DynamoDB code for table '{spec.table_name}' in {config.programming_language.value}...")
        code = agent.generate_code(spec, [], config.programming_language)
        
        # Print generated code
        print("\nGenerated Code:")
        print("-" * 80)
        print(code)
        print("-" * 80)

        # Print execution summary
        print("\nExecution Summary:")
        print(agent.get_observation_summary())

    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 