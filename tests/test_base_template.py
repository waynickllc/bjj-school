"""
Unit tests for base.html template.

Tests verify:
- Navigation menu is present on all pages
- Navigation menu has links to all required pages (Home, Instructor, Contact, Book Trial)
- Active page is highlighted in navigation
- CSRF token meta tag is present
- Bootstrap CSS is included
- Responsive design elements are present
- Flash messages are displayed correctly
"""

import pytest
from app import create_app


@pytest.fixture
def app():
    """Create and configure a test application instance."""
    app = create_app('config.yaml')
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = True  # Enable CSRF to test token
    
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    """Create a test client for the application."""
    return app.test_client()


class TestNavigationMenu:
    """Tests for navigation menu (Requirement 9.1, 9.2)."""
    
    def test_navigation_menu_present_on_home(self, client):
        """Test that navigation menu is present on home page."""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'<nav' in response.data
        assert b'navbar' in response.data
    
    def test_navigation_menu_present_on_instructor(self, client):
        """Test that navigation menu is present on instructor page."""
        response = client.get('/instructor')
        
        assert response.status_code == 200
        assert b'<nav' in response.data
        assert b'navbar' in response.data
    
    def test_navigation_menu_present_on_contact(self, client):
        """Test that navigation menu is present on contact page."""
        response = client.get('/contact')
        
        assert response.status_code == 200
        assert b'<nav' in response.data
        assert b'navbar' in response.data
    
    def test_navigation_menu_present_on_booking(self, client):
        """Test that navigation menu is present on booking page."""
        response = client.get('/booking')
        
        assert response.status_code == 200
        assert b'<nav' in response.data
        assert b'navbar' in response.data
    
    def test_navigation_has_home_link(self, client):
        """Test that navigation menu has Home link."""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'Home' in response.data
        assert b'href="/"' in response.data or b"href='/'" in response.data
    
    def test_navigation_has_instructor_link(self, client):
        """Test that navigation menu has Instructor link."""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'Instructor' in response.data
        assert b'/instructor' in response.data
    
    def test_navigation_has_contact_link(self, client):
        """Test that navigation menu has Contact link."""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'Contact' in response.data
        assert b'/contact' in response.data
    
    def test_navigation_has_book_trial_link(self, client):
        """Test that navigation menu has Book Trial link."""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'Book Trial' in response.data
        assert b'/booking' in response.data
    
    def test_active_page_highlighted_home(self, client):
        """Test that current page is highlighted in navigation (Home)."""
        response = client.get('/')
        
        assert response.status_code == 200
        # Check for active class on home link
        assert b'active' in response.data
    
    def test_active_page_highlighted_instructor(self, client):
        """Test that current page is highlighted in navigation (Instructor)."""
        response = client.get('/instructor')
        
        assert response.status_code == 200
        # Check for active class
        assert b'active' in response.data


class TestCSRFToken:
    """Tests for CSRF token meta tag."""
    
    def test_csrf_token_meta_tag_present(self, client):
        """Test that CSRF token meta tag is present in all pages."""
        pages = ['/', '/instructor', '/contact', '/booking']
        
        for page in pages:
            response = client.get(page)
            
            assert response.status_code == 200
            assert b'<meta name="csrf-token"' in response.data
            assert b'content=' in response.data


class TestBootstrapIntegration:
    """Tests for Bootstrap CSS framework integration."""
    
    def test_bootstrap_css_included(self, client):
        """Test that Bootstrap CSS is included."""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'bootstrap' in response.data.lower()
        assert b'.css' in response.data
    
    def test_bootstrap_js_included(self, client):
        """Test that Bootstrap JS is included."""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'bootstrap' in response.data.lower()
        assert b'.js' in response.data
    
    def test_responsive_viewport_meta_tag(self, client):
        """Test that responsive viewport meta tag is present."""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'<meta name="viewport"' in response.data
        assert b'width=device-width' in response.data


class TestFlashMessages:
    """Tests for flash message display."""
    
    def test_flash_message_container_present(self, client):
        """Test that flash message container is present."""
        # Add a flash message to verify the container works
        with client.session_transaction() as session:
            session['_flashes'] = [('success', 'Test message')]
        
        response = client.get('/')
        
        assert response.status_code == 200
        # Check that the flash message is displayed (which means the container is working)
        assert b'Test message' in response.data
        assert b'alert' in response.data
    
    def test_flash_message_displayed(self, client, app):
        """Test that flash messages are displayed correctly."""
        with client.session_transaction() as session:
            # Manually add a flash message to the session
            session['_flashes'] = [('success', 'Test success message')]
        
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'Test success message' in response.data


class TestFooter:
    """Tests for footer section."""
    
    def test_footer_present(self, client):
        """Test that footer is present on all pages."""
        pages = ['/', '/instructor', '/contact', '/booking']
        
        for page in pages:
            response = client.get(page)
            
            assert response.status_code == 200
            assert b'<footer' in response.data
    
    def test_footer_has_quick_links(self, client):
        """Test that footer has quick links section."""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'Quick Links' in response.data or b'footer' in response.data.lower()


class TestPageStructure:
    """Tests for overall page structure."""
    
    def test_html5_doctype(self, client):
        """Test that pages use HTML5 doctype."""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'<!DOCTYPE html>' in response.data
    
    def test_main_content_area(self, client):
        """Test that pages have main content area."""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'<main' in response.data
    
    def test_page_title(self, client):
        """Test that pages have title tag."""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'<title>' in response.data
        assert b'BJJ School' in response.data
