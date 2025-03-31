from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable
from inference import InferenceClient
import time
from dataclasses import dataclass
from enum import Enum
import json

class AgentStep(Enum):
    """Enumeration of possible agent steps."""
    START = "start"
    LOAD_TEMPLATE = "load_template"
    FORMAT_PROMPT = "format_prompt"
    GENERATE_CODE = "generate_code"
    PARSE_RESPONSE = "parse_response"
    VALIDATE_CODE = "validate_code"
    RETRY = "retry"
    COMPLETE = "complete"
    ERROR = "error"

@dataclass
class AgentObservation:
    """Observation of an agent's step."""
    step: AgentStep
    timestamp: float
    details: Dict[str, Any]
    error: Optional[str] = None

class GenerationFeedback:
    """Feedback about code generation that can be used for retries."""
    def __init__(
        self,
        error_message: Optional[str] = None,
        missing_imports: Optional[List[str]] = None,
        missing_patterns: Optional[List[str]] = None,
        validation_errors: Optional[List[str]] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ):
        self.error_message = error_message
        self.missing_imports = missing_imports or []
        self.missing_patterns = missing_patterns or []
        self.validation_errors = validation_errors or []
        self.additional_context = additional_context or {}

class BaseSpecAgent(ABC):
    def __init__(
        self,
        inference_client: InferenceClient,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        observation_callback: Optional[Callable[[AgentObservation], None]] = None
    ):
        self.inference_client = inference_client
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.observation_callback = observation_callback
        self.observations: List[AgentObservation] = []
        
    def _observe(self, step: AgentStep, details: Dict[str, Any], error: Optional[str] = None) -> None:
        """
        Record an observation of the agent's progress.
        
        Args:
            step: The current step being observed
            details: Additional details about the step
            error: Optional error message if the step failed
        """
        observation = AgentObservation(
            step=step,
            timestamp=time.time(),
            details=details,
            error=error
        )
        self.observations.append(observation)
        
        if self.observation_callback:
            self.observation_callback(observation)
            
    def get_observations(self) -> List[AgentObservation]:
        """
        Get all observations recorded during execution.
        
        Returns:
            List[AgentObservation]: List of observations
        """
        return self.observations
        
    def get_observation_summary(self) -> str:
        """
        Get a human-readable summary of the agent's execution.
        
        Returns:
            str: Summary of observations
        """
        summary = []
        for obs in self.observations:
            step_info = f"Step: {obs.step.value}"
            if obs.error:
                step_info += f" (Error: {obs.error})"
            summary.append(step_info)
        return "\n".join(summary)
        
    @abstractmethod
    def generate_code(self, spec: Any, input_specs: List[Any]) -> str:
        """
        Generate code based on the spec and input specs.
        
        Args:
            spec: The spec for which code needs to be generated
            input_specs: List of specs from input nodes
            
        Returns:
            str: Generated code
        """
        pass
    
    @abstractmethod
    def parse_response(self, response: str) -> str:
        """
        Parse the LLM response to extract the generated code.
        
        Args:
            response: Raw response from the LLM
            
        Returns:
            str: Parsed code
        """
        pass
    
    def generate_with_retry(
        self,
        spec: Any,
        input_specs: List[Any],
        feedback: Optional[GenerationFeedback] = None,
        retry_count: int = 0
    ) -> str:
        """
        Generate code with retry mechanism based on feedback.
        
        Args:
            spec: The spec for which code needs to be generated
            input_specs: List of specs from input nodes
            feedback: Optional feedback from previous generation attempt
            retry_count: Current retry count
            
        Returns:
            str: Generated code
            
        Raises:
            ValueError: If max retries exceeded or generation fails
        """
        try:
            self._observe(AgentStep.START, {
                "spec": str(spec),
                "input_specs": [str(s) for s in input_specs],
                "retry_count": retry_count,
                "feedback": str(feedback) if feedback else None
            })
            
            # Generate code
            self._observe(AgentStep.GENERATE_CODE, {"spec": str(spec)})
            code = self.generate_code(spec, input_specs)
            
            # Parse and validate the response
            self._observe(AgentStep.PARSE_RESPONSE, {"code_length": len(code)})
            parsed_code = self.parse_response(code)
            
            self._observe(AgentStep.COMPLETE, {
                "code_length": len(parsed_code),
                "retry_count": retry_count
            })
            return parsed_code
            
        except ValueError as e:
            self._observe(AgentStep.ERROR, {
                "error": str(e),
                "retry_count": retry_count
            }, str(e))
            
            # If we have feedback, use it to improve the next attempt
            if feedback:
                self._observe(AgentStep.RETRY, {
                    "feedback": str(feedback),
                    "retry_count": retry_count
                })
                # Update prompt with feedback
                self._update_prompt_with_feedback(feedback)
                
            # Check if we should retry
            if retry_count < self.max_retries:
                # Wait before retrying
                time.sleep(self.retry_delay)
                
                # Increment retry count and try again
                return self.generate_with_retry(
                    spec,
                    input_specs,
                    feedback,
                    retry_count + 1
                )
            else:
                raise ValueError(f"Max retries ({self.max_retries}) exceeded: {str(e)}")
                
    @abstractmethod
    def _update_prompt_with_feedback(self, feedback: GenerationFeedback) -> None:
        """
        Update the prompt template based on feedback.
        
        Args:
            feedback: Feedback from previous generation attempt
        """
        pass
    
    def _load_prompt_template(self, template_path: str) -> str:
        """
        Load a prompt template from file.
        
        Args:
            template_path: Path to the prompt template file
            
        Returns:
            str: The prompt template
        """
        self._observe(AgentStep.LOAD_TEMPLATE, {"template_path": template_path})
        with open(template_path, 'r') as f:
            template = f.read()
        return template
            
    def _format_prompt(self, template: str, **kwargs) -> str:
        """
        Format a prompt template with the given values.
        
        Args:
            template: The prompt template
            **kwargs: Values to format into the template
            
        Returns:
            str: Formatted prompt
        """
        self._observe(AgentStep.FORMAT_PROMPT, {
            "template_length": len(template),
            "kwargs_keys": list(kwargs.keys())
        })
        return template.format(**kwargs)
        
    def _save_formatted_prompt(self, prompt: str, output_path: str) -> None:
        """
        Save a formatted prompt to file.
        
        Args:
            prompt: The formatted prompt
            output_path: Path where to save the prompt
        """
        with open(output_path, 'w') as f:
            f.write(prompt) 