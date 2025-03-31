import os
from typing import Dict, Any, List
from src.spec_agents.base_agent import CodeFeedback

class BaseFormatter:
    """Base class for all prompt formatters."""
    
    def __init__(self, template_path: str):
        """
        Initialize the formatter.
        
        Args:
            template_path: Path to the language-specific template file
        """
        self.template_path = template_path
        self.code_json_format_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'prompts',
            'prompt_templates',
            'common',
            'code_json_format.txt'
        )

    def _read_file(self, file_path: str) -> str:
        """Read and return contents of a file."""
        with open(file_path, 'r') as f:
            return f.read()

    def _format_feedback(self, feedback: CodeFeedback) -> str:
        """Format a single feedback item."""
        lines = [f"- {feedback.feedback_type.value}: {feedback.message}"]
        if feedback.details:
            lines.append(f"  Details: {feedback.details}")
        return "\n".join(lines)

    def _format_feedback_history(self, feedback_history: Dict[int, List[CodeFeedback]]) -> str:
        """Format feedback history into a string."""
        if not feedback_history:
            return ""
            
        sections = []
        for attempt_num, feedback_list in sorted(feedback_history.items()):
            sections.append(f"\nAttempt {attempt_num} Feedback:")
            sections.extend(self._format_feedback(feedback) for feedback in feedback_list)
        
        return "\n".join(sections)

    def _format_dependencies(self, dependencies: List[str]) -> str:
        """Format dependencies code into a string."""
        if not dependencies:
            return ""
            
        sections = ["\nDependencies Code:"]
        for i, code in enumerate(dependencies, 1):
            sections.append(f"\nDependency {i}:")
            sections.append("```")
            sections.append(code)
            sections.append("```")
        
        return "\n".join(sections)

    def format_prompt(self, **kwargs: Dict[str, Any]) -> str:
        """
        Format the complete prompt including main template, feedback history, and JSON format.
        
        Args:
            **kwargs: Keyword arguments for prompt formatting, including:
                - feedback_history: Dict[int, List[CodeFeedback]] - History of feedback for previous attempts
                - dependencies_code: List[str] - List of code snippets that the generated code depends on
            
        Returns:
            str: Formatted prompt
        """
        # Read and format main template
        template = self._read_file(self.template_path)
        main_prompt = template.format(**kwargs)
        
        # Get feedback section if present
        feedback_history = kwargs.get('feedback_history', {})
        feedback_section = self._format_feedback_history(feedback_history)
        
        # Get dependencies section if present
        dependencies = kwargs.get('dependencies_code', [])
        dependencies_section = self._format_dependencies(dependencies)
        
        # Read JSON format
        json_format = self._read_file(self.code_json_format_path)
        
        # Combine all sections
        sections = [main_prompt]
        if dependencies_section:
            sections.append(dependencies_section)
        if feedback_section:
            sections.append(feedback_section)
        sections.append(json_format)
        
        return "\n\n".join(sections) 