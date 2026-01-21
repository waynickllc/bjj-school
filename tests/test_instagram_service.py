"""
Unit tests for InstagramService

These tests verify the Instagram API integration functionality.
"""

import pytest
from unittest.mock import Mock, patch
from app.services.instagram import InstagramService, InstagramAPIError


class TestInstagramService:
    """Test suite for InstagramService class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.access_token = "test_access_token"
        self.user_id = "test_user_id"
        self.service = InstagramService(self.access_token, self.user_id)
    
    def test_init(self):
        """Test InstagramService initialization"""
        assert self.service.access_token == self.access_token
        assert self.service.user_id == self.user_id
        assert self.service.base_url == "https://graph.instagram.com"
    
    @patch('app.services.instagram.requests.get')
    def test_fetch_recent_media_success(self, mock_get):
        """Test successful fetch of recent media"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [
                {
                    'id': '123',
                    'media_type': 'IMAGE',
                    'media_url': 'https://example.com/image1.jpg',
                    'permalink': 'https://instagram.com/p/abc123',
                    'caption': 'Test caption',
                    'timestamp': '2024-01-01T12:00:00+0000'
                },
                {
                    'id': '456',
                    'media_type': 'VIDEO',
                    'media_url': 'https://example.com/video1.mp4',
                    'permalink': 'https://instagram.com/p/def456',
                    'timestamp': '2024-01-02T12:00:00+0000'
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Call method
        result = self.service.fetch_recent_media(limit=2)
        
        # Verify results
        assert len(result) == 2
        assert result[0]['id'] == '123'
        assert result[0]['media_type'] == 'IMAGE'
        assert result[1]['id'] == '456'
        
        # Verify API was called correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert f"{self.service.base_url}/{self.user_id}/media" in call_args[0]
        assert call_args[1]['params']['access_token'] == self.access_token
        assert call_args[1]['params']['limit'] == 2
    
    @patch('app.services.instagram.requests.get')
    def test_fetch_recent_media_default_limit(self, mock_get):
        """Test fetch_recent_media uses default limit of 6"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': []}
        mock_get.return_value = mock_response
        
        self.service.fetch_recent_media()
        
        call_args = mock_get.call_args
        assert call_args[1]['params']['limit'] == 6
    
    @patch('app.services.instagram.requests.get')
    def test_fetch_recent_media_api_error(self, mock_get):
        """Test handling of API error response"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.content = b'{"error": {"message": "Invalid token"}}'
        mock_response.json.return_value = {
            'error': {'message': 'Invalid token'}
        }
        mock_get.return_value = mock_response
        
        with pytest.raises(InstagramAPIError) as exc_info:
            self.service.fetch_recent_media()
        
        assert "400" in str(exc_info.value)
        assert "Invalid token" in str(exc_info.value)
    
    @patch('app.services.instagram.requests.get')
    def test_fetch_recent_media_timeout(self, mock_get):
        """Test handling of request timeout"""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout()
        
        with pytest.raises(InstagramAPIError) as exc_info:
            self.service.fetch_recent_media()
        
        assert "timed out" in str(exc_info.value)
    
    @patch('app.services.instagram.requests.get')
    def test_fetch_recent_media_connection_error(self, mock_get):
        """Test handling of connection error"""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        with pytest.raises(InstagramAPIError) as exc_info:
            self.service.fetch_recent_media()
        
        assert "Failed to connect" in str(exc_info.value)
    
    @patch('app.services.instagram.requests.get')
    def test_fetch_recent_media_invalid_json(self, mock_get):
        """Test handling of invalid JSON response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response
        
        with pytest.raises(InstagramAPIError) as exc_info:
            self.service.fetch_recent_media()
        
        assert "Failed to parse" in str(exc_info.value)
    
    @patch('app.services.instagram.requests.get')
    def test_is_token_valid_success(self, mock_get):
        """Test successful token validation"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {
                'is_valid': True,
                'user_id': self.user_id
            }
        }
        mock_get.return_value = mock_response
        
        result = self.service.is_token_valid()
        
        assert result is True
        
        # Verify API was called correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "debug_token" in call_args[0][0]
        assert call_args[1]['params']['input_token'] == self.access_token
    
    @patch('app.services.instagram.requests.get')
    def test_is_token_valid_invalid_token(self, mock_get):
        """Test token validation with invalid token"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {
                'is_valid': False
            }
        }
        mock_get.return_value = mock_response
        
        result = self.service.is_token_valid()
        
        assert result is False
    
    @patch('app.services.instagram.requests.get')
    def test_is_token_valid_api_error(self, mock_get):
        """Test token validation with API error"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_get.return_value = mock_response
        
        result = self.service.is_token_valid()
        
        assert result is False
    
    @patch('app.services.instagram.requests.get')
    def test_is_token_valid_network_error(self, mock_get):
        """Test token validation with network error"""
        import requests
        mock_get.side_effect = requests.exceptions.RequestException()
        
        result = self.service.is_token_valid()
        
        assert result is False
    
    @patch('app.services.instagram.requests.get')
    def test_is_token_valid_malformed_response(self, mock_get):
        """Test token validation with malformed response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}  # Missing 'data' key
        mock_get.return_value = mock_response
        
        result = self.service.is_token_valid()
        
        assert result is False
