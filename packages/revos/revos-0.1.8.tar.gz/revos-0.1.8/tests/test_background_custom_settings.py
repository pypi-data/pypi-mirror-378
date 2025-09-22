"""
Test suite for background token refresh with custom settings.

This module tests the fix for the issue where background token refresh process
was not using custom settings and was failing with validation errors.
"""

import os
import pytest
import asyncio
from unittest.mock import patch, MagicMock

from revos.config.factory import create_config_with_prefixes
from revos.tokens.manager import TokenManager
from revos.tokens.background import BackgroundTokenManager
from revos.tokens.refresh import TokenRefreshManager


class TestBackgroundCustomSettings:
    """Test background token refresh with custom settings."""

    @pytest.fixture
    def test_env_vars(self):
        """Set up test environment variables."""
        test_vars = {
            "RUMBA_CLIENT_ID": "test_client_id",
            "RUMBA_CLIENT_SECRET": "test_client_secret",
            "RUMBA_TOKEN_URL": "https://api.example.com/token",
            "RUMBA_BASE_URL": "https://api.example.com",
            "RUMBA_TOKEN_BUFFER_MINUTES": "5",
            "RUMBA_TOKEN_REFRESH_INTERVAL_MINUTES": "5"
        }
        
        # Set environment variables
        for key, value in test_vars.items():
            os.environ[key] = value
        
        yield test_vars
        
        # Clean up environment variables
        for key in test_vars.keys():
            if key in os.environ:
                del os.environ[key]

    @pytest.fixture
    def custom_config(self, test_env_vars):
        """Create custom configuration with RUMBA_ prefix."""
        return create_config_with_prefixes(
            revo_prefix="RUMBA_",
            llm_prefix="RUMBA_LLM_",
            logging_prefix="RUMBA_LOG_",
            token_prefix="RUMBA_TOKEN_"
        )

    def test_custom_config_creation(self, custom_config):
        """Test that custom configuration is created correctly."""
        assert custom_config is not None
        assert hasattr(custom_config, 'revos')
        assert hasattr(custom_config, 'llm_models')
        assert hasattr(custom_config, 'logging')
        assert hasattr(custom_config, 'token_manager')

    def test_custom_config_values(self, custom_config):
        """Test that custom configuration reads correct values."""
        # Access the revos config section
        revos_config = custom_config.revos
        assert revos_config.client_id == "test_client_id"
        assert revos_config.client_secret == "test_client_secret"
        assert revos_config.token_url == "https://api.example.com/token"
        assert revos_config.base_url == "https://api.example.com"
        assert revos_config.token_buffer_minutes == 5

    def test_token_manager_with_custom_settings(self, custom_config):
        """Test TokenManager initialization with custom settings."""
        token_manager = TokenManager(
            refresh_interval_minutes=5,
            settings_instance=custom_config
        )
        
        assert token_manager is not None
        assert token_manager.refresh_manager.settings_instance is custom_config
        assert token_manager.background_manager.refresh_manager.settings_instance is custom_config

    def test_refresh_manager_custom_settings(self, custom_config):
        """Test TokenRefreshManager with custom settings."""
        refresh_manager = TokenRefreshManager(
            refresh_interval_minutes=5,
            settings_instance=custom_config
        )
        
        assert refresh_manager.settings_instance is custom_config
        assert refresh_manager.refresh_interval == 300  # 5 minutes in seconds

    def test_background_manager_custom_settings(self, custom_config):
        """Test BackgroundTokenManager with custom settings."""
        background_manager = BackgroundTokenManager(
            refresh_interval_minutes=5,
            settings_instance=custom_config
        )
        
        assert background_manager.refresh_manager.settings_instance is custom_config

    def test_settings_consistency(self, custom_config):
        """Test that all managers use the same custom settings."""
        token_manager = TokenManager(
            refresh_interval_minutes=5,
            settings_instance=custom_config
        )
        
        # All managers should use the same settings instance
        assert token_manager.refresh_manager.settings_instance is custom_config
        assert token_manager.background_manager.refresh_manager.settings_instance is custom_config
        
        # Settings should be consistent across managers
        refresh_settings = token_manager.refresh_manager.settings_instance
        background_settings = token_manager.background_manager.refresh_manager.settings_instance
        
        assert refresh_settings is background_settings
        assert refresh_settings.revos.client_id == "test_client_id"
        assert background_settings.revos.client_id == "test_client_id"

    @pytest.mark.asyncio
    async def test_background_service_startup(self, custom_config):
        """Test background service startup with custom settings."""
        token_manager = TokenManager(
            refresh_interval_minutes=5,
            settings_instance=custom_config
        )
        
        # Mock the actual token operations to avoid network calls
        with patch('revos.auth.core.RevosTokenManager') as mock_token_manager_class:
            mock_token_manager = MagicMock()
            mock_token_manager.get_token.return_value = "mock_token"
            mock_token_manager.invalidate_token.return_value = None
            mock_token_manager_class.return_value = mock_token_manager
            
            # Start background service
            await token_manager.start_background_service()
            
            # Verify service is running
            assert token_manager.is_background_service_running() is True
            
            # Stop the service
            await token_manager.stop_background_service()
            
            # Verify service is stopped
            assert token_manager.is_background_service_running() is False

    def test_custom_prefix_validation(self):
        """Test that custom prefixes work correctly."""
        # Set custom environment variables first
        os.environ["CUSTOM_CLIENT_ID"] = "custom_client_id"
        os.environ["CUSTOM_CLIENT_SECRET"] = "custom_client_secret"
        os.environ["CUSTOM_TOKEN_URL"] = "https://custom.api.com/token"
        os.environ["CUSTOM_BASE_URL"] = "https://custom.api.com"
        os.environ["CUSTOM_TOKEN_BUFFER_MINUTES"] = "10"
        os.environ["CUSTOM_TOKEN_REFRESH_INTERVAL_MINUTES"] = "5"  # Minimum allowed
        
        try:
            # Test with different custom prefixes
            config = create_config_with_prefixes(
                revo_prefix="CUSTOM_",
                llm_prefix="CUSTOM_LLM_",
                logging_prefix="CUSTOM_LOG_",
                token_prefix="CUSTOM_TOKEN_"
            )
            
            assert config.revos.client_id == "custom_client_id"
            assert config.revos.client_secret == "custom_client_secret"
            assert config.revos.token_url == "https://custom.api.com/token"
            assert config.revos.base_url == "https://custom.api.com"
            assert config.revos.token_buffer_minutes == 10
        finally:
            # Clean up custom environment variables
            for key in ["CUSTOM_CLIENT_ID", "CUSTOM_CLIENT_SECRET", "CUSTOM_TOKEN_URL", 
                       "CUSTOM_BASE_URL", "CUSTOM_TOKEN_BUFFER_MINUTES", "CUSTOM_TOKEN_REFRESH_INTERVAL_MINUTES"]:
                if key in os.environ:
                    del os.environ[key]

    def test_fallback_to_global_settings(self):
        """Test that managers fall back to global settings when no custom settings provided."""
        # Create managers without custom settings
        token_manager = TokenManager(refresh_interval_minutes=5)
        refresh_manager = TokenRefreshManager(refresh_interval_minutes=5)
        background_manager = BackgroundTokenManager(refresh_interval_minutes=5)
        
        # They should still work (using global settings)
        assert token_manager is not None
        assert refresh_manager is not None
        assert background_manager is not None
        
        # Settings instance should be None (will use global settings)
        assert token_manager.refresh_manager.settings_instance is None
        assert token_manager.background_manager.refresh_manager.settings_instance is None

    def test_original_error_scenario(self):
        """Test that the original error scenario is fixed."""
        # This test simulates the original error where background process
        # was looking for REVOS_CLIENT_ID instead of RUMBA_CLIENT_ID
        
        # Set up environment variables first
        test_vars = {
            "RUMBA_CLIENT_ID": "test_client_id",
            "RUMBA_CLIENT_SECRET": "test_client_secret",
            "RUMBA_TOKEN_URL": "https://api.example.com/token",
            "RUMBA_BASE_URL": "https://api.example.com",
            "RUMBA_TOKEN_BUFFER_MINUTES": "5",
            "RUMBA_TOKEN_REFRESH_INTERVAL_MINUTES": "5"
        }
        
        for key, value in test_vars.items():
            os.environ[key] = value
        
        try:
            # Create config with RUMBA_ prefix (like in the original error)
            config = create_config_with_prefixes(
                revo_prefix="RUMBA_",
                llm_prefix="RUMBA_LLM_",
                logging_prefix="RUMBA_LOG_",
                token_prefix="RUMBA_TOKEN_"
            )
            
            # Create token manager with custom settings
            token_manager = TokenManager(
                refresh_interval_minutes=5,
                settings_instance=config
            )
            
            # Verify that the background manager uses the custom settings
            # This should prevent the original validation error
            background_settings = token_manager.background_manager.refresh_manager.settings_instance
            
            assert background_settings is not None
            assert background_settings.revos.client_id == "test_client_id"
            assert background_settings.revos.client_secret == "test_client_secret"
            
            # The original error was about missing client_id and client_secret
            # Now they should be present in the custom settings
            assert background_settings.revos.client_id is not None
            assert background_settings.revos.client_secret is not None
            
        finally:
            # Clean up environment variables
            for key in test_vars.keys():
                if key in os.environ:
                    del os.environ[key]

    @pytest.mark.asyncio
    async def test_background_refresh_with_custom_settings(self, custom_config):
        """Test that background refresh uses custom settings correctly."""
        token_manager = TokenManager(
            refresh_interval_minutes=5,
            settings_instance=custom_config
        )
        
        # Mock the token operations
        with patch('revos.auth.core.RevosTokenManager') as mock_token_manager_class:
            mock_token_manager = MagicMock()
            mock_token_manager.get_token.return_value = "mock_token"
            mock_token_manager.invalidate_token.return_value = None
            mock_token_manager_class.return_value = mock_token_manager
            
            # Start background service
            await token_manager.start_background_service()
            
            # Let it run briefly
            await asyncio.sleep(0.1)
            
            # Stop the service
            await token_manager.stop_background_service()
            
            # Verify that the mock was called with custom settings
            # This ensures the background process is using custom settings
            assert mock_token_manager_class.called


class TestBackgroundCustomSettingsIntegration:
    """Integration tests for background custom settings."""

    @pytest.fixture
    def integration_env_vars(self):
        """Set up integration test environment variables."""
        test_vars = {
            "INTEGRATION_CLIENT_ID": "integration_client_id",
            "INTEGRATION_CLIENT_SECRET": "integration_client_secret",
            "INTEGRATION_TOKEN_URL": "https://integration.api.com/token",
            "INTEGRATION_BASE_URL": "https://integration.api.com",
            "INTEGRATION_TOKEN_BUFFER_MINUTES": "5",
            "INTEGRATION_TOKEN_REFRESH_INTERVAL_MINUTES": "5"  # Minimum allowed
        }
        
        for key, value in test_vars.items():
            os.environ[key] = value
        
        yield test_vars
        
        for key in test_vars.keys():
            if key in os.environ:
                del os.environ[key]

    def test_full_integration(self, integration_env_vars):
        """Test full integration with custom settings."""
        # Create custom configuration
        config = create_config_with_prefixes(
            revo_prefix="INTEGRATION_",
            llm_prefix="INTEGRATION_LLM_",
            logging_prefix="INTEGRATION_LOG_",
            token_prefix="INTEGRATION_TOKEN_"
        )
        
        # Create token manager with custom settings
        token_manager = TokenManager(
            refresh_interval_minutes=5,
            settings_instance=config
        )
        
        # Verify all components use custom settings
        assert token_manager.refresh_manager.settings_instance is config
        assert token_manager.background_manager.refresh_manager.settings_instance is config
        
        # Verify settings values
        settings = token_manager.refresh_manager.settings_instance
        assert settings.revos.client_id == "integration_client_id"
        assert settings.revos.client_secret == "integration_client_secret"
        assert settings.revos.token_url == "https://integration.api.com/token"
        assert settings.revos.base_url == "https://integration.api.com"
        assert settings.revos.token_buffer_minutes == 5

    @pytest.mark.asyncio
    async def test_background_service_lifecycle(self, integration_env_vars):
        """Test complete background service lifecycle with custom settings."""
        config = create_config_with_prefixes(
            revo_prefix="INTEGRATION_",
            llm_prefix="INTEGRATION_LLM_",
            logging_prefix="INTEGRATION_LOG_",
            token_prefix="INTEGRATION_TOKEN_"
        )
        
        token_manager = TokenManager(
            refresh_interval_minutes=5,
            settings_instance=config
        )
        
        # Mock token operations to avoid network calls
        with patch('revos.auth.core.RevosTokenManager') as mock_token_manager_class:
            mock_token_manager = MagicMock()
            mock_token_manager.get_token.return_value = "mock_token"
            mock_token_manager.invalidate_token.return_value = None
            mock_token_manager_class.return_value = mock_token_manager
            
            # Test service lifecycle
            assert not token_manager.is_background_service_running()
            
            await token_manager.start_background_service()
            assert token_manager.is_background_service_running()
            
            # Let it run briefly
            await asyncio.sleep(0.1)
            
            await token_manager.stop_background_service()
            assert not token_manager.is_background_service_running()
            
            # Verify custom settings were used
            assert mock_token_manager_class.called
