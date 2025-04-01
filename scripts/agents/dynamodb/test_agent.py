#!/usr/bin/env python3

import os
import sys
import argparse
import logging
import re
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
import asyncio
from pprint import pprint
from datetime import datetime

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(project_root)

from src.specs.dynamodb_spec import DynamoDBTableSpec, DynamoDBAttribute
from src.specs.flow_canvas_spec import ProgrammingLanguage, CanvasNodeSpec, NodeDataSpec, CanvasDefinitionSpec
from src.agents_core.agents.dynamodb_agent import DynamoDBAgent
from src.agents_core.prompts.utils.spec_formatters import CanvasToPrompt, NodeSpecToPrompt, DynamoDBTableToPrompt
from src.inference.openai_inference import OpenAIInference
from src.inference.bedrock_inference import BedrockInference

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
    range_key: Optional[str]
    attributes: List[DynamoDBAttribute]
    programming_language: ProgrammingLanguage

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

def create_canvas(node: CanvasNodeSpec, programming_language: ProgrammingLanguage) -> CanvasDefinitionSpec:
    """Create a CanvasDefinitionSpec for testing."""
    return CanvasDefinitionSpec(
        nodes={node.id: node},
        edges=[],
        programming_language=programming_language,
        version="1.0.0",
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat(),
        canvas_id="canvas-1"
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

def save_code_to_file(code: str, table_name: str, language: str) -> str:
    """
    Save generated code to a file in the output directory.
    
    Args:
        code: Generated code string
        table_name: Name of the DynamoDB table
        language: Programming language extension
        
    Returns:
        str: Path to the saved file
    """
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), 'generated')
    os.makedirs(output_dir, exist_ok=True)
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    extension = {
        'java': '.java',
        'python': '.py',
        'typescript': '.ts'
    }.get(language, '.txt')
    
    filename = f"{table_name}_{timestamp}{extension}"
    filepath = os.path.join(output_dir, filename)
    
    # Remove XML tags if present
    code = re.sub(r'<generated_code>|</generated_code>', '', code).strip()
    
    # Save code to file
    with open(filepath, 'w') as f:
        f.write(code)
        
    return filepath

async def run_test_case(
    config: TestConfig,
    inference_client: Any,
    logger: logging.Logger,
    verbose: bool = False
) -> bool:
    """Run a single test case with the given configuration."""
    try:
        # Create DynamoDB spec and canvas node
        spec = create_dynamodb_spec(config)
        canvas_node = create_canvas_node(spec)
        canvas = create_canvas(canvas_node, config.programming_language)
        logger.info(f"Created DynamoDB spec with primary key '{config.primary_key}'")

        # Initialize agent
        agent = DynamoDBAgent(
            inference_client=inference_client,
            current_node_id=canvas_node.id,
            canvas=canvas
        )

        # Generate code
        logger.info(f"Generating DynamoDB code in {config.programming_language.value}")
        response = await agent.generate_code()
        
        # Check for errors
        if response.error:
            logger.error(f"Code generation failed: {response.error}")
            return False
            
        # Save code to file
        filepath = save_code_to_file(
            code=response.code,
            table_name=config.table_name,
            language=config.programming_language.value
        )
        
        # Print generated code and file location
        if verbose:
            print("\nGenerated Code:")
            print("-" * 80)
            pprint(response.code)
            print("-" * 80)
        print(f"\nCode saved to: {filepath}")

        logger.info(f"Code generation completed successfully and saved to {filepath}")
        return True

    except Exception as e:
        logger.error(f"Error during code generation: {str(e)}", exc_info=True)
        return False

async def main():
    parser = argparse.ArgumentParser(description='Test DynamoDB Agent')
    parser.add_argument('--table-name', required=True, help='Name of the DynamoDB table')
    parser.add_argument('--primary-key', required=True, help='Name of the primary key')
    parser.add_argument('--attributes', required=True, help='Comma-separated list of attributes in format "name:type"')
    parser.add_argument('--language', required=True, choices=['java', 'python', 'typescript'], help='Programming language')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--range-key', required=False, help='Name of the range key')
    parser.add_argument('--inference', choices=['bedrock', 'openai'], default='bedrock', help='Inference client to use (default: bedrock)')

    args = parser.parse_args()

    # Setup logging
    logger = setup_logging(args.verbose)
    logger.info("Starting DynamoDB agent test")

    try:
        # Initialize inference client based on argument
        if args.inference == 'openai':
            inference_client = OpenAIInference()
            logger.info("Using OpenAI inference client")
        else:
            inference_client = BedrockInference()
            logger.info("Using Bedrock inference client")

        # Create test configuration
        config = TestConfig(
            table_name=args.table_name,
            primary_key=args.primary_key,
            range_key=args.range_key,
            attributes=parse_attributes(args.attributes),
            programming_language=ProgrammingLanguage(args.language)
        )

        # Run test case
        success = await run_test_case(config, inference_client, logger, args.verbose)
        return 0 if success else 1

    except Exception as e:
        logger.error(f"Error during test execution: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    asyncio.run(main()) 