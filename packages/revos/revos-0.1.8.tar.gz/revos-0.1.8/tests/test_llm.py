"""
Tests for LLM functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from pydantic import BaseModel

from revos.llm.tools import (
    LangChainExtractor,
    get_langchain_extractor,
    create_all_extractors,
    list_available_extractors
)


class MockResult(BaseModel):
    """Test result model for testing."""
    task: str
    result: str
    confidence: float


class TestLangChainExtractor:
    """Test cases for LangChainExtractor."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.settings_mock = Mock()
        self.settings_mock.revos.client_id = "test-client-id"
        self.settings_mock.revos.client_secret = "test-client-secret"
        self.settings_mock.revos.base_url = "https://test.com/api"
        
        # Mock multiple models configuration
        self.settings_mock.llm_models = Mock()
        self.settings_mock.llm_models.models = {
            "gpt-3.5-turbo": Mock(
                model="gpt-3.5-turbo",
                temperature=0.1,
                max_tokens=1000,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            ),
            "gpt-4": Mock(
                model="gpt-4",
                temperature=0.1,
                max_tokens=2000,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
        }
        self.settings_mock.llm_models.get_model.return_value = self.settings_mock.llm_models.models["gpt-3.5-turbo"]
    
    def test_init_requires_model_name(self):
        """Test that LangChainExtractor requires model_name."""
        with pytest.raises(TypeError, match="missing 1 required positional argument"):
            LangChainExtractor()
        
        with pytest.raises(ValueError, match="model_name is required"):
            LangChainExtractor("")
    
    @patch('revos.llm.tools.RevosTokenManager')
    @patch('revos.llm.tools.ChatOpenAI')
    def test_init_success(self, mock_chat_openai, mock_token_manager_class):
        """Test successful LangChainExtractor initialization."""
        mock_token_manager = Mock()
        mock_token_manager.get_token.return_value = "test-token"
        mock_token_manager_class.return_value = mock_token_manager
        
        mock_llm = Mock()
        mock_chat_openai.return_value = mock_llm
        
        with patch('revos.llm.tools.get_settings', return_value=self.settings_mock):
            extractor = LangChainExtractor("gpt-3.5-turbo")
            
            assert extractor.model_name == "gpt-3.5-turbo"
            assert extractor.name == "extractor_gpt-3.5-turbo"
            assert extractor.llm == mock_llm
            mock_chat_openai.assert_called_once()
    
    @patch('revos.llm.tools.RevosTokenManager')
    def test_init_with_custom_name(self, mock_token_manager_class):
        """Test LangChainExtractor initialization with custom name."""
        mock_token_manager = Mock()
        mock_token_manager.get_token.return_value = "test-token"
        mock_token_manager_class.return_value = mock_token_manager
        
        with patch('revos.llm.tools.get_settings', return_value=self.settings_mock):
            with patch('revos.llm.tools.ChatOpenAI'):
                extractor = LangChainExtractor("gpt-4", name="my_custom_extractor")
                
                assert extractor.name == "my_custom_extractor"
    
    @patch('revos.llm.tools.RevosTokenManager')
    def test_init_auth_failure(self, mock_token_manager_class):
        """Test LangChainExtractor initialization with auth failure."""
        mock_token_manager = Mock()
        mock_token_manager.get_token.side_effect = Exception("Authentication failed")
        mock_token_manager_class.return_value = mock_token_manager
        
        with patch('revos.llm.tools.get_settings', return_value=self.settings_mock):
            with pytest.raises(RuntimeError, match="Cannot initialize LangChainExtractor"):
                LangChainExtractor("gpt-3.5-turbo")
    
    @patch('revos.llm.tools.RevosTokenManager')
    @patch('revos.llm.tools.ChatOpenAI')
    def test_init_with_multiple_models_config(self, mock_chat_openai, mock_token_manager_class):
        """Test LangChainExtractor initialization with multiple models config."""
        mock_token_manager = Mock()
        mock_token_manager.get_token.return_value = "test-token"
        mock_token_manager_class.return_value = mock_token_manager
        mock_llm = Mock()
        mock_chat_openai.return_value = mock_llm
        
        # Add llm_models to settings
        self.settings_mock.llm_models = Mock()
        self.settings_mock.llm_models.models = {"gpt-4": Mock()}
        self.settings_mock.llm_models.get_model.return_value = Mock(
            model="gpt-4",
            temperature=0.8,
            max_tokens=2000,
            top_p=0.9,
            frequency_penalty=0.3,
            presence_penalty=0.3
        )
        
        with patch('revos.llm.tools.get_settings', return_value=self.settings_mock):
            extractor = LangChainExtractor("gpt-4")
            
            assert extractor.model_name == "gpt-4"
            self.settings_mock.llm_models.get_model.assert_called_once_with("gpt-4")
    
    @patch('revos.llm.tools.RevosTokenManager')
    def test_get_current_model(self, mock_token_manager_class):
        """Test get_current_model method."""
        mock_token_manager = Mock()
        mock_token_manager.get_token.return_value = "test-token"
        mock_token_manager_class.return_value = mock_token_manager
        
        with patch('revos.llm.tools.get_settings', return_value=self.settings_mock):
            with patch('revos.llm.tools.ChatOpenAI'):
                extractor = LangChainExtractor("gpt-4")
                
                assert extractor.get_current_model() == "gpt-4"
    
    @patch('revos.llm.tools.RevosTokenManager')
    @patch('revos.llm.tools.ChatOpenAI')
    def test_extract_structured_data_success(self, mock_chat_openai, mock_token_manager_class):
        """Test successful structured data extraction."""
        mock_token_manager = Mock()
        mock_token_manager.get_token.return_value = "test-token"
        mock_token_manager_class.return_value = mock_token_manager
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = '{"task": "test", "result": "success", "confidence": 0.95}'
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        mock_chat_openai.return_value = mock_llm
        
        with patch('revos.llm.tools.get_settings', return_value=self.settings_mock):
            extractor = LangChainExtractor("gpt-3.5-turbo")
            
            result = extractor.extract_structured_data(
                prompt="Test prompt",
                target_class=MockResult
            )
            
            assert isinstance(result, MockResult)
            assert result.task == "test"
            assert result.result == "success"
            assert result.confidence == 0.95
    
    @patch('revos.llm.tools.RevosTokenManager')
    @patch('revos.llm.tools.ChatOpenAI')
    def test_extract_structured_data_failure(self, mock_chat_openai, mock_token_manager_class):
        """Test structured data extraction failure."""
        mock_token_manager = Mock()
        mock_token_manager.get_token.return_value = "test-token"
        mock_token_manager_class.return_value = mock_token_manager
        mock_llm = Mock()
        mock_llm.ainvoke = AsyncMock(side_effect=Exception("LLM call failed"))
        mock_chat_openai.return_value = mock_llm
        
        with patch('revos.llm.tools.get_settings', return_value=self.settings_mock):
            extractor = LangChainExtractor("gpt-3.5-turbo")
            
            # Should raise RuntimeError when LLM fails
            with pytest.raises(RuntimeError, match="Failed to extract structured data"):
                extractor.extract_structured_data(
                    prompt="Test prompt",
                    target_class=MockResult
                )
    
    @patch('revos.llm.tools.RevosTokenManager')
    @patch('revos.llm.tools.ChatOpenAI')
    def test_extract_async_success(self, mock_chat_openai, mock_token_manager_class):
        """Test successful async extraction."""
        mock_token_manager = Mock()
        mock_token_manager.get_token.return_value = "test-token"
        mock_token_manager_class.return_value = mock_token_manager
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = '{"task": "async test", "result": "async success", "confidence": 0.9}'
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        mock_chat_openai.return_value = mock_llm
        
        with patch('revos.llm.tools.get_settings', return_value=self.settings_mock):
            extractor = LangChainExtractor("gpt-3.5-turbo")
            
            async def run_test():
                from langchain_core.prompts import PromptTemplate
                prompt = PromptTemplate(input_variables=[], template="Test prompt")
                result = await extractor.extract(MockResult, prompt)
                return result
            
            result = asyncio.run(run_test())
            
            assert isinstance(result, MockResult)
            assert result.task == "async test"
            assert result.result == "async success"
            assert result.confidence == 0.9


class TestLLMFunctions:
    """Test cases for LLM utility functions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Clear any existing extractors
        with patch('revos.llm.tools._langchain_extractors', {}):
            pass
    
    def test_get_langchain_extractor_requires_model_name(self):
        """Test that get_langchain_extractor requires model_name."""
        with pytest.raises(TypeError, match="missing 1 required positional argument"):
            get_langchain_extractor()
        
        with pytest.raises(ValueError, match="model_name is required"):
            get_langchain_extractor("")
    
    @patch('revos.llm.tools.get_settings')
    @patch('revos.llm.tools.LangChainExtractor')
    def test_get_langchain_extractor_success(self, mock_extractor_class, mock_get_settings):
        """Test successful get_langchain_extractor call."""
        mock_extractor = Mock()
        mock_extractor_class.return_value = mock_extractor
        mock_get_settings.return_value = Mock()
        
        result = get_langchain_extractor("gpt-4")
        
        assert result == mock_extractor
        mock_extractor_class.assert_called_once_with(model_name="gpt-4", settings_instance=mock_get_settings.return_value)
    
    @patch('revos.llm.tools.RevosTokenManager')
    @patch('revos.llm.tools.LangChainExtractor')
    @patch('revos.llm.tools.get_settings')
    def test_get_langchain_extractor_caching(self, mock_get_settings, mock_extractor_class, mock_token_manager_class):
        """Test that get_langchain_extractor caches extractors."""
        # Clear the cache first
        from revos.llm.tools import _langchain_extractors
        _langchain_extractors.clear()
        
        mock_token_manager = Mock()
        mock_token_manager.get_token.return_value = "test-token"
        mock_token_manager_class.return_value = mock_token_manager
        mock_extractor = Mock()
        mock_extractor_class.return_value = mock_extractor
        
        # Mock settings
        mock_settings = Mock()
        mock_settings.llm_models = Mock()
        mock_settings.llm_models.get_model.return_value = Mock()
        mock_get_settings.return_value = mock_settings
        
        # First call
        result1 = get_langchain_extractor("gpt-4")
        
        # Second call should return cached extractor
        result2 = get_langchain_extractor("gpt-4")
        
        assert result1 is result2
        mock_extractor_class.assert_called_once()
    
    @patch('revos.llm.tools.get_settings')
    def test_create_all_extractors_success(self, mock_get_settings):
        """Test successful create_all_extractors call."""
        # Mock settings with llm_models
        mock_settings = Mock()
        mock_settings.llm_models = Mock()
        mock_settings.llm_models.list_available_models.return_value = {
            "gpt-3.5-turbo": "Fast model",
            "gpt-4": "Capable model"
        }
        mock_get_settings.return_value = mock_settings
        
        with patch('revos.llm.tools.LangChainExtractor') as mock_extractor_class:
            mock_extractor1 = Mock()
            mock_extractor2 = Mock()
            mock_extractor_class.side_effect = [mock_extractor1, mock_extractor2]
            
            result = create_all_extractors()
            
            assert isinstance(result, dict)
            assert "gpt-3.5-turbo" in result
            assert "gpt-4" in result
            assert result["gpt-3.5-turbo"] == mock_extractor1
            assert result["gpt-4"] == mock_extractor2
            assert mock_extractor_class.call_count == 2
    
    @patch('revos.llm.tools.get_settings')
    def test_create_all_extractors_no_models(self, mock_get_settings):
        """Test create_all_extractors with no models configured."""
        # Mock settings without llm_models
        mock_settings = Mock()
        mock_settings.llm_models = Mock()
        mock_settings.llm_models.models = {}
        mock_get_settings.return_value = mock_settings
        
        with pytest.raises(ValueError, match="No models configured"):
            create_all_extractors()
    
    @patch('revos.llm.tools.get_settings')
    def test_create_all_extractors_empty_models(self, mock_get_settings):
        """Test create_all_extractors with empty models."""
        # Mock settings with empty llm_models
        mock_settings = Mock()
        mock_settings.llm_models = Mock()
        mock_settings.llm_models.models = {}
        mock_get_settings.return_value = mock_settings
        
        with pytest.raises(ValueError, match="No models configured"):
            create_all_extractors()
    
    @patch('revos.llm.tools.get_settings')
    def test_list_available_extractors_success(self, mock_get_settings):
        """Test successful list_available_extractors call."""
        # Mock settings with llm_models
        mock_settings = Mock()
        mock_settings.llm_models = Mock()
        mock_settings.llm_models.list_available_models.return_value = {
            "gpt-3.5-turbo": "Fast model",
            "gpt-4": "Capable model"
        }
        mock_get_settings.return_value = mock_settings
        
        result = list_available_extractors()
        
        assert isinstance(result, dict)
        assert result == {
            "gpt-3.5-turbo": "Fast model",
            "gpt-4": "Capable model"
        }
    
    @patch('revos.llm.tools.get_settings')
    def test_list_available_extractors_no_models(self, mock_get_settings):
        """Test list_available_extractors with no models configured."""
        # Mock settings without llm_models
        mock_settings = Mock()
        mock_settings.llm_models = Mock()
        mock_settings.llm_models.models = {}
        mock_get_settings.return_value = mock_settings
        
        with pytest.raises(ValueError, match="No models configured"):
            list_available_extractors()
    
    @patch('revos.llm.tools.get_settings')
    def test_list_available_extractors_empty_models(self, mock_get_settings):
        """Test list_available_extractors with empty models."""
        # Mock settings with empty llm_models
        mock_settings = Mock()
        mock_settings.llm_models = Mock()
        mock_settings.llm_models.models = {}
        mock_get_settings.return_value = mock_settings
        
        with pytest.raises(ValueError, match="No models configured"):
            list_available_extractors()


class TestLLMIntegration:
    """Integration tests for LLM functionality."""
    
    @patch('revos.llm.tools.RevosTokenManager')
    @patch('revos.llm.tools.ChatOpenAI')
    def test_full_extraction_workflow(self, mock_chat_openai, mock_token_manager_class):
        """Test complete extraction workflow."""
        mock_token_manager = Mock()
        mock_token_manager.get_token.return_value = "test-token"
        mock_token_manager_class.return_value = mock_token_manager
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = '{"task": "integration test", "result": "workflow success", "confidence": 0.98}'
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        mock_chat_openai.return_value = mock_llm
        
        settings_mock = Mock()
        settings_mock.revos.client_id = "test-client-id"
        settings_mock.revos.client_secret = "test-client-secret"
        settings_mock.revos.base_url = "https://test.com/api"
        
        # Mock multiple models configuration
        settings_mock.llm_models = Mock()
        settings_mock.llm_models.models = {
            "gpt-3.5-turbo": Mock(
                model="gpt-3.5-turbo",
                temperature=0.1,
                max_tokens=1000,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
        }
        settings_mock.llm_models.get_model.return_value = settings_mock.llm_models.models["gpt-3.5-turbo"]
        
        with patch('revos.llm.tools.get_settings', return_value=settings_mock):
            # Create extractor
            extractor = get_langchain_extractor("gpt-3.5-turbo")
            
            # Extract structured data
            result = extractor.extract_structured_data(
                prompt="Test the integration workflow",
                target_class=MockResult
            )
            
            # Verify result
            assert isinstance(result, MockResult)
            assert result.task == "integration test"
            assert result.result == "workflow success"
            assert result.confidence == 0.98
            
            # Verify LLM was called correctly
            mock_llm.ainvoke.assert_called_once()
            call_args = mock_llm.ainvoke.call_args[0][0]
            assert len(call_args) == 1  # Should be a list with one message
