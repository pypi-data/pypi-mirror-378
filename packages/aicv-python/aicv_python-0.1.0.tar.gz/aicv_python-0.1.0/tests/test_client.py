"""
Tests for AiCV Client
"""

import pytest
import httpx
from unittest.mock import Mock, patch
from aicv import AiCVClient
from aicv.exceptions import AuthenticationError, APIError, ValidationError


class TestAiCVClient:
    """Test cases for AiCVClient"""
    
    def test_client_initialization(self):
        """Test client initialization with valid parameters"""
        client = AiCVClient(api_key="test-key")
        assert client.api_key == "test-key"
        assert client.base_url == "https://api.aicv.com"
        assert client.timeout == 30.0
        client.close()
    
    def test_client_initialization_with_custom_params(self):
        """Test client initialization with custom parameters"""
        client = AiCVClient(
            api_key="test-key",
            base_url="https://custom.api.com",
            timeout=60.0
        )
        assert client.api_key == "test-key"
        assert client.base_url == "https://custom.api.com"
        assert client.timeout == 60.0
        client.close()
    
    def test_client_initialization_without_api_key(self):
        """Test client initialization without API key raises ValidationError"""
        with pytest.raises(ValidationError, match="API key is required"):
            AiCVClient(api_key="")
    
    def test_context_manager(self):
        """Test client as context manager"""
        with AiCVClient(api_key="test-key") as client:
            assert isinstance(client, AiCVClient)
    
    @patch('httpx.Client.request')
    def test_analyze_cv_success(self, mock_request):
        """Test successful CV analysis"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"analysis": "success"}
        mock_request.return_value = mock_response
        
        client = AiCVClient(api_key="test-key")
        result = client.analyze_cv("Test CV content")
        
        assert result == {"analysis": "success"}
        mock_request.assert_called_once()
        client.close()
    
    @patch('httpx.Client.request')
    def test_analyze_cv_validation_error(self, mock_request):
        """Test CV analysis with empty text raises ValidationError"""
        client = AiCVClient(api_key="test-key")
        
        with pytest.raises(ValidationError, match="CV text cannot be empty"):
            client.analyze_cv("")
        
        client.close()
    
    @patch('httpx.Client.request')
    def test_analyze_cv_authentication_error(self, mock_request):
        """Test CV analysis with authentication error"""
        # Mock 401 response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_request.return_value = mock_response
        
        client = AiCVClient(api_key="test-key")
        
        with pytest.raises(AuthenticationError, match="Invalid API key"):
            client.analyze_cv("Test CV content")
        
        client.close()
    
    @patch('httpx.Client.request')
    def test_analyze_cv_api_error(self, mock_request):
        """Test CV analysis with API error"""
        # Mock 400 response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Bad request"}
        mock_request.return_value = mock_response
        
        client = AiCVClient(api_key="test-key")
        
        with pytest.raises(APIError, match="Bad request"):
            client.analyze_cv("Test CV content")
        
        client.close()
    
    @patch('httpx.Client.request')
    def test_generate_cv_section_success(self, mock_request):
        """Test successful CV section generation"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"generated": "content"}
        mock_request.return_value = mock_response
        
        client = AiCVClient(api_key="test-key")
        result = client.generate_cv_section("summary", "context", "requirements")
        
        assert result == {"generated": "content"}
        mock_request.assert_called_once()
        client.close()
    
    @patch('httpx.Client.request')
    def test_generate_cv_section_validation_error(self, mock_request):
        """Test CV section generation with validation error"""
        client = AiCVClient(api_key="test-key")
        
        with pytest.raises(ValidationError, match="Section type and context are required"):
            client.generate_cv_section("", "context")
        
        with pytest.raises(ValidationError, match="Section type and context are required"):
            client.generate_cv_section("summary", "")
        
        client.close()
    
    @patch('httpx.Client.request')
    def test_optimize_cv_success(self, mock_request):
        """Test successful CV optimization"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"optimization": "suggestions"}
        mock_request.return_value = mock_response
        
        client = AiCVClient(api_key="test-key")
        result = client.optimize_cv("Test CV content", "Target job")
        
        assert result == {"optimization": "suggestions"}
        mock_request.assert_called_once()
        client.close()
    
    @patch('httpx.Client.request')
    def test_optimize_cv_validation_error(self, mock_request):
        """Test CV optimization with validation error"""
        client = AiCVClient(api_key="test-key")
        
        with pytest.raises(ValidationError, match="CV text cannot be empty"):
            client.optimize_cv("")
        
        client.close()
    
    @patch('httpx.Client.request')
    def test_get_account_info_success(self, mock_request):
        """Test successful account info retrieval"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"account": "info"}
        mock_request.return_value = mock_response
        
        client = AiCVClient(api_key="test-key")
        result = client.get_account_info()
        
        assert result == {"account": "info"}
        mock_request.assert_called_once()
        client.close()
    
    @patch('httpx.Client.request')
    def test_health_check_success(self, mock_request):
        """Test successful health check"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy"}
        mock_request.return_value = mock_response
        
        client = AiCVClient(api_key="test-key")
        result = client.health_check()
        
        assert result == {"status": "healthy"}
        mock_request.assert_called_once()
        client.close()
    
    @patch('httpx.Client.request')
    def test_request_error_handling(self, mock_request):
        """Test request error handling"""
        # Mock request error
        mock_request.side_effect = httpx.RequestError("Network error")
        
        client = AiCVClient(api_key="test-key")
        
        with pytest.raises(Exception, match="Request failed: Network error"):
            client.analyze_cv("Test CV content")
        
        client.close()
