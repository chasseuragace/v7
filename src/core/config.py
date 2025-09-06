"""
Configuration management for the Statement-to-Reality System.

This module handles all configuration settings, environment variables,
and system defaults in a centralized manner.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path


@dataclass
class LLMConfig:
    """Configuration for LLM providers."""
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    default_provider: str = "openai"
    timeout: int = 30
    max_retries: int = 3
    temperature: float = 0.1
    max_tokens: int = 4000

    @classmethod
    def from_env(cls) -> 'LLMConfig':
        """Create configuration from environment variables."""
        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            default_provider=os.getenv("DEFAULT_LLM_PROVIDER", "openai"),
            timeout=int(os.getenv("LLM_TIMEOUT", "30")),
            max_retries=int(os.getenv("LLM_MAX_RETRIES", "3")),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "4000"))
        )


@dataclass
class CloudConfig:
    """Configuration for cloud providers."""
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    
    gcp_credentials_path: Optional[str] = None
    gcp_project_id: Optional[str] = None
    gcp_region: str = "us-central1"
    
    azure_client_id: Optional[str] = None
    azure_client_secret: Optional[str] = None
    azure_tenant_id: Optional[str] = None
    
    vercel_token: Optional[str] = None
    netlify_auth_token: Optional[str] = None
    
    default_provider: str = "vercel"
    deployment_timeout: int = 300

    @classmethod
    def from_env(cls) -> 'CloudConfig':
        """Create configuration from environment variables."""
        return cls(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            aws_region=os.getenv("AWS_REGION", "us-east-1"),
            
            gcp_credentials_path=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
            gcp_project_id=os.getenv("GCP_PROJECT_ID"),
            gcp_region=os.getenv("GCP_REGION", "us-central1"),
            
            azure_client_id=os.getenv("AZURE_CLIENT_ID"),
            azure_client_secret=os.getenv("AZURE_CLIENT_SECRET"),
            azure_tenant_id=os.getenv("AZURE_TENANT_ID"),
            
            vercel_token=os.getenv("VERCEL_TOKEN"),
            netlify_auth_token=os.getenv("NETLIFY_AUTH_TOKEN"),
            
            default_provider=os.getenv("DEFAULT_CLOUD_PROVIDER", "vercel"),
            deployment_timeout=int(os.getenv("DEPLOYMENT_TIMEOUT", "300"))
        )


@dataclass
class CodeGenConfig:
    """Configuration for code generation."""
    supported_languages: List[str] = field(default_factory=lambda: [
        "python", "rust", "go", "typescript", "java", "cpp"
    ])
    default_language: str = "python"
    output_directory: str = "generated"
    template_directory: str = "templates"
    include_tests: bool = True
    include_documentation: bool = True
    code_style: str = "standard"

    @classmethod
    def from_env(cls) -> 'CodeGenConfig':
        """Create configuration from environment variables."""
        return cls(
            default_language=os.getenv("DEFAULT_LANGUAGE", "python"),
            output_directory=os.getenv("OUTPUT_DIRECTORY", "generated"),
            template_directory=os.getenv("TEMPLATE_DIRECTORY", "templates"),
            include_tests=os.getenv("INCLUDE_TESTS", "true").lower() == "true",
            include_documentation=os.getenv("INCLUDE_DOCS", "true").lower() == "true",
            code_style=os.getenv("CODE_STYLE", "standard")
        )


@dataclass
class SystemConfig:
    """Main system configuration."""
    llm: LLMConfig = field(default_factory=LLMConfig)
    cloud: CloudConfig = field(default_factory=CloudConfig)
    codegen: CodeGenConfig = field(default_factory=CodeGenConfig)
    
    # System settings
    debug: bool = False
    log_level: str = "INFO"
    max_processing_time: int = 600
    enable_caching: bool = True
    cache_directory: str = ".cache"
    
    # Security settings
    enable_sandboxing: bool = True
    max_code_size: int = 1024 * 1024  # 1MB
    allowed_imports: List[str] = field(default_factory=lambda: [
        "os", "sys", "json", "time", "datetime", "re", "math", "random",
        "requests", "flask", "fastapi", "express", "axios"
    ])
    
    # Performance settings
    max_concurrent_generations: int = 5
    generation_timeout: int = 120
    
    @classmethod
    def from_env(cls) -> 'SystemConfig':
        """Create configuration from environment variables."""
        config = cls()
        config.llm = LLMConfig.from_env()
        config.cloud = CloudConfig.from_env()
        config.codegen = CodeGenConfig.from_env()
        
        config.debug = os.getenv("DEBUG", "false").lower() == "true"
        config.log_level = os.getenv("LOG_LEVEL", "INFO")
        config.max_processing_time = int(os.getenv("MAX_PROCESSING_TIME", "600"))
        config.enable_caching = os.getenv("ENABLE_CACHING", "true").lower() == "true"
        config.cache_directory = os.getenv("CACHE_DIRECTORY", ".cache")
        
        config.enable_sandboxing = os.getenv("ENABLE_SANDBOXING", "true").lower() == "true"
        config.max_code_size = int(os.getenv("MAX_CODE_SIZE", str(1024 * 1024)))
        
        config.max_concurrent_generations = int(os.getenv("MAX_CONCURRENT_GENERATIONS", "5"))
        config.generation_timeout = int(os.getenv("GENERATION_TIMEOUT", "120"))
        
        return config

    def validate(self) -> List[str]:
        """Validate configuration and return list of issues."""
        issues = []
        
        # Check LLM configuration
        if not self.llm.openai_api_key and not self.llm.anthropic_api_key:
            issues.append("No LLM API keys configured")
        
        # Check directories exist
        for directory in [self.codegen.output_directory, self.cache_directory]:
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                except Exception as e:
                    issues.append(f"Cannot create directory {directory}: {e}")
        
        # Check numeric values
        if self.max_processing_time <= 0:
            issues.append("max_processing_time must be positive")
        
        if self.generation_timeout <= 0:
            issues.append("generation_timeout must be positive")
        
        if self.max_concurrent_generations <= 0:
            issues.append("max_concurrent_generations must be positive")
        
        return issues

    def get_available_providers(self) -> Dict[str, bool]:
        """Get available cloud providers based on configuration."""
        return {
            "aws": bool(self.cloud.aws_access_key_id and self.cloud.aws_secret_access_key),
            "gcp": bool(self.cloud.gcp_credentials_path and self.cloud.gcp_project_id),
            "azure": bool(self.cloud.azure_client_id and self.cloud.azure_client_secret),
            "vercel": bool(self.cloud.vercel_token),
            "netlify": bool(self.cloud.netlify_auth_token)
        }

    def get_available_llm_providers(self) -> Dict[str, bool]:
        """Get available LLM providers based on configuration."""
        return {
            "openai": bool(self.llm.openai_api_key),
            "anthropic": bool(self.llm.anthropic_api_key)
        }


# Global configuration instance
_config: Optional[SystemConfig] = None


def get_config() -> SystemConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = SystemConfig.from_env()
    return _config


def set_config(config: SystemConfig) -> None:
    """Set the global configuration instance."""
    global _config
    _config = config


def reload_config() -> SystemConfig:
    """Reload configuration from environment."""
    global _config
    _config = SystemConfig.from_env()
    return _config
