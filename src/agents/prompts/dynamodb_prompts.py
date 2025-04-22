from .node_prompts import COMMON_CODE_GENERATION_INSTRUCTIONS

PYTHON_PROMPT = f"""{COMMON_CODE_GENERATION_INSTRUCTIONS}

Generate a DynamoDB-backed architectural component in Python using boto3.

Instructions:
1. Create a data model using Python dataclasses with type hints
2. Generate a DAO class with basic CRUD operations using boto3
3. Include table definition/schema as metadata or class-level constants
4. Implement helper methods for indexing, pagination, conditional updates
5. Include proper error handling with custom exception classes if needed
6. Follow DynamoDB best practices (e.g., partition/sort key, idempotent writes)
7. Structure code cleanly under `dao/` and `models/` subfolders
8. Include unit tests for all public DAO methods
9. Make the code production-ready and follow PEP 8
10. Include all necessary imports and organize logically
11. Use meaningful naming and clean abstractions
12. Include logging and input validation where helpful
"""

JAVA_PROMPT = f"""{COMMON_CODE_GENERATION_INSTRUCTIONS}

Generate a DynamoDB-backed architectural component in Java using AWS SDK v2.

Instructions:
1. Create a well-structured POJO for the entity with annotations (e.g., @DynamoDbBean)
2. Implement a DAO class with CRUD operations using DynamoDBEnhancedClient
3. Include table name and schema definition in a configuration class or annotation
4. Implement optional secondary index access patterns
5. Handle conditional writes, paginated queries, and retries
6. Include proper JavaDoc and access modifiers
7. Add error handling, validation, and logging
8. Organize code under `dao/` and `model/` packages
9. Follow Java best practices and conventions
10. Generate corresponding unit tests using JUnit or TestNG
"""

TYPESCRIPT_PROMPT = f"""{COMMON_CODE_GENERATION_INSTRUCTIONS}

Generate a DynamoDB-backed architectural component in TypeScript using AWS SDK v3.

Instructions:
1. Define a strongly typed data model interface
2. Implement a class with CRUD methods using DynamoDB DocumentClient
3. Include utility functions for queries, pagination, and conditional updates
4. Clearly define the table name, key structure, and indexes
5. Follow TypeScript best practices and use strict typing
6. Structure code under `dao/` and `models/` folders
7. Include comprehensive error handling and custom error types if needed
8. Use async/await consistently
9. Generate test stubs with mocked DynamoDB client
10. Make the code production-ready and cleanly documented
"""

# Map of language to prompt template
DDB_PROMPTS = {
    "python": PYTHON_PROMPT,
    "java": JAVA_PROMPT,
    "typescript": TYPESCRIPT_PROMPT
} 