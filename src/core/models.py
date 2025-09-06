"""
Core data models for the Statement-to-Reality System.

This module contains all the fundamental data structures used throughout the system,
providing type safety and clear interfaces between components.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enum import Enum


class StatementType(Enum):
    """Types of statements that can be processed."""
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    CONSTRAINT = "constraint"
    BUSINESS_RULE = "business_rule"
    EVOLUTION = "evolution"


class SystemStatus(Enum):
    """Status of a running system."""
    INITIALIZING = "initializing"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"


class DeploymentProvider(Enum):
    """Supported cloud deployment providers."""
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    VERCEL = "vercel"
    NETLIFY = "netlify"
    RAILWAY = "railway"
    RENDER = "render"


@dataclass
class Statement:
    """A single conversational statement with metadata."""
    content: str
    context: Dict[str, Any]
    timestamp: datetime
    speaker: str
    statement_type: StatementType
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate statement after initialization."""
        if not self.content.strip():
            raise ValueError("Statement content cannot be empty")
        if not 0 <= self.confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1")


@dataclass
class Conversation:
    """A collection of statements forming a conversation."""
    statements: List[Statement]
    metadata: Dict[str, Any]
    conversation_id: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate conversation after initialization."""
        if not self.statements:
            raise ValueError("Conversation must contain at least one statement")
        if not self.conversation_id:
            raise ValueError("Conversation ID cannot be empty")

    def add_statement(self, statement: Statement) -> None:
        """Add a new statement to the conversation."""
        self.statements.append(statement)
        self.updated_at = datetime.now()

    def get_statements_by_type(self, statement_type: StatementType) -> List[Statement]:
        """Get all statements of a specific type."""
        return [s for s in self.statements if s.statement_type == statement_type]


@dataclass
class SystemRequirements:
    """Extracted requirements from conversation analysis."""
    functional_requirements: List[str]
    non_functional_requirements: List[str]
    constraints: List[str]
    business_rules: List[str]
    quality_attributes: Dict[str, Any]
    extracted_entities: List[str]
    confidence_score: float = 0.0

    def __post_init__(self):
        """Validate requirements after initialization."""
        if not 0 <= self.confidence_score <= 1:
            raise ValueError("Confidence score must be between 0 and 1")


@dataclass
class SystemComponent:
    """A component in the system architecture."""
    name: str
    component_type: str
    responsibilities: List[str]
    interfaces: List[str]
    dependencies: List[str]
    properties: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate component after initialization."""
        if not self.name.strip():
            raise ValueError("Component name cannot be empty")
        if not self.component_type.strip():
            raise ValueError("Component type cannot be empty")


@dataclass
class SystemArchitecture:
    """Complete system architecture specification."""
    components: List[SystemComponent]
    relationships: List[Dict[str, Any]]
    patterns: List[str]
    quality_attributes: Dict[str, Any]
    technology_stack: Dict[str, List[str]]
    deployment_model: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate architecture after initialization."""
        if not self.components:
            raise ValueError("Architecture must contain at least one component")

    def get_component_by_name(self, name: str) -> Optional[SystemComponent]:
        """Get a component by its name."""
        return next((c for c in self.components if c.name == name), None)

    def get_components_by_type(self, component_type: str) -> List[SystemComponent]:
        """Get all components of a specific type."""
        return [c for c in self.components if c.component_type == component_type]


@dataclass
class GeneratedCode:
    """Generated code artifact."""
    language: str
    framework: str
    files: Dict[str, str]  # filename -> content
    dependencies: List[str]
    entry_point: str
    build_commands: List[str] = field(default_factory=list)
    run_commands: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate generated code after initialization."""
        if not self.language.strip():
            raise ValueError("Language cannot be empty")
        if not self.files:
            raise ValueError("Generated code must contain at least one file")
        if self.entry_point not in self.files:
            raise ValueError("Entry point must be one of the generated files")


@dataclass
class DeploymentConfiguration:
    """Cloud deployment configuration."""
    provider: DeploymentProvider
    service_type: str
    configuration: Dict[str, Any]
    environment_variables: Dict[str, str] = field(default_factory=dict)
    resource_limits: Dict[str, str] = field(default_factory=dict)
    scaling_config: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate deployment configuration after initialization."""
        if not self.service_type.strip():
            raise ValueError("Service type cannot be empty")


@dataclass
class DeploymentInfo:
    """Information about a deployed system."""
    provider: DeploymentProvider
    service_id: str
    endpoints: List[str]
    status: str
    deployed_at: datetime
    configuration: DeploymentConfiguration
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate deployment info after initialization."""
        if not self.service_id.strip():
            raise ValueError("Service ID cannot be empty")


@dataclass
class RunningSystem:
    """A running system instance."""
    deployment_info: DeploymentInfo
    endpoints: List[str]
    monitoring_urls: List[str]
    status: SystemStatus
    created_at: datetime = field(default_factory=datetime.now)
    last_health_check: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate running system after initialization."""
        if not self.endpoints:
            raise ValueError("Running system must have at least one endpoint")

    def is_healthy(self) -> bool:
        """Check if the system is in a healthy state."""
        return self.status in [SystemStatus.RUNNING, SystemStatus.DEPLOYED]

    def update_status(self, status: SystemStatus) -> None:
        """Update the system status."""
        self.status = status
        self.last_health_check = datetime.now()


@dataclass
class ProcessingResult:
    """Result of processing a conversation through the system."""
    conversation: Conversation
    requirements: SystemRequirements
    architecture: SystemArchitecture
    generated_code: Dict[str, GeneratedCode]  # language -> code
    deployment_configs: Dict[str, DeploymentConfiguration]  # provider -> config
    running_system: Optional[RunningSystem] = None
    processing_time: float = 0.0
    success: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_error(self, error: str) -> None:
        """Add an error to the result."""
        self.errors.append(error)
        self.success = False

    def add_warning(self, warning: str) -> None:
        """Add a warning to the result."""
        self.warnings.append(warning)

    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0


# Type aliases for better readability
ConversationId = str
ComponentName = str
LanguageName = str
ProviderName = str
