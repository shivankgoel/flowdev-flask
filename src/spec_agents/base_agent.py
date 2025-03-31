from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from src.inference import InferenceClient
from src.specs.flow_canvas_spec import CanvasNodeSpec, ProgrammingLanguage
import time
from dataclasses import dataclass
from enum import Enum
import logging
import asyncio

logger = logging.getLogger(__name__)

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

class FeedbackType(Enum):
    """Types of feedback that can be generated."""
    ERROR = "error"
    MISSING_IMPORT = "missing_import"
    MISSING_PATTERN = "missing_pattern"
    VALIDATION_ERROR = "validation_error"
    TYPE_ERROR = "type_error"
    SYNTAX_ERROR = "syntax_error"
    OTHER = "other"

@dataclass
class CodeFeedback:
    """Structured feedback about code generation issues."""
    feedback_type: FeedbackType
    message: str
    details: Optional[Dict[str, Any]] = None

    def __str__(self) -> str:
        return f"{self.feedback_type.value}: {self.message}"

class BaseSpecAgent(ABC):
    def __init__(
        self,
        inference_client: InferenceClient,
        current_node: CanvasNodeSpec,
        programming_language: ProgrammingLanguage,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        self.inference_client = inference_client
        self.current_node = current_node
        self.programming_language = programming_language
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.logger = logging.getLogger(self.__class__.__name__)
        self.feedback_history: Dict[int, List[CodeFeedback]] = {}
        
    def _log_step(self, step: AgentStep, details: Dict[str, Any], error: Optional[str] = None) -> None:
        """Log an agent step with details."""
        log_data = {
            "step": step.value,
            "timestamp": time.time(),
            **details
        }
        
        if error:
            self.logger.error(f"Step {step.value} failed: {error}", extra=log_data)
        else:
            self.logger.info(f"Step {step.value} completed", extra=log_data)

    def _store_feedback(self, retry_count: int, feedback_list: List[CodeFeedback]) -> None:
        """Store feedback for a specific retry attempt."""
        if retry_count not in self.feedback_history:
            self.feedback_history[retry_count] = []
        self.feedback_history[retry_count].extend(feedback_list)
        
        self._log_step(AgentStep.RETRY, {
            "feedback": [str(f) for f in feedback_list],
            "retry_count": retry_count,
            "feedback_history": {k: [str(f) for f in v] for k, v in self.feedback_history.items()}
        })
    
    @abstractmethod
    async def generate_code(self, retry_count: int = 0) -> str:
        """Generate code based on the input specs."""
        pass
    
    @abstractmethod
    def parse_response(self, response: str, retry_count: int) -> str:
        """Parse the LLM response to extract the generated code."""
        pass
    
    async def generate_with_retry(
        self,
        input_specs: List[Any],
        retry_count: int = 0
    ) -> str:
        """
        Generate code with retry mechanism based on feedback history.
        
        Args:
            input_specs: List of specs from input nodes
            retry_count: Current retry count
            
        Returns:
            str: Generated code
            
        Raises:
            ValueError: If max retries exceeded or generation fails
        """
        try:
            # Log start of generation attempt
            self._log_step(AgentStep.START, {
                "input_specs": [str(s) for s in input_specs],
                "retry_count": retry_count,
                "feedback_history": {k: [str(f) for f in v] for k, v in self.feedback_history.items()}
            })
            
            # Generate code
            code = await self.generate_code(retry_count)
            self._log_step(AgentStep.GENERATE_CODE, {"input_specs": [str(s) for s in input_specs]})
            
            # Parse response
            parsed_code = self.parse_response(code, retry_count)
            self._log_step(AgentStep.PARSE_RESPONSE, {"code_length": len(code)})
            
            # Log successful completion
            self._log_step(AgentStep.COMPLETE, {
                "code_length": len(parsed_code),
                "retry_count": retry_count
            })
            return parsed_code
            
        except ValueError as e:
            # Log error
            self._log_step(AgentStep.ERROR, {
                "error": str(e),
                "retry_count": retry_count
            }, str(e))
            
            # Handle retry logic
            if retry_count < self.max_retries:
                await asyncio.sleep(self.retry_delay)
                return await self.generate_with_retry(
                    input_specs,
                    retry_count + 1
                )
            
            raise ValueError(f"Max retries ({self.max_retries}) exceeded: {str(e)}") 