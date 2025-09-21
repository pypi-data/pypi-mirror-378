"""
Tests for the Rose Python SDK client.
"""

import pytest
import json
from unittest.mock import Mock, patch
from rose_sdk import RoseClient
from rose_sdk.exceptions import (
    RoseAPIError,
    RoseAuthenticationError,
    RosePermissionError,
    RoseNotFoundError,
    RoseValidationError,
    RoseServerError,
    RoseTimeoutError,
)


class TestRoseClient:
    """Test cases for RoseClient."""
    
    def test_client_initialization(self):
        """Test client initialization."""
        client = RoseClient(
            base_url="https://api.example.com",
            access_token="test_token",
            timeout=60,
            max_retries=5
        )
        
        assert client.base_url == "https://api.example.com"
        assert client.access_token == "test_token"
        assert client.timeout == 60
        assert "Authorization" in client.session.headers
        assert client.session.headers["Authorization"] == "Bearer test_token"
    
    def test_set_access_token(self):
        """Test setting access token."""
        client = RoseClient(base_url="https://api.example.com")
        client.set_access_token("new_token")
        
        assert client.access_token == "new_token"
        assert client.session.headers["Authorization"] == "Bearer new_token"
    
    @patch('requests.Session.request')
    def test_successful_request(self, mock_request):
        """Test successful API request."""
        # Mock successful response
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "OK", "data": {"id": "123"}}
        mock_request.return_value = mock_response
        
        client = RoseClient(base_url="https://api.example.com")
        response = client.get("/test")
        
        assert response == {"message": "OK", "data": {"id": "123"}}
        mock_request.assert_called_once()
    
    @patch('requests.Session.request')
    def test_authentication_error(self, mock_request):
        """Test authentication error handling."""
        # Mock 401 response
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "message": "Unauthorized",
            "error": "authorization failed"
        }
        mock_request.return_value = mock_response
        
        client = RoseClient(base_url="https://api.example.com")
        
        with pytest.raises(RoseAuthenticationError) as exc_info:
            client.get("/test")
        
        assert exc_info.value.status_code == 401
        assert "authorization failed" in exc_info.value.message
    
    @patch('requests.Session.request')
    def test_permission_error(self, mock_request):
        """Test permission error handling."""
        # Mock 403 response
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 403
        mock_response.json.return_value = {
            "message": "Forbidden",
            "error": "permission denied"
        }
        mock_request.return_value = mock_response
        
        client = RoseClient(base_url="https://api.example.com")
        
        with pytest.raises(RosePermissionError) as exc_info:
            client.get("/test")
        
        assert exc_info.value.status_code == 403
        assert "permission denied" in exc_info.value.message
    
    @patch('requests.Session.request')
    def test_not_found_error(self, mock_request):
        """Test not found error handling."""
        # Mock 404 response
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_response.json.return_value = {
            "message": "Not Found",
            "error": "data not found"
        }
        mock_request.return_value = mock_response
        
        client = RoseClient(base_url="https://api.example.com")
        
        with pytest.raises(RoseNotFoundError) as exc_info:
            client.get("/test")
        
        assert exc_info.value.status_code == 404
        assert "data not found" in exc_info.value.message
    
    @patch('requests.Session.request')
    def test_validation_error(self, mock_request):
        """Test validation error handling."""
        # Mock 400 response
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "message": "Bad Request",
            "error": "invalid parameter"
        }
        mock_request.return_value = mock_response
        
        client = RoseClient(base_url="https://api.example.com")
        
        with pytest.raises(RoseValidationError) as exc_info:
            client.get("/test")
        
        assert exc_info.value.status_code == 400
        assert "invalid parameter" in exc_info.value.message
    
    @patch('requests.Session.request')
    def test_server_error(self, mock_request):
        """Test server error handling."""
        # Mock 500 response
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 500
        mock_response.json.return_value = {
            "message": "Internal Server Error",
            "error": "server failure"
        }
        mock_request.return_value = mock_response
        
        client = RoseClient(base_url="https://api.example.com")
        
        with pytest.raises(RoseServerError) as exc_info:
            client.get("/test")
        
        assert exc_info.value.status_code == 500
        assert "server failure" in exc_info.value.message
    
    @patch('requests.Session.request')
    def test_timeout_error(self, mock_request):
        """Test timeout error handling."""
        # Mock 504 response
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 504
        mock_response.json.return_value = {
            "message": "Gateway Timeout",
            "error": "request timed out"
        }
        mock_request.return_value = mock_response
        
        client = RoseClient(base_url="https://api.example.com")
        
        with pytest.raises(RoseTimeoutError) as exc_info:
            client.get("/test")
        
        assert exc_info.value.status_code == 504
        assert "request timed out" in exc_info.value.message
    
    @patch('requests.Session.request')
    def test_health_check(self, mock_request):
        """Test health check endpoint."""
        # Mock successful health check response
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy"}
        mock_request.return_value = mock_response
        
        client = RoseClient(base_url="https://api.example.com")
        response = client.health_check()
        
        assert response == {"status": "healthy"}
        # Check that the request was made with the correct parameters
        # Note: requests adds default headers, so we check the call args
        call_args = mock_request.call_args
        assert call_args[1]['method'] == 'GET'
        assert call_args[1]['url'] == 'https://api.example.com/healthcheck'
        assert call_args[1]['params'] is None
        assert call_args[1]['data'] is None
        assert call_args[1]['timeout'] == 30
        # Headers will contain default requests headers
        assert 'headers' in call_args[1]
