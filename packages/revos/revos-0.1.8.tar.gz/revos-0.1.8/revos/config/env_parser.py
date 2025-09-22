"""
Custom .env parser for multiple LLM models.

This module provides functionality to parse environment variables
and group them by model name to create LLM model configurations.
"""

import os
import re
from typing import Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path

if TYPE_CHECKING:
    from .llm_models import LLMModelConfig


class EnvModelParser:
    """Parser for environment variables that groups them by model name."""
    
    def __init__(self, env_prefix: str = "LLM_MODELS_", env_file: Optional[str] = None):
        """
        Initialize the parser.
        
        Args:
            env_prefix: Prefix for environment variables (e.g., "LLM_MODELS_")
            env_file: Path to .env file to load
        """
        self.env_prefix = env_prefix
        self.env_file = env_file
        self._load_env_file()
    
    def _load_env_file(self):
        """Load environment variables from .env file if specified."""
        if self.env_file and Path(self.env_file).exists():
            with open(self.env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        # Remove quotes if present
                        value = value.strip('"\'')
                        os.environ[key] = value
    
    def parse_models(self) -> Dict[str, 'LLMModelConfig']:
        """
        Parse environment variables and group them by model name.
        
        Expected format:
        LLM_MODELS_{MODEL_NAME}_{PARAMETER} = value
        
        Example:
        LLM_MODELS_CLAUDE_4_SONNET_MODEL = claude_4_sonnet
        LLM_MODELS_CLAUDE_4_SONNET_TEMPERATURE = 0.3
        LLM_MODELS_CLAUDE_4_SONNET_MAX_TOKENS = 4000
        LLM_MODELS_GPT_4_MODEL = gpt-4
        LLM_MODELS_GPT_4_TEMPERATURE = 0.1
        
        Returns:
            Dict[str, LLMModelConfig]: Dictionary of model configurations
        """
        models = {}
        env_vars = {}
        
        # Collect all environment variables with the prefix
        for key, value in os.environ.items():
            if key.startswith(self.env_prefix):
                # Remove prefix
                remaining = key[len(self.env_prefix):]
                
                # Find the model name by looking for common parameter suffixes
                # Common parameter names that should be at the end
                param_suffixes = [
                    '_MODEL', '_TEMPERATURE', '_MAX_TOKENS', '_TOP_P', 
                    '_FREQUENCY_PENALTY', '_PRESENCE_PENALTY', '_DESCRIPTION',
                    '_TIMEOUT', '_STREAM', '_STREAMING'
                ]
                
                model_name = None
                param = None
                
                for suffix in param_suffixes:
                    if remaining.endswith(suffix):
                        model_name = remaining[:-len(suffix)]
                        param = suffix[1:].lower()  # Remove leading underscore and convert to lowercase
                        break
                
                if model_name and param:
                    if model_name not in env_vars:
                        env_vars[model_name] = {}
                    env_vars[model_name][param] = value
        
        # Create LLMModelConfig objects for each model
        for model_name, params in env_vars.items():
            try:
                # Convert string values to appropriate types
                config_dict = self._convert_params(params)
                
                # Import LLMModelConfig at runtime to avoid circular import
                from .llm_models import LLMModelConfig
                
                # Create LLMModelConfig
                model_config = LLMModelConfig(**config_dict)
                models[model_name.lower()] = model_config
                
            except Exception as e:
                # Skip invalid configurations
                print(f"Warning: Failed to create config for model '{model_name}': {e}")
                continue
        
        return models
    
    def _convert_params(self, params: Dict[str, str]) -> Dict[str, Any]:
        """
        Convert string parameters to appropriate types.
        
        Args:
            params: Dictionary of string parameters
            
        Returns:
            Dict[str, Any]: Converted parameters
        """
        converted = {}
        
        for key, value in params.items():
            # Convert to appropriate type
            if key in ['temperature', 'top_p', 'frequency_penalty', 'presence_penalty']:
                try:
                    converted[key] = float(value)
                except ValueError:
                    converted[key] = 0.0
            elif key in ['max_tokens', 'timeout']:
                try:
                    converted[key] = int(value)
                except ValueError:
                    converted[key] = None
            elif key in ['stream', 'streaming']:
                converted[key] = value.lower() in ('true', '1', 'yes', 'on')
            elif key == 'model':
                converted[key] = value
            elif key == 'description':
                converted[key] = value
            else:
                # For custom parameters, try to convert to appropriate type
                converted[key] = self._smart_convert(value)
        
        return converted
    
    def _smart_convert(self, value: str) -> Any:
        """
        Smart conversion of string values to appropriate types.
        
        Args:
            value: String value to convert
            
        Returns:
            Converted value
        """
        # Try boolean
        if value.lower() in ('true', 'false', '1', '0', 'yes', 'no', 'on', 'off'):
            return value.lower() in ('true', '1', 'yes', 'on')
        
        # Try integer
        try:
            return int(value)
        except ValueError:
            pass
        
        # Try float
        try:
            return float(value)
        except ValueError:
            pass
        
        # Return as string
        return value


def parse_models_from_env(env_prefix: str = "LLM_MODELS_", env_file: Optional[str] = None) -> Dict[str, 'LLMModelConfig']:
    """
    Convenience function to parse models from environment variables.
    
    Args:
        env_prefix: Prefix for environment variables
        env_file: Path to .env file to load
        
    Returns:
        Dict[str, LLMModelConfig]: Dictionary of model configurations
    """
    parser = EnvModelParser(env_prefix, env_file)
    return parser.parse_models()
