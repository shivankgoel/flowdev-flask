from .common_prompts import COMMON_CODE_GENERATION_INSTRUCTIONS

PYTHON_PROMPT = f"""{COMMON_CODE_GENERATION_INSTRUCTIONS}

Generate an S3 bucket DAO layer in Python using boto3.

Instructions:
1. Use boto3 for AWS S3 operations
2. Include proper docstrings and type hints
3. Include methods for CRUDL operations:
   - Uploading files
   - Downloading files
   - Listing objects
   - Deleting objects
4. Include proper error handling for S3-specific errors
5. Use best practices for S3 operations
6. Follow PEP 8 style guide
7. Use dataclasses for data models
8. Include async support where appropriate
9. Make the code production-ready
10. Include all necessary imports
11. Use proper type hints
12. Use async/await where appropriate
13. Handle large file uploads with multipart upload
14. Include proper logging
15. Support different storage classes
16. Note down the file path and bucket description and provide code accordingly
"""

JAVA_PROMPT = f"""{COMMON_CODE_GENERATION_INSTRUCTIONS}

Generate an S3 bucket DAO layer in Java using AWS SDK v2.

Instructions:
1. Use AWS SDK v2 for S3 operations
2. Include proper annotations and documentation
3. Include methods for CRUDL operations:
   - Uploading files
   - Downloading files
   - Listing objects
   - Deleting objects
4. Include proper error handling for S3-specific errors
5. Use best practices for S3 operations
6. Follow Java coding conventions and style
7. Include comprehensive Javadoc
8. Use appropriate access modifiers
9. Make the code production-ready
10. Include all necessary imports
11. Use proper Java annotations
12. Include proper exception handling
13. Handle large file uploads with multipart upload
14. Include proper logging
15. Support different storage classes
16. Note down the file path and bucket description and provide code accordingly"""

TYPESCRIPT_PROMPT = f"""{COMMON_CODE_GENERATION_INSTRUCTIONS}

Generate an S3 bucket DAO layer in TypeScript using AWS SDK v3.

Instructions:
1. Use AWS SDK v3 for S3 operations
2. Include proper TypeScript types and interfaces
3. Include methods for CRUDL operations:
   - Uploading files
   - Downloading files
   - Listing objects
   - Deleting objects
4. Include proper error handling for S3-specific errors
5. Use best practices for S3 operations
6. Follow TypeScript best practices
7. Use async/await for all operations
8. Include proper JSDoc documentation
9. Use strict TypeScript mode
10. Make the code production-ready
11. Include all necessary imports
12. Use proper TypeScript types
13. Handle large file uploads with multipart upload
14. Include proper logging
15. Support different storage classes
16. Note down the file path and bucket description and provide code accordingly"""

# Map of language to prompt template
S3_PROMPTS = {
    "python": PYTHON_PROMPT,
    "java": JAVA_PROMPT,
    "typescript": TYPESCRIPT_PROMPT
} 