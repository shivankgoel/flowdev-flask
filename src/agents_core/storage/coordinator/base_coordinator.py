from typing import Dict, Any
from datetime import datetime
import logging

class StorageCoordinatorError(Exception):
    """Base exception for storage coordinator errors."""
    pass

class ImmutableVersionError(StorageCoordinatorError):
    """Raised when attempting to modify a non-draft version."""
    pass

class BaseCoordinator:
    """Base class for all coordinators."""
    
    def __init__(self):
        """Initialize the coordinator."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def _validate_version_mutable(self, version: str) -> None:
        """Validate that a version is mutable (draft).
        
        Args:
            version: The version to validate
            
        Raises:
            ImmutableVersionError: If the version is not draft
        """
        if version != "draft":
            raise ImmutableVersionError(f"Cannot modify non-draft version: {version}")

    def _get_timestamp(self) -> str:
        """Get the current timestamp in ISO format.
        
        Returns:
            str: Current timestamp in ISO format
        """
        return datetime.utcnow().isoformat() 