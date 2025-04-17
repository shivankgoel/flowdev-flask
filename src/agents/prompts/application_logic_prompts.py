from .common_prompts import COMMON_CODE_GENERATION_INSTRUCTIONS

PYTHON_PROMPT = f"""{COMMON_CODE_GENERATION_INSTRUCTIONS}

Generate a Python class with application logic based on the provided specifications.

Instructions:
1. Create a well-structured Python class
2. Include proper docstrings and type hints
3. Implement all specified private and public attributes
4. Implement all specified private and public functions
5. Include proper error handling
6. Follow PEP 8 style guide
7. Use dataclasses for data models
8. Include async support where appropriate
9. Make the code production-ready
10. Include all necessary imports
11. Use proper type hints
12. Use async/await where appropriate
13. Include comprehensive logging
14. Add input validation where necessary
15. Include proper error messages
16. Follow SOLID principles
17. Use dependency injection where appropriate
18. Include proper documentation for each method
19. Handle edge cases appropriately
20. Include unit test stubs"""

JAVA_PROMPT = f"""{COMMON_CODE_GENERATION_INSTRUCTIONS}

Generate a Java class with application logic based on the provided specifications.

Instructions:
1. Create a well-structured Java class
2. Include proper annotations and documentation
3. Implement all specified private and public attributes
4. Implement all specified private and public functions
5. Include proper error handling
6. Follow Java coding conventions and style
7. Include comprehensive Javadoc
8. Use appropriate access modifiers
9. Make the code production-ready
10. Include all necessary imports
11. Use proper Java annotations
12. Include proper exception handling
13. Include comprehensive logging
14. Add input validation where necessary
15. Include proper error messages
16. Follow SOLID principles
17. Use dependency injection where appropriate
18. Include proper documentation for each method
19. Handle edge cases appropriately
20. Include unit test stubs"""

TYPESCRIPT_PROMPT = f"""{COMMON_CODE_GENERATION_INSTRUCTIONS}

Generate a TypeScript class with application logic based on the provided specifications.

Instructions:
1. Create a well-structured TypeScript class
2. Include proper TypeScript types and interfaces
3. Implement all specified private and public attributes
4. Implement all specified private and public functions
5. Include proper error handling
6. Follow TypeScript best practices
7. Use async/await for all operations
8. Include proper JSDoc documentation
9. Use strict TypeScript mode
10. Make the code production-ready
11. Include all necessary imports
12. Use proper TypeScript types
13. Include comprehensive logging
14. Add input validation where necessary
15. Include proper error messages
16. Follow SOLID principles
17. Use dependency injection where appropriate
18. Include proper documentation for each method
19. Handle edge cases appropriately
20. Include unit test stubs"""

# Map of language to prompt template
APPLICATION_LOGIC_PROMPTS = {
    "python": PYTHON_PROMPT,
    "java": JAVA_PROMPT,
    "typescript": TYPESCRIPT_PROMPT
}