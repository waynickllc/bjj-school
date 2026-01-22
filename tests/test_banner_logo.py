"""
Unit tests for banner and logo support (Task 14.3).

Tests verify:
- Context processor provides banner_url, logo_url, and site_name
- Logo is displayed in navigation when logo_url is set
- Site name text is displayed when logo_url is None (fallback)
- Banner is displayed on homepage when banner_url is set
- Banner section is hidden when banner_url is None
- CSS styling for logo and banner is present

Validates Requirements: 9.3, 9.10
"""

import pytest
from app import create_app


@pytest.fixture
def app():
    """Create and configure a test application instance."""
    app = create_app('config.yaml')
    app.config['TESTING'] = True
    
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    """Create a test client for the application."""
    return app.test_client()


class TestContextProcessor:
    """Tests for site settings context processor."""
    
    def test_context_processor_provides_site_name(self, app):
        """Test that context processor provides site_name."""
        with app.test_request_context('/'):
            from flask import render_template_string
            
            result = render_template_string('{{ site_name }}')
            assert result == 'BJJ SCHOOL'
    
    def test_context_processor_provides_logo_url(self, app):
        """Test that context processor provides logo_url."""
        with app.test_request_context('/'):
            from flask import render_template_string
            
            # Should be None by default (until task 22.1)
            result = render_template_string('{{ logo_url }}')
            assert result == 'None'
    
    def test_context_processor_provides_banner_url(self, app):
        """Test that context processor provides banner_url."""
        with app.test_request_context('/'):
            from flask import render_template_string
            
            # Should be None by default (until task 22.1)
            result = render_template_string('{{ banner_url }}')
            assert result == 'None'


class TestLogoFallback:
    """Tests for logo fallback behavior (Requirement 9.3)."""
    
    def test_site_name_displayed_when_no_logo(self, client):
        """Test that site name text is displayed when logo_url is None."""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'BJJ SCHOOL' in response.data
    
    def test_no_broken_image_tags(self, client):
        """Test that no broken image tags are rendered when logo_url is None."""
        response = client.get('/')
        
        assert response.status_code == 200
        # Should not have img tag with None as src
        assert b'<img src="None"' not in response.data
    
    def test_navbar_brand_present(self, client):
        """Test that navbar-brand element is present."""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'navbar-brand' in response.data


class TestLogoDisplay:
    """Tests for logo display when logo_url is set."""
    
    def test_logo_image_displayed_when_url_set(self, app):
        """Test that logo image is displayed when logo_url is set."""
        # Override context processor to simulate having a logo
        @app.context_processor
        def inject_test_logo():
            return {
                'banner_url': None,
                'logo_url': '/static/uploads/logo.png',
                'site_name': 'BJJ SCHOOL'
            }
        
        with app.test_client() as client:
            response = client.get('/')
            
            assert response.status_code == 200
            assert b'/static/uploads/logo.png' in response.data
            assert b'navbar-logo' in response.data
    
    def test_logo_has_alt_text(self, app):
        """Test that logo image has proper alt text."""
        @app.context_processor
        def inject_test_logo():
            return {
                'banner_url': None,
                'logo_url': '/static/uploads/logo.png',
                'site_name': 'BJJ SCHOOL'
            }
        
        with app.test_client() as client:
            response = client.get('/')
            
            assert response.status_code == 200
            assert b'alt="BJJ SCHOOL"' in response.data


class TestBannerHidden:
    """Tests for banner hidden behavior (Requirement 9.10)."""
    
    def test_banner_section_hidden_when_no_banner(self, client):
        """Test that banner section is hidden when banner_url is None."""
        response = client.get('/')
        
        assert response.status_code == 200
        # Banner section should not be present
        assert b'<section class="banner' not in response.data


class TestBannerDisplay:
    """Tests for banner display when banner_url is set."""
    
    def test_banner_displayed_when_url_set(self, app):
        """Test that banner is displayed when banner_url is set."""
        @app.context_processor
        def inject_test_banner():
            return {
                'banner_url': '/static/uploads/banner.jpg',
                'logo_url': None,
                'site_name': 'BJJ SCHOOL'
            }
        
        with app.test_client() as client:
            response = client.get('/')
            
            assert response.status_code == 200
            assert b'<section class="banner' in response.data
            assert b'/static/uploads/banner.jpg' in response.data
    
    def test_banner_has_alt_text(self, app):
        """Test that banner image has proper alt text."""
        @app.context_processor
        def inject_test_banner():
            return {
                'banner_url': '/static/uploads/banner.jpg',
                'logo_url': None,
                'site_name': 'BJJ SCHOOL'
            }
        
        with app.test_client() as client:
            response = client.get('/')
            
            assert response.status_code == 200
            assert b'alt="BJJ SCHOOL Banner"' in response.data
    
    def test_banner_only_on_homepage(self, app):
        """Test that banner is only displayed on homepage."""
        @app.context_processor
        def inject_test_banner():
            return {
                'banner_url': '/static/uploads/banner.jpg',
                'logo_url': None,
                'site_name': 'BJJ SCHOOL'
            }
        
        with app.test_client() as client:
            # Banner should be on home page
            response = client.get('/')
            assert b'<section class="banner' in response.data
            
            # Banner should NOT be on other pages
            response = client.get('/instructor')
            assert b'<section class="banner' not in response.data
            
            response = client.get('/contact')
            assert b'<section class="banner' not in response.data


class TestCSSStyles:
    """Tests for CSS styling."""
    
    def test_navbar_logo_css_exists(self):
        """Test that navbar-logo CSS class is defined."""
        with open('app/static/css/style.css', 'r') as f:
            css = f.read()
        
        assert '.navbar-logo' in css
        assert 'height: 50px' in css
        assert 'object-fit: contain' in css
    
    def test_banner_css_exists(self):
        """Test that banner CSS class is defined."""
        # Banner CSS is in home.html template (inline styles)
        with open('app/templates/home.html', 'r') as f:
            html = f.read()
        
        assert '.banner' in html
        assert 'max-height: 500px' in html


class TestIntegrationWithTask22_1:
    """Tests to verify readiness for task 22.1 (SiteSettings model)."""
    
    def test_templates_ready_for_site_settings(self, app):
        """Test that templates are ready to use SiteSettings model."""
        # Simulate what will happen in task 22.1
        @app.context_processor
        def inject_site_settings_from_db():
            # This simulates querying SiteSettings model
            return {
                'banner_url': '/static/uploads/banner.jpg',
                'logo_url': '/static/uploads/logo.png',
                'site_name': 'BJJ SCHOOL'
            }
        
        with app.test_client() as client:
            response = client.get('/')
            
            assert response.status_code == 200
            # Both banner and logo should be displayed
            assert b'/static/uploads/banner.jpg' in response.data
            assert b'/static/uploads/logo.png' in response.data
            assert b'navbar-logo' in response.data
            assert b'<section class="banner' in response.data
    
    def test_context_processor_has_todo_comment(self):
        """Test that context processor has TODO comment for task 22.1."""
        with open('app/__init__.py', 'r') as f:
            content = f.read()
        
        assert 'TODO: In task 22.1' in content
        assert 'SiteSettings' in content
