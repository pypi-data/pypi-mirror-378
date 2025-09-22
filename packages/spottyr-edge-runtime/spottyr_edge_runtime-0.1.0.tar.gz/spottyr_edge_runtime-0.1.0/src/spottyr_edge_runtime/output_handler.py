"""
Output handling utilities for SpottyrWorkflow.
Provides structured output, logging, and result serialization.
"""

import json
import sys
import logging
from typing import Any, Dict, Optional
from enum import Enum
from datetime import datetime


class OutputLevel(Enum):
    """Output levels for different types of messages."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    RESULT = "result"


class WorkflowOutputHandler:
    """
    Handles structured output for workflow scripts.
    Separates result data from logging/debug information.
    """

    def __init__(self, enable_logging: bool = True, log_level: str = "INFO"):
        """
        Initialize the output handler.

        Args:
            enable_logging: Whether to enable file/stderr logging
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.enable_logging = enable_logging
        self._setup_logging(log_level)

    def _setup_logging(self, log_level: str):
        """Setup logging configuration."""
        if not self.enable_logging:
            return

        # Configure logging to stderr (not stdout) to avoid interfering with results
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(levelname)s - %(message)s',
            stream=sys.stderr  # Important: use stderr, not stdout
        )
        self.logger = logging.getLogger(__name__)

    def log(self, level: OutputLevel, message: str, **kwargs):
        """
        Log a message at the specified level.

        Args:
            level: The output level
            message: The message to log
            **kwargs: Additional context data
        """
        if not self.enable_logging:
            return

        log_data = {
            "message": message,
            "timestamp": datetime.now().isoformat(),
            **kwargs
        }

        if level == OutputLevel.DEBUG:
            self.logger.debug(json.dumps(log_data))
        elif level == OutputLevel.INFO:
            self.logger.info(json.dumps(log_data))
        elif level == OutputLevel.WARNING:
            self.logger.warning(json.dumps(log_data))
        elif level == OutputLevel.ERROR:
            self.logger.error(json.dumps(log_data))

    def output_result(self, result: Dict[str, Any]):
        """
        Output the final result to stdout as JSON.
        This is the primary output that will be captured by the workflow system.

        Args:
            result: The result dictionary to output
        """
        # Add metadata to the result
        enriched_result = {
            **result,
            "_metadata": {
                "timestamp": datetime.now().isoformat(),
                "output_version": "1.0"
            }
        }

        # Output to stdout (this is what gets captured)
        print(json.dumps(enriched_result, indent=None, separators=(',', ':')))

    def output_error(self, error_message: str, error_code: Optional[int] = None):
        """
        Output an error result and exit.

        Args:
            error_message: The error message
            error_code: Optional error code (defaults to 1)
        """
        error_result = {
            "error": error_message,
            "_metadata": {
                "timestamp": datetime.now().isoformat(),
                "output_version": "1.0",
                "type": "error"
            }
        }

        # Log the error as well
        if self.enable_logging:
            self.log(OutputLevel.ERROR, error_message)

        # Output error to stdout (so it gets captured properly)
        print(json.dumps(error_result, indent=None, separators=(',', ':')))
        sys.exit(error_code or 1)


# Convenience functions for common use cases
def create_success_result(prediction: Any, **additional_data) -> Dict[str, Any]:
    """
    Create a standardized success result.

    Args:
        prediction: The main prediction/result
        **additional_data: Additional data to include

    Returns:
        Formatted result dictionary
    """
    return {
        "prediction": prediction,
        "success": True,
        **additional_data
    }


def create_error_result(error_message: str, **additional_data) -> Dict[str, Any]:
    """
    Create a standardized error result.

    Args:
        error_message: The error message
        **additional_data: Additional error context

    Returns:
        Formatted error dictionary
    """
    return {
        "error": error_message,
        "success": False,
        **additional_data
    }
