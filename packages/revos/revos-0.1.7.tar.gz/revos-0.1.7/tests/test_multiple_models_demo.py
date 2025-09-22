"""
Comprehensive demonstration of multiple models configuration.

This test shows how to use the new .env parser for multiple LLM models.
"""

import os
import pytest
from unittest.mock import patch
from revos import create_config_with_prefixes, get_langchain_extractor
from revos.llm.tools import _langchain_extractors
from langchain_openai.chat_models.base import ChatOpenAI


class TestMultipleModelsDemo:
    """Comprehensive test of multiple models configuration."""
    
    def setup_method(self):
        """Set up test environment."""
        _langchain_extractors.clear()
        
        # Comprehensive environment variables for multiple models
        self.test_env = {
            'MYAPP_CLIENT_ID': 'myapp-client-123',
            'MYAPP_CLIENT_SECRET': 'myapp-secret-456',
            'MYAPP_TOKEN_URL': 'https://myapp.com/oauth/token',
            'MYAPP_BASE_URL': 'https://myapp.com/llm-api',
            
            # Single LLM configuration (fallback)
            'LLM_MODEL': 'claude_4_sonnet',
            'LLM_TEMPERATURE': '0.3',
            'LLM_MAX_TOKENS': '4000',
            
            # Multiple models using the new syntax
            # Claude 4 Sonnet
            'LLM_MODELS_CLAUDE_4_SONNET_MODEL': 'claude_4_sonnet',
            'LLM_MODELS_CLAUDE_4_SONNET_TEMPERATURE': '0.3',
            'LLM_MODELS_CLAUDE_4_SONNET_MAX_TOKENS': '4000',
            'LLM_MODELS_CLAUDE_4_SONNET_TOP_P': '0.95',
            'LLM_MODELS_CLAUDE_4_SONNET_FREQUENCY_PENALTY': '0.0',
            'LLM_MODELS_CLAUDE_4_SONNET_PRESENCE_PENALTY': '0.0',
            'LLM_MODELS_CLAUDE_4_SONNET_DESCRIPTION': 'MyApp Claude 4 Sonnet Model',
            
            # GPT-4
            'LLM_MODELS_GPT_4_MODEL': 'gpt-4',
            'LLM_MODELS_GPT_4_TEMPERATURE': '0.1',
            'LLM_MODELS_GPT_4_MAX_TOKENS': '2000',
            'LLM_MODELS_GPT_4_TOP_P': '1.0',
            'LLM_MODELS_GPT_4_FREQUENCY_PENALTY': '0.0',
            'LLM_MODELS_GPT_4_PRESENCE_PENALTY': '0.0',
            'LLM_MODELS_GPT_4_DESCRIPTION': 'MyApp GPT-4 Model',
            
            # Claude 3
            'LLM_MODELS_CLAUDE_3_MODEL': 'claude-3-sonnet',
            'LLM_MODELS_CLAUDE_3_TEMPERATURE': '0.2',
            'LLM_MODELS_CLAUDE_3_MAX_TOKENS': '3000',
            'LLM_MODELS_CLAUDE_3_TOP_P': '0.9',
            'LLM_MODELS_CLAUDE_3_FREQUENCY_PENALTY': '0.1',
            'LLM_MODELS_CLAUDE_3_PRESENCE_PENALTY': '0.1',
            'LLM_MODELS_CLAUDE_3_DESCRIPTION': 'MyApp Claude 3 Model',
            
            # Custom model with additional parameters
            'LLM_MODELS_CUSTOM_MODEL': 'my-custom-model',
            'LLM_MODELS_CUSTOM_TEMPERATURE': '0.5',
            'LLM_MODELS_CUSTOM_MAX_TOKENS': '5000',
            'LLM_MODELS_CUSTOM_TOP_P': '0.8',
            'LLM_MODELS_CUSTOM_FREQUENCY_PENALTY': '0.2',
            'LLM_MODELS_CUSTOM_PRESENCE_PENALTY': '0.2',
            'LLM_MODELS_CUSTOM_DESCRIPTION': 'My Custom Model',
            'LLM_MODELS_CUSTOM_TIMEOUT': '30',
            'LLM_MODELS_CUSTOM_STREAM': 'true',
        }
    
    def teardown_method(self):
        """Clean up after each test."""
        _langchain_extractors.clear()
    
    @patch.dict(os.environ, {})
    def test_multiple_models_comprehensive(self):
        """Test comprehensive multiple models configuration."""
        with patch.dict(os.environ, self.test_env):
            config = create_config_with_prefixes(
                revo_prefix="MYAPP_",
                llm_prefix="LLM_"
            )
            
            print(f"\n=== Multiple Models Configuration Demo ===")
            print(f"Available models: {list(config.llm_models.models.keys())}")
            
            # Test each configured model
            models_to_test = [
                'claude_4_sonnet',
                'gpt_4', 
                'claude_3',
                'custom'
            ]
            
            for model_name in models_to_test:
                if model_name in config.llm_models.models:
                    model_config = config.llm_models.get_model(model_name)
                    print(f"\n✅ {model_name.upper()}:")
                    print(f"   Model: {model_config.model}")
                    print(f"   Temperature: {model_config.temperature}")
                    print(f"   Max Tokens: {model_config.max_tokens}")
                    print(f"   Top P: {model_config.top_p}")
                    print(f"   Description: {model_config.description}")
                    
                    # Test that the model configuration is correct
                    if model_name == 'claude_4_sonnet':
                        assert model_config.model == 'claude_4_sonnet'
                        assert model_config.temperature == 0.3
                        assert model_config.max_tokens == 4000
                        assert model_config.top_p == 0.95
                        assert model_config.description == 'MyApp Claude 4 Sonnet Model'
                    elif model_name == 'gpt_4':
                        assert model_config.model == 'gpt-4'
                        assert model_config.temperature == 0.1
                        assert model_config.max_tokens == 2000
                        assert model_config.top_p == 1.0
                        assert model_config.description == 'MyApp GPT-4 Model'
                    elif model_name == 'claude_3':
                        assert model_config.model == 'claude-3-sonnet'
                        assert model_config.temperature == 0.2
                        assert model_config.max_tokens == 3000
                        assert model_config.top_p == 0.9
                        assert model_config.description == 'MyApp Claude 3 Model'
                    elif model_name == 'custom':
                        assert model_config.model == 'my-custom-model'
                        assert model_config.temperature == 0.5
                        assert model_config.max_tokens == 5000
                        assert model_config.top_p == 0.8
                        assert model_config.description == 'My Custom Model'
                        # Test custom parameters
                        assert model_config.custom_params.get('timeout') == 30
                        assert model_config.custom_params.get('stream') == True
                else:
                    print(f"ℹ️  {model_name} not found in models")
    
    @patch.dict(os.environ, {})
    def test_extractor_creation_with_multiple_models(self):
        """Test that extractors are created correctly for multiple models."""
        with patch.dict(os.environ, self.test_env):
            config = create_config_with_prefixes(
                revo_prefix="MYAPP_",
                llm_prefix="LLM_"
            )
            
            # Mock token manager
            with patch('revos.llm.tools.RevosTokenManager') as mock_token_manager:
                mock_token_manager.return_value.get_token.return_value = 'fake-token'
                
                print(f"\n=== Extractor Creation Demo ===")
                
                # Test extractor creation for each model
                models_to_test = ['claude_4_sonnet', 'gpt_4', 'claude_3', 'custom']
                
                for model_name in models_to_test:
                    if model_name in config.llm_models.models:
                        extractor = get_langchain_extractor(model_name, settings_instance=config)
                        
                        print(f"\n✅ {model_name.upper()} Extractor:")
                        print(f"   Model Name: {extractor.model_name}")
                        print(f"   LLM Model: {extractor.llm.model_name}")
                        print(f"   Temperature: {extractor.llm.temperature}")
                        print(f"   Max Tokens: {extractor.llm.max_tokens}")
                        
                        # Verify the extractor is created correctly
                        assert isinstance(extractor.llm, ChatOpenAI)
                        assert extractor.model_name == model_name
                        
                        # Test that extractors are cached
                        assert model_name in _langchain_extractors
                    else:
                        print(f"ℹ️  {model_name} not available for extractor creation")
    
    @patch.dict(os.environ, {})
    def test_model_not_found_error(self):
        """Test that appropriate error is raised when model is not found."""
        with patch.dict(os.environ, self.test_env):
            config = create_config_with_prefixes(
                revo_prefix="MYAPP_",
                llm_prefix="LLM_"
            )
            
            # Mock token manager
            with patch('revos.llm.tools.RevosTokenManager') as mock_token_manager:
                mock_token_manager.return_value.get_token.return_value = 'fake-token'
                
                print(f"\n=== Model Not Found Error Demo ===")
                
                # Test that appropriate error is raised for non-existent model
                with pytest.raises(RuntimeError, match="Cannot initialize LangChainExtractor"):
                    get_langchain_extractor('nonexistent_model', settings_instance=config)
                
                print(f"✅ Model not found error handled correctly")
    
    @patch.dict(os.environ, {})
    def test_model_name_consistency(self):
        """Test that model names are consistent across the system."""
        with patch.dict(os.environ, self.test_env):
            config = create_config_with_prefixes(
                revo_prefix="MYAPP_",
                llm_prefix="LLM_"
            )
            
            # Mock token manager
            with patch('revos.llm.tools.RevosTokenManager') as mock_token_manager:
                mock_token_manager.return_value.get_token.return_value = 'fake-token'
                
                print(f"\n=== Model Name Consistency Demo ===")
                
                # Test claude_4_sonnet consistency
                if 'claude_4_sonnet' in config.llm_models.models:
                    extractor = get_langchain_extractor('claude_4_sonnet', settings_instance=config)
                    
                    print(f"✅ claude_4_sonnet consistency:")
                    print(f"   Extractor model_name: {extractor.model_name}")
                    print(f"   LLM model_name: {extractor.llm.model_name}")
                    print(f"   Model config model: {config.llm_models.get_model('claude_4_sonnet').model}")
                    
                    # All should use underscores consistently
                    assert extractor.model_name == 'claude_4_sonnet'
                    assert extractor.llm.model_name == 'claude_4_sonnet'
                    assert config.llm_models.get_model('claude_4_sonnet').model == 'claude_4_sonnet'
                    
                    # Should not contain hyphens
                    assert 'claude-4-sonnet' not in extractor.llm.model_name
                    assert 'claude-4-sonnet' not in extractor.model_name


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
