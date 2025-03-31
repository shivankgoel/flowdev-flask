#!/usr/bin/env python3

import os
import sys
import argparse
import logging
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio
from pprint import pprint

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(project_root)

from src.specs.dynamodb_spec import DynamoDBTableSpec, DynamoDBAttribute
from src.specs.flow_canvas_spec import ProgrammingLanguage, CanvasNodeSpec, NodeDataSpec
from src.spec_agents.dynamodb_agent import DynamoDBAgent
from src.inference.openai_inference import OpenAIInference

# Configure logging
def setup_logging(verbose: bool = False):
    """Configure logging based on verbosity level."""
    level = logging.DEBUG if verbose else logging.INFO
    
    # Create formatters
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create handlers
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(project_root, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # File handler for detailed logs
    file_handler = logging.FileHandler(
        os.path.join(log_dir, 'dynamodb_agent.log')
    )
    file_handler.setFormatter(file_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    return root_logger

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
    range_key: str
    attributes: List[DynamoDBAttribute]
    programming_language: ProgrammingLanguage
    max_retries: int = 3
    retry_delay: float = 1.0

def create_dynamodb_spec(config: TestConfig) -> DynamoDBTableSpec:
    """Create a DynamoDBTableSpec from the test configuration."""
    return DynamoDBTableSpec(
        name=config.table_name,
        hash_key=config.primary_key,
        range_key=config.range_key,
        attributes=config.attributes
    )

def create_canvas_node(spec: DynamoDBTableSpec) -> CanvasNodeSpec:
    """Create a CanvasNodeSpec from the DynamoDB spec."""
    return CanvasNodeSpec(
        id=f"dynamodb-{spec.name}",
        type="dynamodb",
        position={"x": 0, "y": 0},  # Default position for testing
        data=NodeDataSpec(spec=spec)
    )

def parse_attributes(attributes_str: str) -> List[DynamoDBAttribute]:
    """Parse attribute string into list of DynamoDBAttribute objects."""
    attributes = []
    for attr_str in attributes_str.split(','):
        try:
            name, type_str = attr_str.split(':')
            try:
                attr_type = AttributeType[type_str.upper()]
            except KeyError:
                print(f"Error: Invalid attribute type '{type_str}'. Must be one of: {', '.join(attr.name for attr in AttributeType)}")
                sys.exit(1)
            attributes.append(DynamoDBAttribute(name=name.strip(), type=attr_type.value))
        except ValueError:
            print(f"Error: Invalid attribute format '{attr_str}'. Expected format: 'name:type'")
            sys.exit(1)
    return attributes

async def main():
    parser = argparse.ArgumentParser(description='Test DynamoDB Agent')
    parser.add_argument('--table-name', required=True, help='Name of the DynamoDB table')
    parser.add_argument('--primary-key', required=True, help='Name of the primary key')
    parser.add_argument('--attributes', required=True, help='Comma-separated list of attributes in format "name:type"')
    parser.add_argument('--language', required=True, choices=['java', 'python', 'typescript'], help='Programming language')
    parser.add_argument('--max-retries', type=int, default=3, help='Maximum number of retries')
    parser.add_argument('--retry-delay', type=float, default=1.0, help='Delay between retries in seconds')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--range-key', required=False, help='Name of the range key')

    args = parser.parse_args()

    # Setup logging
    logger = setup_logging(args.verbose)
    logger.info("Starting DynamoDB agent test")

    try:
        # Create test configuration
        config = TestConfig(
            table_name=args.table_name,
            primary_key=args.primary_key,
            range_key=args.range_key,
            attributes=parse_attributes(args.attributes),
            programming_language=ProgrammingLanguage(args.language),
            max_retries=args.max_retries,
            retry_delay=args.retry_delay
        )

        # Create DynamoDB spec and canvas node
        spec = create_dynamodb_spec(config)
        canvas_node = create_canvas_node(spec)
        logger.info(f"Created DynamoDB spec with primary key '{config.primary_key}'")

        # Initialize inference client and agent
        inference_client = OpenAIInference()  # You'll need to implement this
        agent = DynamoDBAgent(
            inference_client=inference_client,
            current_node=canvas_node,
            programming_language=config.programming_language,
            max_retries=config.max_retries,
            retry_delay=config.retry_delay
        )

        # Generate code
        logger.info(f"Generating DynamoDB code in {config.programming_language.value}")
        code = await agent.generate_code()
        
        # Print generated code
        print("\nGenerated Code:")
        print("-" * 80)
        pprint(code)
        print("-" * 80)

        logger.info("Code generation completed successfully")
        return 0

    except Exception as e:
        logger.error(f"Error during code generation: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    asyncio.run(main()) 