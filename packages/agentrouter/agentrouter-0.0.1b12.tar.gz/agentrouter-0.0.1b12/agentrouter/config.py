"""
Configuration management for AgentRouter SDK
Provides centralized configuration for network, execution, and retry settings
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator


class NetworkConfig(BaseModel):
    """
    Network and API configuration settings
    """
    api_timeout: float = Field(
        default=60.0,
        ge=5.0,
        le=300.0,
        description="API request timeout in seconds (5-300)"
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum number of retry attempts (0-10)"
    )
    retry_delay: float = Field(
        default=1.0,
        ge=0.1,
        le=60.0,
        description="Initial delay between retries in seconds (0.1-60)"
    )
    retry_multiplier: float = Field(
        default=2.0,
        ge=1.0,
        le=10.0,
        description="Exponential backoff multiplier for retries (1-10)"
    )
    retry_max_wait: float = Field(
        default=60.0,
        ge=1.0,
        le=300.0,
        description="Maximum wait time between retries in seconds (1-300)"
    )


class ExecutionConfig(BaseModel):
    """
    Agent execution configuration settings
    """
    max_iterations: int = Field(
        default=30,
        ge=3,
        le=50,
        description="Maximum workflow iterations (3-50)"
    )
    worker_timeout: float = Field(
        default=60.0,
        ge=5.0,
        le=300.0,
        description="Worker execution timeout in seconds (5-300)"
    )


class AgentConfiguration(BaseModel):
    """
    Complete agent configuration combining network and execution settings
    """
    network: NetworkConfig = Field(default_factory=NetworkConfig)
    execution: ExecutionConfig = Field(default_factory=ExecutionConfig)
    
    @classmethod
    def create_with_overrides(
        cls,
        max_iterations: Optional[int] = None,
        api_timeout: Optional[float] = None,
        worker_timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        retry_delay: Optional[float] = None,
        retry_multiplier: Optional[float] = None,
        retry_max_wait: Optional[float] = None
    ) -> 'AgentConfiguration':
        """
        Create configuration with specific overrides
        
        Args:
            max_iterations: Maximum workflow iterations (3-50)
            api_timeout: API request timeout in seconds (5-300)
            worker_timeout: Worker execution timeout in seconds (5-300)
            max_retries: Maximum retry attempts (0-10)
            retry_delay: Initial retry delay in seconds (0.1-60)
            retry_multiplier: Exponential backoff multiplier (1-10)
            retry_max_wait: Maximum wait between retries (1-300)
            
        Returns:
            AgentConfiguration instance with overrides applied
        """
        network_kwargs = {}
        if api_timeout is not None:
            network_kwargs['api_timeout'] = api_timeout
        if max_retries is not None:
            network_kwargs['max_retries'] = max_retries
        if retry_delay is not None:
            network_kwargs['retry_delay'] = retry_delay
        if retry_multiplier is not None:
            network_kwargs['retry_multiplier'] = retry_multiplier
        if retry_max_wait is not None:
            network_kwargs['retry_max_wait'] = retry_max_wait
        
        execution_kwargs = {}
        if max_iterations is not None:
            execution_kwargs['max_iterations'] = max_iterations
        if worker_timeout is not None:
            execution_kwargs['worker_timeout'] = worker_timeout
        
        return cls(
            network=NetworkConfig(**network_kwargs),
            execution=ExecutionConfig(**execution_kwargs)
        )


# Default configuration instance
DEFAULT_CONFIG = AgentConfiguration()


def get_default_config() -> AgentConfiguration:
    """
    Get the default configuration
    
    Returns:
        Default AgentConfiguration instance
    """
    return DEFAULT_CONFIG


def validate_config(config: AgentConfiguration) -> None:
    """
    Validate a configuration instance
    
    Args:
        config: Configuration to validate
        
    Raises:
        ValueError: If configuration is invalid
    """
    # Pydantic handles most validation, but we can add custom checks here
    if config.network.retry_delay >= config.network.retry_max_wait:
        raise ValueError(
            f"retry_delay ({config.network.retry_delay}) must be less than "
            f"retry_max_wait ({config.network.retry_max_wait})"
        )
    
    if config.execution.worker_timeout < config.network.api_timeout:
        # Warning, not error - worker timeout should generally be >= api timeout
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(
            f"worker_timeout ({config.execution.worker_timeout}s) is less than "
            f"api_timeout ({config.network.api_timeout}s) - this may cause issues"
        )