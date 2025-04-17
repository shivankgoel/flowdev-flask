from .common_prompts import COMMON_CODE_GENERATION_INSTRUCTIONS

PYTHON_PROMPT = f"""{COMMON_CODE_GENERATION_INSTRUCTIONS}

Generate a Python data model class based on the provided specifications.

Instructions:
1. Create a well-structured Python class using dataclasses
2. Include proper docstrings and type hints
3. Implement all specified attributes with proper types
4. Implement relationship handling methods
5. Include proper validation methods
6. Follow PEP 8 style guide
7. Use dataclasses for data models
8. Include proper serialization/deserialization methods
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
19. Implement proper relationship handling
20. Include proper validation rules"""

JAVA_PROMPT = f"""{COMMON_CODE_GENERATION_INSTRUCTIONS}

Generate a Java data model class based on the provided specifications.

Instructions:
1. Create a well-structured Java class
2. Include proper annotations and documentation
3. Implement all specified attributes with proper types
4. Implement relationship handling methods
5. Include proper validation methods
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
17. Include proper documentation for each method
18. Handle edge cases appropriately
19. Include unit test stubs
20. Implement proper relationship handling"""

TYPESCRIPT_PROMPT = f"""{COMMON_CODE_GENERATION_INSTRUCTIONS}

Generate a TypeScript data model class based on the provided specifications.

Instructions:
1. Create a well-structured TypeScript class
2. Include proper TypeScript types and interfaces
3. Implement all specified attributes with proper types
4. Implement relationship handling methods
5. Include proper validation methods
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
17. Include proper documentation for each method
18. Handle edge cases appropriately
19. Include unit test stubs
20. Implement proper relationship handling"""

# Map of language to prompt template
DATA_MODEL_PROMPTS = {
    "python": PYTHON_PROMPT,
    "java": JAVA_PROMPT,
    "typescript": TYPESCRIPT_PROMPT
}