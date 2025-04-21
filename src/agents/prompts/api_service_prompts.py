from .common_prompts import COMMON_CODE_GENERATION_INSTRUCTIONS

PYTHON_PROMPT = f"""{COMMON_CODE_GENERATION_INSTRUCTIONS}

Generate an API service architectural component in Python.

Instructions:
1. Create a service that encapsulates the API logic. Define a strongly typed service interface.
2. Include methods for:
   - API endpoint management (GET, POST, PUT, DELETE, PATCH)
   - Request/response handling
   - Error handling and status codes
   - Input validation
3. Use dataclasses for API endpoint models with:
   - path: str
   - method: Literal['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
   - description: str
4. Implement proper logging and monitoring
5. Structure code under `service/` and `models/` subfolders
6. Include comprehensive error handling with custom exceptions
7. Add input validation and sanitization
8. Follow PEP 8 and Python best practices
9. Include unit tests for all public methods
10. Make the code production-ready and well-documented
11. Use meaningful naming and clean abstractions
12. Include proper configuration management
"""

JAVA_PROMPT = f"""{COMMON_CODE_GENERATION_INSTRUCTIONS}

Generate an API service architectural component in Java.

Instructions:
1. Create a well-structured service with proper annotations. Define a strongly typed service interface.
2. Implement core service methods with proper error handling
3. Use Spring Boot or similar framework if applicable
4. Define API endpoint models with:
   - path: String
   - method: Enum['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
   - description: String
5. Add proper JavaDoc and access modifiers
6. Implement retry mechanisms and circuit breakers
7. Include logging and monitoring
8. Organize code under `service/` and `model/` packages
9. Follow Java best practices and conventions
10. Generate corresponding unit tests using JUnit or TestNG
11. Include proper exception handling and validation
12. Make the code production-grade and well-documented
"""

TYPESCRIPT_PROMPT = f"""{COMMON_CODE_GENERATION_INSTRUCTIONS}

Generate an API service architectural component in TypeScript.

Instructions:
1. Define a strongly typed service interface.
2. Implement a service class with core operations
3. Define API endpoint interfaces with:
   - path: string
   - method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'
   - description: string
4. Add proper error handling and retries
5. Follow TypeScript best practices and use strict typing
6. Structure code under `service/` and `models/` folders
7. Include comprehensive error handling
8. Use async/await consistently
9. Generate test stubs with mocked dependencies
10. Make the code production-ready and cleanly documented
11. Include proper logging and monitoring
12. Use meaningful naming and clean abstractions
"""

# Map of language to prompt template
API_SERVICE_PROMPTS = {
    "python": PYTHON_PROMPT,
    "java": JAVA_PROMPT,
    "typescript": TYPESCRIPT_PROMPT
} 