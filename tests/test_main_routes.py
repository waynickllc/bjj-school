"""
Unit tests for main routes (home and instructor pages).

Tests verify:
- Home route renders correctly with Instagram photos
- Home route handles Instagram API failures gracefully
- Instructor route renders correctly with instructor data
- Error handling for Instagram API failures
"""

import pytest
from unittest.mock import patch, MagicMock
from app import create_app, db
from app.services.instagram import InstagramAPIError


@pytest.fixture
def app():
    """Create and configure a test application instance."""
    app = create_app('config.yaml')
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    """Create a test client for the application."""
    return app.test_client()


class TestHomeRoute:
    """Tests for the home route."""
    
    def test_home_route_renders(self, client):
        """Test that home route returns 200 and renders template."""
        with patch('app.routes.main.InstagramService') as mock_service:
            # Mock successful Instagram API response
            mock_instance = MagicMock()
            mock_instance.fetch_recent_media.return_value = [
                {
                    'id': '123',
                    'media_type': 'IMAGE',
                    'media_url': 'https://example.com/photo1.jpg',
                    'permalink': 'https://instagram.com/p/123',
                    'caption': 'Test photo 1',
                    'timestamp': '2024-01-01T12:00:00+0000'
                }
            ]
            mock_service.return_value = mock_instance
            
            response = client.get('/')
            
            assert response.status_code == 200
            assert b'Welcome to Our BJJ School' in response.data
    
    def test_home_route_with_instagram_photos(self, client):
        """Test that home route displays Instagram photos when API succeeds."""
        with patch('app.routes.main.InstagramService') as mock_service:
            # Mock successful Instagram API response with multiple photos
            mock_instance = MagicMock()
            mock_instance.fetch_recent_media.return_value = [
                {
                    'id': '123',
                    'media_type': 'IMAGE',
                    'media_url': 'https://example.com/photo1.jpg',
                    'permalink': 'https://instagram.com/p/123',
                    'caption': 'Training session',
                    'timestamp': '2024-01-01T12:00:00+0000'
                },
                {
                    'id': '456',
                    'media_type': 'IMAGE',
                    'media_url': 'https://example.com/photo2.jpg',
                    'permalink': 'https://instagram.com/p/456',
                    'caption': 'Competition day',
                    'timestamp': '2024-01-02T12:00:00+0000'
                }
            ]
            mock_service.return_value = mock_instance
            
            response = client.get('/')
            
            assert response.status_code == 200
            assert b'https://example.com/photo1.jpg' in response.data
            assert b'https://example.com/photo2.jpg' in response.data
            assert b'https://instagram.com/p/123' in response.data
            assert b'https://instagram.com/p/456' in response.data
    
    def test_home_route_instagram_api_error(self, client):
        """Test that home route handles Instagram API errors gracefully."""
        with patch('app.routes.main.InstagramService') as mock_service:
            # Mock Instagram API error
            mock_instance = MagicMock()
            mock_instance.fetch_recent_media.side_effect = InstagramAPIError("API error")
            mock_service.return_value = mock_instance
            
            response = client.get('/')
            
            # Should still return 200 (page loads successfully)
            assert response.status_code == 200
            # Should display fallback message
            assert b'Instagram photos temporarily unavailable' in response.data
    
    def test_home_route_missing_instagram_credentials(self, client, app):
        """Test that home route handles missing Instagram credentials."""
        with app.app_context():
            # Temporarily remove Instagram credentials
            original_token = app.config.get('INSTAGRAM_ACCESS_TOKEN')
            original_user_id = app.config.get('INSTAGRAM_USER_ID')
            app.config['INSTAGRAM_ACCESS_TOKEN'] = None
            app.config['INSTAGRAM_USER_ID'] = None
            
            try:
                response = client.get('/')
                
                # Should still return 200 (page loads successfully)
                assert response.status_code == 200
                # Should display fallback message
                assert b'Instagram photos temporarily unavailable' in response.data
            finally:
                # Restore credentials
                app.config['INSTAGRAM_ACCESS_TOKEN'] = original_token
                app.config['INSTAGRAM_USER_ID'] = original_user_id
    
    def test_home_route_unexpected_error(self, client):
        """Test that home route handles unexpected errors gracefully."""
        with patch('app.routes.main.InstagramService') as mock_service:
            # Mock unexpected error
            mock_service.side_effect = Exception("Unexpected error")
            
            response = client.get('/')
            
            # Should still return 200 (page loads successfully)
            assert response.status_code == 200
            # Should display fallback message
            assert b'Instagram photos temporarily unavailable' in response.data
    
    def test_home_route_empty_instagram_photos(self, client):
        """Test that home route handles empty Instagram response."""
        with patch('app.routes.main.InstagramService') as mock_service:
            # Mock empty Instagram API response
            mock_instance = MagicMock()
            mock_instance.fetch_recent_media.return_value = []
            mock_service.return_value = mock_instance
            
            response = client.get('/')
            
            assert response.status_code == 200
            # Should display empty message
            assert b'No photos available at this time' in response.data


class TestInstructorRoute:
    """Tests for the instructor route."""
    
    def test_instructor_route_renders(self, client):
        """Test that instructor route returns 200 and renders template."""
        response = client.get('/instructor')
        
        assert response.status_code == 200
        assert b'Meet Your Instructor' in response.data
    
    def test_instructor_route_displays_bio(self, client):
        """Test that instructor route displays biographical information."""
        response = client.get('/instructor')
        
        assert response.status_code == 200
        assert b'Master Instructor' in response.data
        assert b'Brazilian Jiu-Jitsu instructor' in response.data
    
    def test_instructor_route_displays_qualifications(self, client):
        """Test that instructor route displays qualifications."""
        response = client.get('/instructor')
        
        assert response.status_code == 200
        assert b'Qualifications &amp; Certifications' in response.data or b'Qualifications & Certifications' in response.data
        assert b'Black Belt in Brazilian Jiu-Jitsu' in response.data
        assert b'Certified Gracie Jiu-Jitsu Instructor' in response.data
    
    def test_instructor_route_displays_training_history(self, client):
        """Test that instructor route displays training history."""
        response = client.get('/instructor')
        
        assert response.status_code == 200
        assert b'Training History' in response.data
        assert b'Trained under Master Carlos Gracie Jr.' in response.data
        assert b'Teaching BJJ since 2010' in response.data
    
    def test_instructor_route_has_cta_buttons(self, client):
        """Test that instructor route has call-to-action buttons."""
        response = client.get('/instructor')
        
        assert response.status_code == 200
        # Should have links to booking and contact pages
        assert b'Book a Trial Class' in response.data
        assert b'Contact Us' in response.data


class TestInstagramPhotoLinks:
    """Tests for Instagram photo links (Property 10)."""
    
    def test_instagram_photos_have_target_blank(self, client):
        """Test that Instagram photo links open in new tab (target="_blank")."""
        with patch('app.routes.main.InstagramService') as mock_service:
            # Mock successful Instagram API response
            mock_instance = MagicMock()
            mock_instance.fetch_recent_media.return_value = [
                {
                    'id': '123',
                    'media_type': 'IMAGE',
                    'media_url': 'https://example.com/photo1.jpg',
                    'permalink': 'https://instagram.com/p/123',
                    'caption': 'Test photo',
                    'timestamp': '2024-01-01T12:00:00+0000'
                }
            ]
            mock_service.return_value = mock_instance
            
            response = client.get('/')
            
            assert response.status_code == 200
            # Check that links have target="_blank"
            assert b'target="_blank"' in response.data
            # Check that links have rel="noopener noreferrer" for security
            assert b'rel="noopener noreferrer"' in response.data
    
    def test_instagram_photos_have_valid_permalink(self, client):
        """Test that Instagram photos have valid permalink URLs."""
        with patch('app.routes.main.InstagramService') as mock_service:
            # Mock successful Instagram API response
            mock_instance = MagicMock()
            test_permalink = 'https://instagram.com/p/test123'
            mock_instance.fetch_recent_media.return_value = [
                {
                    'id': '123',
                    'media_type': 'IMAGE',
                    'media_url': 'https://example.com/photo1.jpg',
                    'permalink': test_permalink,
                    'caption': 'Test photo',
                    'timestamp': '2024-01-01T12:00:00+0000'
                }
            ]
            mock_service.return_value = mock_instance
            
            response = client.get('/')
            
            assert response.status_code == 200
            # Check that permalink is in the response
            assert test_permalink.encode() in response.data
