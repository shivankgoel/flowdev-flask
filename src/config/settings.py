"""
Configuration settings for the project.
"""

# S3 bucket for storing code and messages
S3_BUCKET_NAME = "flowdev-code-store"

# DynamoDB Table Configurations
CANVAS_TABLE = "flow_canvas"
CANVAS_NODES_TABLE = "flow_canvas_nodes"
CANVAS_EDGES_TABLE = "flow_canvas_edges"
CANVAS_CHAT_THREADS_TABLE = "flow_canvas_chat_threads"

# AWS Configuration
AWS_REGION = "us-east-1"
DYNAMODB_ENDPOINT = None  # Set to None for production, use local endpoint for development 