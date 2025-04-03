from dataclasses import dataclass
from typing import List, Dict, Any
from src.infra.config import BillingMode

@dataclass
class GSI:
    index_name: str
    partition_key: str
    sort_key: str
    projection_type: str = "ALL"

@dataclass
class TableDefinition:
    table_name: str
    partition_key: str
    sort_key: str
    attributes: List[Dict[str, str]]
    gsis: List[GSI] = None
    billing_mode: BillingMode = BillingMode.PAY_PER_REQUEST

# Table Definitions

"""
CANVAS_TABLE Access Patterns:
1. Get all canvas IDs for a customer (using partition key)
2. Get all versions for a specific canvas (using sort key prefix)
"""
CANVAS_TABLE = TableDefinition(
    table_name="flow_canvas",
    partition_key="customer_id",
    sort_key="canvas_id_and_version",  # Format: canvas_id#version
    attributes=[
        {"AttributeName": "customer_id", "AttributeType": "S"},
        {"AttributeName": "canvas_id_and_version", "AttributeType": "S"}
    ],
    gsis=[]  # No GSIs needed as main index supports all required patterns
)

"""
NODES_TABLE Access Patterns:
1. Get all nodes for a specific canvas version (using sort key prefix)
2. Get/update a specific node (using full key)
"""
NODES_TABLE = TableDefinition(
    table_name="flow_canvas_nodes",
    partition_key="customer_id_and_canvas_id",  # Format: customer_id#canvas_id
    sort_key="version_and_node_id",  # Format: version#node_id
    attributes=[
        {"AttributeName": "customer_id_and_canvas_id", "AttributeType": "S"},
        {"AttributeName": "version_and_node_id", "AttributeType": "S"}
    ],
    gsis=[]  # No GSIs needed as main index supports all required patterns
)

"""
EDGES_TABLE Access Patterns:
1. Get all edges for a specific canvas version (using sort key prefix)
2. Get/update a specific edge (using full key)
"""
EDGES_TABLE = TableDefinition(
    table_name="flow_canvas_edges",
    partition_key="customer_id_and_canvas_id",  # Format: customer_id#canvas_id
    sort_key="version_and_edge_id",  # Format: version#edge_id
    attributes=[
        {"AttributeName": "customer_id_and_canvas_id", "AttributeType": "S"},
        {"AttributeName": "version_and_edge_id", "AttributeType": "S"}
    ],
    gsis=[]  # No GSIs needed as main index supports all required patterns
)

"""
CHAT_THREADS_TABLE Access Patterns:
1. Get all threads for a specific node in a canvas version (using sort key prefix)
2. Get/update a specific thread (using full key)
"""
CHAT_THREADS_TABLE = TableDefinition(
    table_name="flow_canvas_chat_threads",
    partition_key="customer_id_and_canvas_id",  # Format: customer_id#canvas_id
    sort_key="version_node_id_and_thread_id",  # Format: version#node_id#thread_id
    attributes=[
        {"AttributeName": "customer_id_and_canvas_id", "AttributeType": "S"},
        {"AttributeName": "version_node_id_and_thread_id", "AttributeType": "S"}
    ],
    gsis=[]  # No GSIs needed as main index supports all required patterns
) 