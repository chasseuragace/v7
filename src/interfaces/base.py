"""
Abstract base interfaces for the Statement-to-Reality System.

This module defines the core interfaces that all concrete implementations
must follow, ensuring consistency and enabling dependency injection.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, AsyncIterator
from src.core.models import (
    Conversation, Statement, SystemRequirements, SystemArchitecture,
    GeneratedCode, DeploymentConfiguration, RunningSystem, ProcessingResult
)


class ConversationalParser(ABC):
    """Abstract interface for parsing conversational statements."""
    
    @abstractmethod
    def parse_statements(self, conversation: Conversation) -> SystemRequirements:
        """
        Parse conversation statements into structured requirements.
        
        Args:
            conversation: The conversation to parse
            
        Returns:
            SystemRequirements: Extracted requirements
            
        Raises:
            StatementParsingError: If parsing fails
        """
        pass
    
    @abstractmethod
    def extract_entities(self, text: str) -> List[str]:
        """
        Extract entities from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of extracted entities
        """
        pass
    
    @abstractmethod
    def classify_statement(self, statement: Statement) -> str:
        """
        Classify a statement into categories.
        
        Args:
            statement: Statement to classify
            
        Returns:
            Classification category
        """
        pass


class ArchitecturalInference(ABC):
    """Abstract interface for inferring system architecture."""
    
    @abstractmethod
    def infer_architecture(self, requirements: SystemRequirements) -> SystemArchitecture:
        """
        Infer system architecture from requirements.
        
        Args:
            requirements: System requirements
            
        Returns:
            SystemArchitecture: Inferred architecture
            
        Raises:
            ArchitectureInferenceError: If inference fails
        """
        pass
    
    @abstractmethod
    def suggest_patterns(self, requirements: SystemRequirements) -> List[str]:
        """
        Suggest architectural patterns for requirements.
        
        Args:
            requirements: System requirements
            
        Returns:
            List of suggested patterns
        """
        pass
    
    @abstractmethod
    def validate_architecture(self, architecture: SystemArchitecture) -> List[str]:
        """
        Validate architecture and return issues.
        
        Args:
            architecture: Architecture to validate
            
        Returns:
            List of validation issues
        """
        pass


class MultiLanguageGenerator(ABC):
    """Abstract interface for multi-language code generation."""
    
    @abstractmethod
    def generate_code(
        self, 
        architecture: SystemArchitecture, 
        language: str, 
        framework: Optional[str] = None
    ) -> GeneratedCode:
        """
        Generate code for the given architecture.
        
        Args:
            architecture: System architecture
            language: Target programming language
            framework: Optional framework to use
            
        Returns:
            GeneratedCode: Generated code artifacts
            
        Raises:
            CodeGenerationError: If generation fails
            UnsupportedLanguageError: If language not supported
        """
        pass
    
    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported programming languages.
        
        Returns:
            List of supported language names
        """
        pass
    
    @abstractmethod
    def get_supported_frameworks(self, language: str) -> List[str]:
        """
        Get supported frameworks for a language.
        
        Args:
            language: Programming language
            
        Returns:
            List of supported frameworks
        """
        pass
    
    @abstractmethod
    def validate_code(self, code: GeneratedCode) -> List[str]:
        """
        Validate generated code.
        
        Args:
            code: Generated code to validate
            
        Returns:
            List of validation issues
        """
        pass


class CloudDeploymentEngine(ABC):
    """Abstract interface for cloud deployment."""
    
    @abstractmethod
    def generate_deployment_config(
        self, 
        code: GeneratedCode, 
        provider: str
    ) -> DeploymentConfiguration:
        """
        Generate deployment configuration for a provider.
        
        Args:
            code: Generated code to deploy
            provider: Cloud provider name
            
        Returns:
            DeploymentConfiguration: Deployment configuration
            
        Raises:
            UnsupportedProviderError: If provider not supported
        """
        pass
    
    @abstractmethod
    async def deploy(
        self, 
        code: GeneratedCode, 
        config: DeploymentConfiguration
    ) -> RunningSystem:
        """
        Deploy code using the given configuration.
        
        Args:
            code: Code to deploy
            config: Deployment configuration
            
        Returns:
            RunningSystem: Information about deployed system
            
        Raises:
            DeploymentError: If deployment fails
        """
        pass
    
    @abstractmethod
    def get_supported_providers(self) -> List[str]:
        """
        Get list of supported cloud providers.
        
        Returns:
            List of supported provider names
        """
        pass
    
    @abstractmethod
    async def check_deployment_status(self, system: RunningSystem) -> str:
        """
        Check the status of a deployed system.
        
        Args:
            system: Running system to check
            
        Returns:
            Current deployment status
        """
        pass


class LLMProvider(ABC):
    """Abstract interface for LLM providers."""
    
    @abstractmethod
    async def generate_text(
        self, 
        prompt: str, 
        max_tokens: int = 1000,
        temperature: float = 0.1
    ) -> str:
        """
        Generate text using the LLM.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Generation temperature
            
        Returns:
            Generated text
            
        Raises:
            LLMIntegrationError: If generation fails
        """
        pass
    
    @abstractmethod
    async def generate_structured_output(
        self, 
        prompt: str, 
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate structured output matching a schema.
        
        Args:
            prompt: Input prompt
            schema: Expected output schema
            
        Returns:
            Structured output matching schema
            
        Raises:
            LLMIntegrationError: If generation fails
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get the name of this LLM provider.
        
        Returns:
            Provider name
        """
        pass


class SystemEvolution(ABC):
    """Abstract interface for system evolution."""
    
    @abstractmethod
    def evolve_system(
        self, 
        current_system: RunningSystem, 
        evolution_statements: List[Statement]
    ) -> ProcessingResult:
        """
        Evolve an existing system with new statements.
        
        Args:
            current_system: Current running system
            evolution_statements: New statements for evolution
            
        Returns:
            ProcessingResult: Result of evolution
            
        Raises:
            SystemEvolutionError: If evolution fails
        """
        pass
    
    @abstractmethod
    def analyze_evolution_impact(
        self, 
        current_architecture: SystemArchitecture,
        new_requirements: SystemRequirements
    ) -> Dict[str, Any]:
        """
        Analyze the impact of evolution on existing architecture.
        
        Args:
            current_architecture: Current system architecture
            new_requirements: New requirements from evolution
            
        Returns:
            Impact analysis results
        """
        pass


class StatementToRealitySystem(ABC):
    """Main interface for the complete Statement-to-Reality System."""
    
    @abstractmethod
    def manifest_from_conversation(self, conversation: Conversation) -> ProcessingResult:
        """
        Transform conversation into running system.
        
        Args:
            conversation: Input conversation
            
        Returns:
            ProcessingResult: Complete processing result
            
        Raises:
            ConversationProcessingError: If processing fails
        """
        pass
    
    @abstractmethod
    async def manifest_from_conversation_async(
        self, 
        conversation: Conversation
    ) -> AsyncIterator[ProcessingResult]:
        """
        Transform conversation into running system asynchronously.
        
        Args:
            conversation: Input conversation
            
        Yields:
            ProcessingResult: Incremental processing results
        """
        pass
    
    @abstractmethod
    def process_recursive_statement(
        self, 
        statement: str
    ) -> ProcessingResult:
        """
        Process a statement that references the system itself.
        
        Args:
            statement: Self-referential statement
            
        Returns:
            ProcessingResult: Result of recursive processing
            
        Raises:
            RecursiveProcessingError: If recursive processing fails
        """
        pass


class CacheProvider(ABC):
    """Abstract interface for caching providers."""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete value from cache."""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all cache entries."""
        pass


class MetricsCollector(ABC):
    """Abstract interface for metrics collection."""
    
    @abstractmethod
    def record_processing_time(self, operation: str, duration: float) -> None:
        """Record processing time for an operation."""
        pass
    
    @abstractmethod
    def increment_counter(self, metric: str, tags: Dict[str, str] = None) -> None:
        """Increment a counter metric."""
        pass
    
    @abstractmethod
    def record_gauge(self, metric: str, value: float, tags: Dict[str, str] = None) -> None:
        """Record a gauge metric."""
        pass
    
    @abstractmethod
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of collected metrics."""
        pass
