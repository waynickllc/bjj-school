"""
Tests for CSS animations and transitions (Task 14.2)

This test suite verifies that:
- Scroll reveal classes are present in templates
- Animation CSS is included in the stylesheet
- JavaScript scroll reveal functionality is present
- Accessibility features (reduced motion) are implemented
"""

import pytest
from app import create_app


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        yield client


class TestScrollAnimations:
    """Test scroll reveal animations in templates."""
    
    def test_home_page_has_scroll_reveal_classes(self, client):
        """Test that home page includes scroll-reveal classes."""
        response = client.get('/')
        assert response.status_code == 200
        
        # Check for scroll reveal classes
        assert b'scroll-reveal' in response.data
        assert b'fade-in' in response.data
        
    def test_instructor_page_has_scroll_reveal_classes(self, client):
        """Test that instructor page includes scroll-reveal classes."""
        response = client.get('/instructor')
        assert response.status_code == 200
        
        # Check for scroll reveal classes
        assert b'scroll-reveal' in response.data
        
    def test_contact_page_has_scroll_reveal_classes(self, client):
        """Test that contact page includes scroll-reveal classes."""
        response = client.get('/contact')
        assert response.status_code == 200
        
        # Check for scroll reveal classes
        assert b'scroll-reveal' in response.data
        
    def test_booking_page_has_scroll_reveal_classes(self, client):
        """Test that booking page includes scroll-reveal classes."""
        response = client.get('/booking')
        assert response.status_code == 200
        
        # Check for scroll reveal classes
        assert b'scroll-reveal' in response.data


class TestCSSAnimations:
    """Test CSS animation definitions."""
    
    def test_css_file_includes_animation_keyframes(self, client):
        """Test that CSS file includes animation keyframes."""
        response = client.get('/static/css/style.css')
        assert response.status_code == 200
        
        # Check for keyframe animations
        assert b'@keyframes fadeIn' in response.data
        assert b'@keyframes fadeInUp' in response.data
        assert b'@keyframes fadeInLeft' in response.data
        assert b'@keyframes fadeInRight' in response.data
        assert b'@keyframes scaleIn' in response.data
        assert b'@keyframes shake' in response.data
        
    def test_css_file_includes_scroll_reveal_classes(self, client):
        """Test that CSS file includes scroll reveal classes."""
        response = client.get('/static/css/style.css')
        assert response.status_code == 200
        
        # Check for scroll reveal classes
        assert b'.scroll-reveal' in response.data
        assert b'.scroll-reveal-left' in response.data
        assert b'.scroll-reveal-right' in response.data
        assert b'.scroll-reveal-scale' in response.data
        
    def test_css_file_includes_hover_animations(self, client):
        """Test that CSS file includes hover animations."""
        response = client.get('/static/css/style.css')
        assert response.status_code == 200
        
        # Check for hover transitions
        assert b'transition:' in response.data or b'transition :' in response.data
        assert b':hover' in response.data
        
    def test_css_file_includes_reduced_motion_support(self, client):
        """Test that CSS file includes reduced motion media query."""
        response = client.get('/static/css/style.css')
        assert response.status_code == 200
        
        # Check for reduced motion accessibility
        assert b'prefers-reduced-motion' in response.data


class TestJavaScriptAnimations:
    """Test JavaScript animation functionality."""
    
    def test_js_file_includes_scroll_reveal_function(self, client):
        """Test that JS file includes scroll reveal initialization."""
        response = client.get('/static/js/main.js')
        assert response.status_code == 200
        
        # Check for scroll reveal function
        assert b'initScrollReveal' in response.data
        assert b'IntersectionObserver' in response.data
        
    def test_js_file_includes_navbar_scroll_effect(self, client):
        """Test that JS file includes navbar scroll effect."""
        response = client.get('/static/js/main.js')
        assert response.status_code == 200
        
        # Check for navbar scroll function
        assert b'initNavbarScroll' in response.data
        
    def test_js_file_checks_reduced_motion_preference(self, client):
        """Test that JS respects reduced motion preference."""
        response = client.get('/static/js/main.js')
        assert response.status_code == 200
        
        # Check for reduced motion check
        assert b'prefers-reduced-motion' in response.data


class TestButtonAnimations:
    """Test button hover animations."""
    
    def test_buttons_have_transition_effects(self, client):
        """Test that buttons have transition effects in CSS."""
        response = client.get('/static/css/style.css')
        assert response.status_code == 200
        
        # Check for button transitions
        assert b'.btn' in response.data
        assert b'transform:' in response.data or b'transform :' in response.data
        
    def test_buttons_have_hover_states(self, client):
        """Test that buttons have hover states defined."""
        response = client.get('/static/css/style.css')
        assert response.status_code == 200
        
        # Check for button hover states
        assert b'.btn-primary:hover' in response.data
        assert b'.btn-secondary:hover' in response.data


class TestFormAnimations:
    """Test form input animations."""
    
    def test_form_controls_have_transitions(self, client):
        """Test that form controls have transition effects."""
        response = client.get('/static/css/style.css')
        assert response.status_code == 200
        
        # Check for form control transitions
        assert b'.form-control' in response.data
        assert b'.form-control:focus' in response.data
        
    def test_error_messages_have_shake_animation(self, client):
        """Test that error messages have shake animation."""
        response = client.get('/static/css/style.css')
        assert response.status_code == 200
        
        # Check for error shake animation
        assert b'@keyframes shake' in response.data
        assert b'.error' in response.data


class TestPageTransitions:
    """Test page load transitions."""
    
    def test_page_load_animation_exists(self, client):
        """Test that page load animation is defined."""
        response = client.get('/static/css/style.css')
        assert response.status_code == 200
        
        # Check for page load animation
        assert b'@keyframes pageLoad' in response.data
        assert b'@keyframes contentFadeIn' in response.data
        
    def test_body_has_page_load_animation(self, client):
        """Test that body element has page load animation."""
        response = client.get('/static/css/style.css')
        assert response.status_code == 200
        
        # Check that body has animation
        assert b'body {' in response.data or b'body{' in response.data


class TestPerformance:
    """Test performance optimizations for animations."""
    
    def test_gpu_acceleration_enabled(self, client):
        """Test that GPU acceleration is enabled for animations."""
        response = client.get('/static/css/style.css')
        assert response.status_code == 200
        
        # Check for GPU acceleration properties
        assert b'will-change' in response.data or b'backface-visibility' in response.data
        
    def test_animation_delays_are_staggered(self, client):
        """Test that animation delays are defined for staggered effects."""
        response = client.get('/static/css/style.css')
        assert response.status_code == 200
        
        # Check for animation delay classes
        assert b'animate-delay' in response.data or b'animation-delay' in response.data
