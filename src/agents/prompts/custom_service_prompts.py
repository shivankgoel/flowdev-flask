from .common_prompts import COMMON_CODE_GENERATION_INSTRUCTIONS

PYTHON_PROMPT = f"""{COMMON_CODE_GENERATION_INSTRUCTIONS}

Generate a custom service architectural component in Python.
Service must be built on top of other services whenever possible using composition.
Do not try to implement logic already implemented by other services. Just use them.

Instructions:
1. Create a service that encapsulates the custom service logic.  Define a strongly typed service interface.
2. Include methods for:
   - Service initialization and configuration
   - Core service operations
   - Error handling and retries
3. Use dataclasses for data models and type hints throughout
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

Generate a custom service architectural component in Java.

Instructions:
1. Create a well-structured service with proper annotations.  Define a strongly typed service interface.
2. Implement core service methods with proper error handling
3. Use Spring Boot or similar framework if applicable
4. Include configuration management
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

Generate a custom service architectural component in TypeScript.

Instructions:
1. Define a strongly typed service interface.
2. Implement a service class with core operations
3. Include configuration management
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
CUSTOM_SERVICE_PROMPTS = {
    "python": PYTHON_PROMPT,
    "java": JAVA_PROMPT,
    "typescript": TYPESCRIPT_PROMPT
}
