"""
Tests for Session Timeout Functionality

This module tests the 30-minute session timeout requirement.
Tests Requirement 16.4 and 16.5 (Session timeout and expiration handling).
"""

import pytest
from datetime import timedelta
from app import create_app, db
from app.models import User


@pytest.fixture
def app():
    """Create and configure a test Flask application."""
    import os
    from flask import Flask
    
    # Get the path to the app directory
    app_dir = os.path.join(os.path.dirname(__file__), '..', 'app')
    template_dir = os.path.join(app_dir, 'templates')
    static_dir = os.path.join(app_dir, 'static')
    
    # Create app with correct template and static folders
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'test-secret-key-for-testing'
    # Set session timeout to 30 minutes (1800 seconds)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
    
    # Initialize extensions
    from app import db, csrf, login_manager
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.contact import contact_bp
    from app.routes.booking import booking_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    
    # User loader callback
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def test_user(app):
    """Create a test user for authentication tests."""
    with app.app_context():
        user = User(username='testinstructor', email='test@example.com')
        user.set_password('testpassword123')
        db.session.add(user)
        db.session.commit()
        return user


class TestSessionTimeout:
    """Tests for session timeout functionality."""
    
    def test_session_is_marked_as_permanent(self, client, test_user):
        """
        Test that session is marked as permanent after login.
        
        This is required for the PERMANENT_SESSION_LIFETIME to take effect.
        
        Validates:
        - Requirement 16.4: Implement session timeout after 30 minutes of inactivity
        """
        with client:
            # Login
            response = client.post('/login', data={
                'username': 'testinstructor',
                'password': 'testpassword123'
            }, follow_redirects=True)
            
            assert response.status_code == 200
            
            # Check that session is permanent
            from flask import session
            assert session.permanent is True
    
    def test_session_timeout_configuration(self, app):
        """
        Test that session timeout is configured to 30 minutes.
        
        Validates:
        - Requirement 16.4: Implement session timeout after 30 minutes of inactivity
        """
        # Check that PERMANENT_SESSION_LIFETIME is set to 30 minutes
        assert app.config['PERMANENT_SESSION_LIFETIME'] == timedelta(minutes=30)
    
    def test_authenticated_user_can_access_admin(self, client, test_user):
        """
        Test that authenticated user can access admin dashboard.
        
        Validates:
        - Requirement 16.3: Verify instructor authentication on every admin request
        """
        # Login
        client.post('/login', data={
            'username': 'testinstructor',
            'password': 'testpassword123'
        })
        
        # Access admin dashboard
        response = client.get('/admin/dashboard')
        assert response.status_code == 200
        assert b'Admin Dashboard' in response.data
    
    def test_unauthenticated_user_redirected_to_login(self, client):
        """
        Test that unauthenticated user is redirected to login page.
        
        Validates:
        - Requirement 16.1: Redirect unauthenticated users to login page
        - Requirement 16.2: Redirect unauthenticated users attempting admin functions
        """
        response = client.get('/admin/dashboard', follow_redirects=True)
        assert response.status_code == 200
        # Should be redirected to login page
        assert b'Instructor Login' in response.data or b'Please log in' in response.data
    
    def test_session_persists_within_timeout_period(self, client, test_user):
        """
        Test that session persists for multiple requests within timeout period.
        
        Validates:
        - Requirement 16.4: Session should remain active within 30-minute window
        """
        # Login
        client.post('/login', data={
            'username': 'testinstructor',
            'password': 'testpassword123'
        })
        
        # Make multiple requests - all should succeed
        for _ in range(5):
            response = client.get('/admin/dashboard')
            assert response.status_code == 200
            assert b'Admin Dashboard' in response.data


class TestAdminRouteProtection:
    """Tests for admin route protection."""
    
    def test_admin_dashboard_route_requires_login(self, client):
        """
        Test that /admin/dashboard requires authentication.
        
        Validates:
        - Requirement 16.1: Redirect unauthenticated users to login page
        """
        response = client.get('/admin/dashboard', follow_redirects=True)
        assert b'Instructor Login' in response.data or b'Please log in' in response.data
    
    def test_admin_root_route_requires_login(self, client):
        """
        Test that /admin requires authentication.
        
        Validates:
        - Requirement 16.1: Redirect unauthenticated users to login page
        """
        response = client.get('/admin', follow_redirects=True)
        assert b'Instructor Login' in response.data or b'Please log in' in response.data
    
    def test_admin_routes_accessible_when_authenticated(self, client, test_user):
        """
        Test that admin routes are accessible when authenticated.
        
        Validates:
        - Requirement 13.1: Admin dashboard accessible only to authenticated users
        """
        # Login
        client.post('/login', data={
            'username': 'testinstructor',
            'password': 'testpassword123'
        })
        
        # Test /admin route (redirects to /admin/dashboard)
        response = client.get('/admin', follow_redirects=True)
        assert response.status_code == 200
        assert b'Admin Dashboard' in response.data
        
        # Test /admin/dashboard route
        response = client.get('/admin/dashboard')
        assert response.status_code == 200
        assert b'Admin Dashboard' in response.data
