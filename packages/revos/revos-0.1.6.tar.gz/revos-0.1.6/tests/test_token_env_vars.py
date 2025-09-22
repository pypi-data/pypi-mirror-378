#!/usr/bin/env python3
"""
Test script to verify that TokenManager picks up custom environment variables from .env files.

This script demonstrates:
1. Creating a test .env file with custom TOKEN_ variables
2. Loading the configuration and verifying the values are picked up
3. Testing both default and custom prefix scenarios
"""

import os
import tempfile
import pytest
from pathlib import Path
from revos.config.token import TokenManagerConfig
from revos.config.main import RevosMainConfig
from revos.config.factory import create_config_with_prefixes


class TestTokenManagerEnvVars:
    """Test class for TokenManager environment variable loading."""

    def test_default_token_config(self):
        """Test TokenManager with default TOKEN_ prefix."""
        # Create a temporary .env file with custom TOKEN_ variables
        env_content = """
# Custom token management settings
TOKEN_REFRESH_INTERVAL_MINUTES=30
TOKEN_MAX_FAILURES_BEFORE_FALLBACK=3
TOKEN_ENABLE_PERIODIC_REFRESH=false
TOKEN_ENABLE_FALLBACK=false
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            env_file = f.name
        
        try:
            # Test TokenManagerConfig directly
            config = TokenManagerConfig(_env_file=env_file)
            
            # Verify the values match our .env file
            assert config.refresh_interval_minutes == 30
            assert config.max_failures_before_fallback == 3
            assert config.enable_periodic_refresh == False
            assert config.enable_fallback == False
            
        finally:
            # Clean up
            os.unlink(env_file)

    def test_custom_prefix_config(self):
        """Test TokenManager with custom prefix."""
        # Create a temporary .env file with custom AUTH_ variables
        env_content = """
# Custom token management settings with AUTH_ prefix
AUTH_REFRESH_INTERVAL_MINUTES=60
AUTH_MAX_FAILURES_BEFORE_FALLBACK=5
AUTH_ENABLE_PERIODIC_REFRESH=true
AUTH_ENABLE_FALLBACK=true

# Required Revos credentials for the full config
REVOS_CLIENT_ID=test_client_id
REVOS_CLIENT_SECRET=test_client_secret
REVOS_TOKEN_URL=https://test.example.com/oauth/token
REVOS_BASE_URL=https://test.example.com/api
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            env_file = f.name
        
        try:
            # Test with custom prefix
            config = create_config_with_prefixes(
                revo_prefix="REVOS_",
                llm_prefix="LLM_",
                logging_prefix="LOG_",
                token_prefix="AUTH_",
                _env_file=env_file
            )
            
            token_config = config.token_manager
            
            # Verify the values match our .env file
            assert token_config.refresh_interval_minutes == 60
            assert token_config.max_failures_before_fallback == 5
            assert token_config.enable_periodic_refresh == True
            assert token_config.enable_fallback == True
            
        finally:
            # Clean up
            os.unlink(env_file)

    def test_main_config_with_env(self):
        """Test RevosMainConfig with .env file."""
        # Create a temporary .env file with mixed configuration
        env_content = """
# Mixed configuration for main config test
TOKEN_REFRESH_INTERVAL_MINUTES=45
TOKEN_MAX_FAILURES_BEFORE_FALLBACK=2
TOKEN_ENABLE_PERIODIC_REFRESH=true
TOKEN_ENABLE_FALLBACK=true

# Some other configs to test the full system
REVOS_CLIENT_ID=test_client_id
REVOS_CLIENT_SECRET=test_client_secret
REVOS_TOKEN_URL=https://test.example.com/oauth/token
REVOS_BASE_URL=https://test.example.com/api

LOG_LEVEL=DEBUG
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            env_file = f.name
        
        try:
            # Test RevosMainConfig
            config = RevosMainConfig(_env_file=env_file)
            
            # Verify token manager values
            assert config.token_manager.refresh_interval_minutes == 45
            assert config.token_manager.max_failures_before_fallback == 2
            assert config.token_manager.enable_periodic_refresh == True
            assert config.token_manager.enable_fallback == True
            
            # Verify other configs are also loaded
            assert config.revos.client_id == "test_client_id"
            assert config.logging.level == "DEBUG"
            
        finally:
            # Clean up
            os.unlink(env_file)

    def test_env_file_loading(self):
        """Test that .env files are actually loaded into environment."""
        # Create a temporary .env file
        env_content = """
# Test environment variables
TEST_TOKEN_REFRESH_INTERVAL_MINUTES=90
TEST_TOKEN_MAX_FAILURES_BEFORE_FALLBACK=7
TEST_TOKEN_ENABLE_PERIODIC_REFRESH=false
TEST_TOKEN_ENABLE_FALLBACK=false

# Required Revos credentials for the full config
REVOS_CLIENT_ID=test_client_id
REVOS_CLIENT_SECRET=test_client_secret
REVOS_TOKEN_URL=https://test.example.com/oauth/token
REVOS_BASE_URL=https://test.example.com/api
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            env_file = f.name
        
        try:
            # Test custom prefix that matches our env vars
            config = create_config_with_prefixes(
                revo_prefix="REVOS_",
                llm_prefix="LLM_",
                logging_prefix="LOG_",
                token_prefix="TEST_TOKEN_",
                _env_file=env_file
            )
            
            token_config = config.token_manager
            
            # Verify the values
            assert token_config.refresh_interval_minutes == 90
            assert token_config.max_failures_before_fallback == 7
            assert token_config.enable_periodic_refresh == False
            assert token_config.enable_fallback == False
            
        finally:
            # Clean up
            os.unlink(env_file)

    def test_token_config_defaults(self):
        """Test that TokenManagerConfig uses correct defaults when no .env file is provided."""
        # Test that the TokenManagerConfig class has the expected default values
        # by checking the field definitions directly
        from revos.config.token import TokenManagerConfig
        
        # Check that the field defaults are as expected
        fields = TokenManagerConfig.model_fields
        
        # Verify field defaults
        assert fields['refresh_interval_minutes'].default == 45
        assert fields['max_failures_before_fallback'].default == 1
        assert fields['enable_periodic_refresh'].default == True
        assert fields['enable_fallback'].default == True

    def test_token_config_validation(self):
        """Test that TokenManagerConfig validates input values correctly."""
        # Test with invalid values that should be caught by validation
        with pytest.raises(ValueError):
            TokenManagerConfig(refresh_interval_minutes=4)  # Below minimum of 5
        
        with pytest.raises(ValueError):
            TokenManagerConfig(refresh_interval_minutes=1441)  # Above maximum of 1440
        
        with pytest.raises(ValueError):
            TokenManagerConfig(max_failures_before_fallback=0)  # Below minimum of 1
        
        with pytest.raises(ValueError):
            TokenManagerConfig(max_failures_before_fallback=11)  # Above maximum of 10

    def test_multiple_env_files(self):
        """Test loading from multiple .env files with different prefixes."""
        # Create first .env file with CUSTOM_TOKEN_ prefix
        env_content_1 = """
CUSTOM_TOKEN_REFRESH_INTERVAL_MINUTES=30
CUSTOM_TOKEN_MAX_FAILURES_BEFORE_FALLBACK=2
CUSTOM_TOKEN_ENABLE_PERIODIC_REFRESH=false
CUSTOM_TOKEN_ENABLE_FALLBACK=false
"""
        
        # Create second .env file with AUTH_ prefix  
        env_content_2 = """
AUTH_REFRESH_INTERVAL_MINUTES=60
AUTH_MAX_FAILURES_BEFORE_FALLBACK=4
AUTH_ENABLE_PERIODIC_REFRESH=true
AUTH_ENABLE_FALLBACK=true

# Required Revos credentials for the full config
REVOS_CLIENT_ID=test_client_id
REVOS_CLIENT_SECRET=test_client_secret
REVOS_TOKEN_URL=https://test.example.com/oauth/token
REVOS_BASE_URL=https://test.example.com/api
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f1:
            f1.write(env_content_1)
            env_file_1 = f1.name
            
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f2:
            f2.write(env_content_2)
            env_file_2 = f2.name
        
        try:
            # Test first file with CUSTOM_TOKEN_ prefix using custom config
            from pydantic_settings import BaseSettings, SettingsConfigDict
            
            class CustomTokenConfig(BaseSettings):
                model_config = SettingsConfigDict(
                    env_prefix="CUSTOM_TOKEN_",
                    env_file=env_file_1,
                    env_file_encoding="utf-8",
                    case_sensitive=False,
                    extra="ignore"
                )
                
                refresh_interval_minutes: int = 45
                max_failures_before_fallback: int = 1
                enable_periodic_refresh: bool = True
                enable_fallback: bool = True
            
            config1 = CustomTokenConfig()
            assert config1.refresh_interval_minutes == 30
            assert config1.max_failures_before_fallback == 2
            assert config1.enable_periodic_refresh == False
            assert config1.enable_fallback == False
            
            # Test second file with AUTH_ prefix
            config2 = create_config_with_prefixes(
                revo_prefix="REVOS_",
                llm_prefix="LLM_",
                logging_prefix="LOG_", 
                token_prefix="AUTH_",
                _env_file=env_file_2
            )
            assert config2.token_manager.refresh_interval_minutes == 60
            assert config2.token_manager.max_failures_before_fallback == 4
            assert config2.token_manager.enable_periodic_refresh == True
            assert config2.token_manager.enable_fallback == True
            
        finally:
            # Clean up
            os.unlink(env_file_1)
            os.unlink(env_file_2)


if __name__ == "__main__":
    # Allow running the tests directly
    pytest.main([__file__, "-v"])
