"""
Configuration Factory Functions

This module provides factory functions for creating configurations
with custom settings, prefixes, and other options.
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import SettingsConfigDict

from .api import RevosConfig
from .llm_models import LLMModelsConfig
from .logging import LoggingConfig
from .token import TokenManagerConfig
from .main import RevosMainConfig


def create_config_with_prefixes(
    revo_prefix: str = "REVOS_",
    llm_prefix: str = "LLM_", 
    logging_prefix: str = "LOG_",
    token_prefix: str = "TOKEN_",
    **kwargs
) -> RevosMainConfig:
    """
    Create a RevosMainConfig with custom environment variable prefixes.
    
    Args:
        revo_prefix: Prefix for Revos API environment variables (default: "REVOS_")
        llm_prefix: Prefix for LLM environment variables (default: "LLM_")
        logging_prefix: Prefix for logging environment variables (default: "LOG_")
        token_prefix: Prefix for token management environment variables (default: "TOKEN_")
        **kwargs: Additional arguments passed to RevosMainConfig
        
    Returns:
        RevosMainConfig instance with custom prefixes
        
    Raises:
        ValueError: If any prefixes are the same (to avoid variable name conflicts)
        
    Example:
        # Use custom prefixes
        config = create_config_with_prefixes(
            revo_prefix="MY_API_",
            llm_prefix="AI_",
            logging_prefix="LOG_"
        )
        
        # This will look for environment variables like:
        # MY_API_CLIENT_ID, MY_API_CLIENT_SECRET
        # AI_GPT_4_MODEL, AI_GPT_4_TEMPERATURE
        # LOG_LEVEL, LOG_FORMAT
    """
    # Validate that all prefixes are different to avoid variable name conflicts
    prefixes = [revo_prefix, llm_prefix, logging_prefix, token_prefix]
    if len(set(prefixes)) != len(prefixes):
        duplicates = [prefix for prefix in prefixes if prefixes.count(prefix) > 1]
        raise ValueError(
            f"All prefixes must be different to avoid variable name conflicts. "
            f"Found duplicate prefixes: {set(duplicates)}. "
            f"Provided: revo='{revo_prefix}', llm='{llm_prefix}', "
            f"logging='{logging_prefix}', token='{token_prefix}'"
        )
    # Create custom config classes with modified prefixes
    class CustomRevosConfig(RevosConfig):
        model_config = SettingsConfigDict(
            env_prefix=revo_prefix,
            env_file=".env",
            env_file_encoding="utf-8",
            case_sensitive=False,
            extra="ignore"
        )
    
    
    class CustomLoggingConfig(LoggingConfig):
        model_config = SettingsConfigDict(
            env_prefix=logging_prefix,
            env_file=".env",
            env_file_encoding="utf-8",
            case_sensitive=False,
            extra="ignore"
        )
    
    class CustomTokenManagerConfig(TokenManagerConfig):
        model_config = SettingsConfigDict(
            env_prefix=token_prefix,
            env_file=".env",
            env_file_encoding="utf-8",
            case_sensitive=False,
            extra="ignore"
        )
    
    class CustomLLMModelsConfig(LLMModelsConfig):
        model_config = SettingsConfigDict(
            env_prefix=llm_prefix,
            env_file=".env",
            env_file_encoding="utf-8",
            case_sensitive=False,
            extra="ignore"
        )
        
        def __init__(self, **kwargs):
            """Initialize with custom environment parsing using the custom prefix."""
            super().__init__(**kwargs)
            
            # Parse models from environment variables using the custom prefix
            from .env_parser import parse_models_from_env
            env_models = parse_models_from_env(
                env_prefix=llm_prefix,
                env_file=kwargs.get('_env_file', '.env')
            )
            
            # If environment models are found, use ONLY those (override defaults)
            # If no environment models are found, use the hardcoded defaults
            if env_models:
                self.models = env_models
    
    # Create the main config with custom nested configs
    class CustomRevosMainConfig(RevosMainConfig):
        revos: CustomRevosConfig = Field(default_factory=CustomRevosConfig)
        llm_models: CustomLLMModelsConfig = Field(default_factory=CustomLLMModelsConfig)
        logging: CustomLoggingConfig = Field(default_factory=CustomLoggingConfig)
        token_manager: CustomTokenManagerConfig = Field(default_factory=CustomTokenManagerConfig)
        
        def __init__(self, **kwargs):
            # Extract _env_file if provided
            env_file = kwargs.pop('_env_file', None)
            
            # If _env_file is provided, pass it to nested configurations
            if env_file:
                if 'revos' not in kwargs:
                    kwargs['revos'] = CustomRevosConfig(_env_file=env_file)
                if 'llm_models' not in kwargs:
                    kwargs['llm_models'] = CustomLLMModelsConfig(_env_file=env_file)
                if 'logging' not in kwargs:
                    kwargs['logging'] = CustomLoggingConfig(_env_file=env_file)
                if 'token_manager' not in kwargs:
                    kwargs['token_manager'] = CustomTokenManagerConfig(_env_file=env_file)
            
            super().__init__(**kwargs)
    
    return CustomRevosMainConfig(**kwargs)


def create_minimal_config(**kwargs) -> RevosMainConfig:
    """
    Create a minimal configuration with only essential settings.
    
    Args:
        **kwargs: Additional arguments passed to RevosMainConfig
        
    Returns:
        RevosMainConfig instance with minimal settings
    """
    return RevosMainConfig(
        revos=RevosConfig(
            client_id=kwargs.get('client_id', ''),
            client_secret=kwargs.get('client_secret', ''),
            token_url=kwargs.get('token_url', 'https://your-site.com/revo/oauth/token'),
            base_url=kwargs.get('base_url', 'https://your-site.com/revo/llm-api')
        ),
        logging=LoggingConfig(
            level=kwargs.get('log_level', 'INFO')
        ),
        debug=kwargs.get('debug', False)
    )


def create_development_config(**kwargs) -> RevosMainConfig:
    """
    Create a configuration optimized for development.
    
    Args:
        **kwargs: Additional arguments passed to RevosMainConfig
        
    Returns:
        RevosMainConfig instance with development-optimized settings
    """
    return RevosMainConfig(
        revos=RevosConfig(
            client_id=kwargs.get('client_id', 'dev-client-id'),
            client_secret=kwargs.get('client_secret', 'dev-client-secret'),
            token_url=kwargs.get('token_url', 'https://dev-api.example.com/oauth/token'),
            base_url=kwargs.get('base_url', 'https://dev-api.example.com/llm-api'),
            token_buffer_minutes=10,  # Longer buffer for dev
            max_retries=5,  # More retries for dev
            request_timeout=60  # Longer timeout for dev
        ),
        logging=LoggingConfig(
            level='DEBUG',
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            file=kwargs.get('log_file', '/tmp/revo-dev.log')
        ),
        token_manager=TokenManagerConfig(
            refresh_interval_minutes=30,  # More frequent refresh for dev
            enable_periodic_refresh=True,
            enable_fallback=True
        ),
        debug=True
    )


def create_production_config(**kwargs) -> RevosMainConfig:
    """
    Create a configuration optimized for production.
    
    Args:
        **kwargs: Additional arguments passed to RevosMainConfig
        
    Returns:
        RevosMainConfig instance with production-optimized settings
    """
    return RevosMainConfig(
        revos=RevosConfig(
            client_id=kwargs.get('client_id', ''),
            client_secret=kwargs.get('client_secret', ''),
            token_url=kwargs.get('token_url', 'https://api.example.com/oauth/token'),
            base_url=kwargs.get('base_url', 'https://api.example.com/llm-api'),
            token_buffer_minutes=5,  # Shorter buffer for prod
            max_retries=3,  # Standard retries for prod
            request_timeout=30  # Standard timeout for prod
        ),
        logging=LoggingConfig(
            level='WARNING',
            format='%(asctime)s - %(levelname)s - %(message)s',
            file=kwargs.get('log_file', '/var/log/revo/revo.log'),
            max_size=50 * 1024 * 1024,  # 50MB
            backup_count=10
        ),
        token_manager=TokenManagerConfig(
            refresh_interval_minutes=45,  # Standard refresh for prod
            enable_periodic_refresh=True,
            enable_fallback=True
        ),
        debug=False
    )
