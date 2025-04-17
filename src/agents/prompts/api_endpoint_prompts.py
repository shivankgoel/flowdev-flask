from .common_prompts import COMMON_CODE_GENERATION_INSTRUCTIONS

PYTHON_PROMPT = f"""{COMMON_CODE_GENERATION_INSTRUCTIONS}

Generate a Python API endpoint handler based on the provided specifications.

Instructions:
1. Create a well-structured Python class for the API endpoint
2. Include proper docstrings and type hints
3. Implement the specified HTTP method handler
4. Handle query parameters (required and optional)
5. Implement request body validation
6. Implement response formatting
7. Follow PEP 8 style guide
8. Include proper error handling
9. Make the code production-ready
10. Include all necessary imports
11. Use proper type hints
12. Include comprehensive logging
13. Add input validation where necessary
14. Include proper error messages
15. Follow SOLID principles
16. Include proper documentation for each method
17. Handle edge cases appropriately
18. Include unit test stubs
19. Implement proper authentication handling
20. Include proper content type handling
21. Handle streaming endpoints if specified
22. Implement proper request/response validation
23. Include proper error responses
24. Handle CORS if needed
25. Include rate limiting if specified"""

JAVA_PROMPT = f"""{COMMON_CODE_GENERATION_INSTRUCTIONS}

Generate a Java API endpoint handler based on the provided specifications.

Instructions:
1. Create a well-structured Java class for the API endpoint
2. Include proper annotations and documentation
3. Implement the specified HTTP method handler
4. Handle query parameters (required and optional)
5. Implement request body validation
6. Implement response formatting
7. Follow Java coding conventions and style
8. Include comprehensive Javadoc
9. Use appropriate access modifiers
10. Make the code production-ready
11. Include all necessary imports
12. Use proper Java annotations
13. Include proper exception handling
14. Include comprehensive logging
15. Add input validation where necessary
16. Include proper error messages
17. Follow SOLID principles
18. Include proper documentation for each method
19. Handle edge cases appropriately
20. Include unit test stubs
21. Implement proper authentication handling
22. Include proper content type handling
23. Handle streaming endpoints if specified
24. Implement proper request/response validation
25. Include proper error responses"""

TYPESCRIPT_PROMPT = f"""{COMMON_CODE_GENERATION_INSTRUCTIONS}

Generate a TypeScript API endpoint handler based on the provided specifications.

Instructions:
1. Create a well-structured TypeScript class for the API endpoint
2. Include proper TypeScript types and interfaces
3. Implement the specified HTTP method handler
4. Handle query parameters (required and optional)
5. Implement request body validation
6. Implement response formatting
7. Follow TypeScript best practices
8. Use async/await for all operations
9. Include proper JSDoc documentation
10. Use strict TypeScript mode
11. Make the code production-ready
12. Include all necessary imports
13. Use proper TypeScript types
14. Include comprehensive logging
15. Add input validation where necessary
16. Include proper error messages
17. Follow SOLID principles
18. Include proper documentation for each method
19. Handle edge cases appropriately
20. Include unit test stubs
21. Implement proper authentication handling
22. Include proper content type handling
23. Handle streaming endpoints if specified
24. Implement proper request/response validation
25. Include proper error responses"""

# Map of language to prompt template
API_ENDPOINT_PROMPTS = {
    "python": PYTHON_PROMPT,
    "java": JAVA_PROMPT,
    "typescript": TYPESCRIPT_PROMPT
}