#!/usr/bin/env python3

import os
import sys
import argparse
import logging
import re
from typing import List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import asyncio
from src.api.models.dataplane_models import CodeFile

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(project_root)

from src.specs.dynamodb_spec import DynamoDBTableSpec, DynamoDBAttribute
from src.agents.node_agents.dynamodb_agent import DynamoDBAgent
from src.inference.openai_inference import OpenAIInference
from src.inference.bedrock_inference import BedrockInference
from src.api.models.node_models import CanvasNode, CanvasNodeType, NodePosition
from src.storage.models.models import CanvasDefinitionDO
from src.api.models.dataplane_models import ProgrammingLanguage
from src.agents.models.agent_models import InvokeAgentRequest, InvokeAgentQuerySource

# Configure logging
def setup_logging(verbose: bool = False):
    """Configure logging based on verbosity level."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    return logging.getLogger(__name__)

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

def create_canvas_node(spec: DynamoDBTableSpec) -> CanvasNode:
    """Create a CanvasNode from the DynamoDB spec."""
    # Create node config with DynamoDB spec
    node_config = {
        "name": spec.name,
        "hashKey": spec.hash_key,
        "rangeKey": spec.range_key,
        "attributes": [{"name": attr.name, "type": attr.type} for attr in spec.attributes]
    }
    
    return CanvasNode(
        nodeId=f"dynamodb-{spec.name}",
        nodeType=CanvasNodeType.DYNAMO_DB,
        nodePosition=NodePosition(x=0, y=0),
        nodeConfig=node_config
    )

def create_canvas(node: CanvasNode, programming_language: ProgrammingLanguage) -> CanvasDefinitionDO:
    """Create a CanvasDefinitionDO for testing."""
    return CanvasDefinitionDO(
        nodes=[node],
        edges=[]
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

def save_code_to_file(code_files: List[CodeFile], table_name: str) -> List[str]:
    """Save generated code files to the output directory."""
    output_dir = os.path.join(os.path.dirname(__file__), 'generated')
    os.makedirs(output_dir, exist_ok=True)
    
    saved_files = []
    for code_file in code_files:
        # Create the full file path
        filepath = os.path.join(output_dir, f"{table_name}_{code_file.filePath}")
        
        # Create parent directories if they don't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Write the file
        with open(filepath, 'w') as f:
            f.write(code_file.code)
        saved_files.append(filepath)
    
    return saved_files

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
            node=canvas_node,
            canvas=canvas
        )

        # Create invoke request
        invoke_request = InvokeAgentRequest(
            query="Generate code for the DynamoDB table",
            query_source=InvokeAgentQuerySource.USER
        )

        # Generate code
        logger.info(f"Generating DynamoDB code in {config.programming_language.name}")
        response = await agent.invoke_agent(
            invoke_agent_request=invoke_request,
            language=config.programming_language
        )
        
        # Check for errors in the response
        if not response.code_parser_response.files:
            logger.error("No code files found in response")
            return False
            
        # Save code to files
        saved_files = save_code_to_file(response.code_parser_response.files, config.table_name)
        
        # Print generated code and file locations
        if verbose:
            print("\nGenerated Code:")
            print("-" * 80)
            for code_file in response.code_parser_response.files:
                print(f"\nFile: {code_file.filePath}")
                print(code_file.code)
            print("-" * 80)
        print(f"\nCode saved to: {', '.join(saved_files)}")

        logger.info(f"Code generation completed successfully and saved to {saved_files}")
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
            programming_language=ProgrammingLanguage(name=args.language, version="latest")
        )

        # Run test case
        success = await run_test_case(config, inference_client, logger, args.verbose)
        return 0 if success else 1

    except Exception as e:
        logger.error(f"Error during test execution: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    asyncio.run(main()) 