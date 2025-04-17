from .common_prompts import COMMON_CODE_GENERATION_INSTRUCTIONS

PYTHON_PROMPT = f"""{COMMON_CODE_GENERATION_INSTRUCTIONS}

Generate a Python application orchestrator class based on the provided specifications.

Instructions:
1. Create a well-structured Python class for the orchestrator
2. Include proper docstrings and type hints
3. Implement orchestration logic for composed nodes
4. Handle node dependencies and execution order
5. Implement proper error handling and recovery
6. Follow PEP 8 style guide
7. Use dependency injection for composed nodes
8. Make the code production-ready
9. Include all necessary imports
10. Use proper type hints
11. Include comprehensive logging
12. Add input validation where necessary
13. Include proper error messages
14. Follow SOLID principles
15. Include proper documentation for each method
16. Handle edge cases appropriately
17. Include unit test stubs
18. Implement proper node lifecycle management
19. Include proper state management
20. Handle concurrent execution if needed
21. Implement proper error propagation
22. Include proper retry mechanisms
23. Handle node failures gracefully
24. Include proper monitoring and metrics
25. Implement proper cleanup procedures"""

JAVA_PROMPT = f"""{COMMON_CODE_GENERATION_INSTRUCTIONS}

Generate a Java application orchestrator class based on the provided specifications.

Instructions:
1. Create a well-structured Java class for the orchestrator
2. Include proper annotations and documentation
3. Implement orchestration logic for composed nodes
4. Handle node dependencies and execution order
5. Implement proper error handling and recovery
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
20. Implement proper node lifecycle management
21. Include proper state management
22. Handle concurrent execution if needed
23. Implement proper error propagation
24. Include proper retry mechanisms
25. Handle node failures gracefully"""

TYPESCRIPT_PROMPT = f"""{COMMON_CODE_GENERATION_INSTRUCTIONS}

Generate a TypeScript application orchestrator class based on the provided specifications.

Instructions:
1. Create a well-structured TypeScript class for the orchestrator
2. Include proper TypeScript types and interfaces
3. Implement orchestration logic for composed nodes
4. Handle node dependencies and execution order
5. Implement proper error handling and recovery
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
20. Implement proper node lifecycle management
21. Include proper state management
22. Handle concurrent execution if needed
23. Implement proper error propagation
24. Include proper retry mechanisms
25. Handle node failures gracefully"""

# Map of language to prompt template
APPLICATION_ORCHESTRATOR_PROMPTS = {
    "python": PYTHON_PROMPT,
    "java": JAVA_PROMPT,
    "typescript": TYPESCRIPT_PROMPT
}