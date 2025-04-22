from .node_prompts import COMMON_CODE_GENERATION_INSTRUCTIONS

PYTHON_PROMPT = f"""{COMMON_CODE_GENERATION_INSTRUCTIONS}

Generate an S3-backed architectural component in Python using boto3.

Instructions:
1. Create a helper class for common S3 operations using boto3
2. Include methods for CRUDL operations:
   - Uploading files
   - Downloading files
   - Listing objects
   - Deleting objects
3. Include class-level config for:
   - Bucket name
   - Default storage class
   - Base path (if provided)
4. Use best practices: multipart upload, retries, public/private ACLs if needed
5. Structure code into `dao/` for logic and `models/` for any data representations
6. Include custom exception handling for S3-specific errors (e.g., NoSuchKey, AccessDenied)
7. Use dataclasses where relevant, and type hints throughout
8. Include proper logging and error messages
9. Use PEP8 and idiomatic Python style
10. Generate corresponding unit tests for all public methods under `tst/<flow>/dao/`
"""

JAVA_PROMPT = f"""{COMMON_CODE_GENERATION_INSTRUCTIONS}

Generate an S3-backed architectural component in Java using AWS SDK v2.

Instructions:
1. Implement a utility class or service for S3 operations using AWS SDK v2
2. Include methods for:
   - Uploading files (including multipart uploads)
   - Downloading files
   - Listing files
   - Deleting files
3. Add configuration for bucket name, region, and base path prefix
4. Handle common exceptions (NoSuchKey, AmazonServiceException, etc.)
5. Include logging, retries, and proper error propagation
6. Use appropriate access modifiers, Java conventions, and annotations
7. Add proper Javadoc for methods and classes
8. Structure logic into `dao/` and unit tests under `tst/`
9. Ensure the code is production-grade and testable
"""

TYPESCRIPT_PROMPT = f"""{COMMON_CODE_GENERATION_INSTRUCTIONS}

Generate an S3-backed architectural component in TypeScript using AWS SDK v3.

Instructions:
1. Implement a class to encapsulate S3 logic using `@aws-sdk/client-s3`
2. Add support for:
   - Uploading files (multipart uploads included)
   - Downloading files
   - Listing contents
   - Deleting files
3. Define config for bucket name, region, and optional base path
4. Use strong types and interfaces for method parameters and responses
5. Add proper error handling for S3-specific errors
6. Include logging and tracing where relevant
7. Follow TypeScript best practices and project conventions
8. Include JSDoc for each method
9. Structure the component in `dao/` and generate corresponding unit tests in `tst/`
10. Ensure the code is clean, reusable, and production-ready
"""

# Map of language to prompt template
S3_PROMPTS = {
    "python": PYTHON_PROMPT,
    "java": JAVA_PROMPT,
    "typescript": TYPESCRIPT_PROMPT
}
