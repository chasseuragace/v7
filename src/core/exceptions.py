"""
Custom exceptions for the Statement-to-Reality System.

This module defines all custom exceptions used throughout the system,
providing clear error handling and debugging capabilities.
"""


class StatementRealityError(Exception):
    """Base exception for all Statement-to-Reality System errors."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConversationProcessingError(StatementRealityError):
    """Raised when conversation processing fails."""
    pass


class StatementParsingError(StatementRealityError):
    """Raised when statement parsing fails."""
    pass


class ArchitectureInferenceError(StatementRealityError):
    """Raised when architecture inference fails."""
    pass


class CodeGenerationError(StatementRealityError):
    """Raised when code generation fails."""
    pass


class DeploymentError(StatementRealityError):
    """Raised when deployment operations fail."""
    pass


class LLMIntegrationError(StatementRealityError):
    """Raised when LLM API calls fail."""
    pass


class ValidationError(StatementRealityError):
    """Raised when data validation fails."""
    pass


class ConfigurationError(StatementRealityError):
    """Raised when configuration is invalid or missing."""
    pass


class UnsupportedLanguageError(CodeGenerationError):
    """Raised when an unsupported programming language is requested."""
    pass


class UnsupportedProviderError(DeploymentError):
    """Raised when an unsupported cloud provider is requested."""
    pass


class SystemEvolutionError(StatementRealityError):
    """Raised when system evolution fails."""
    pass


class RecursiveProcessingError(StatementRealityError):
    """Raised when recursive self-processing fails."""
    pass
