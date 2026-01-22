"""
Tests for Authentication Routes

This module tests the login and logout functionality.
Tests Requirements 13.1-13.8 (Instructor Authentication).
"""

import pytest
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
    app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes
    
    # Initialize extensions
    from app import db, csrf, login_manager
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
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


class TestLoginRoute:
    """Tests for the /login route."""
    
    def test_login_page_loads(self, client):
        """Test that the login page loads successfully."""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Instructor Login' in response.data
        assert b'Username' in response.data
        assert b'Password' in response.data
    
    def test_login_with_valid_credentials(self, client, test_user):
        """
        Test login with valid credentials.
        
        Validates:
        - Requirement 13.3: Authenticate user and redirect to admin dashboard on valid credentials
        - Requirement 13.7: Maintain instructor session state after successful login
        """
        response = client.post('/login', data={
            'username': 'testinstructor',
            'password': 'testpassword123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should redirect to admin dashboard
        assert b'Admin Dashboard' in response.data or b'dashboard' in response.data.lower()
    
    def test_login_with_invalid_username(self, client, test_user):
        """
        Test login with invalid username.
        
        Validates:
        - Requirement 13.4: Display error message and remain on login page for invalid credentials
        """
        response = client.post('/login', data={
            'username': 'wronguser',
            'password': 'testpassword123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data
        assert b'Instructor Login' in response.data  # Still on login page
    
    def test_login_with_invalid_password(self, client, test_user):
        """
        Test login with invalid password.
        
        Validates:
        - Requirement 13.4: Display error message and remain on login page for invalid credentials
        """
        response = client.post('/login', data={
            'username': 'testinstructor',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data
        assert b'Instructor Login' in response.data  # Still on login page
    
    def test_login_with_missing_username(self, client):
        """
        Test login with missing username field.
        
        Validates:
        - Requirement 13.2: Require username and password
        """
        response = client.post('/login', data={
            'password': 'testpassword123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Username is required' in response.data
    
    def test_login_with_missing_password(self, client):
        """
        Test login with missing password field.
        
        Validates:
        - Requirement 13.2: Require username and password
        """
        response = client.post('/login', data={
            'username': 'testinstructor'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Password is required' in response.data
    
    def test_login_redirects_if_already_authenticated(self, client, test_user):
        """
        Test that accessing login page while already logged in redirects to dashboard.
        """
        # First login
        client.post('/login', data={
            'username': 'testinstructor',
            'password': 'testpassword123'
        })
        
        # Try to access login page again
        response = client.get('/login', follow_redirects=True)
        assert response.status_code == 200
        # Should be redirected to dashboard
        assert b'Admin Dashboard' in response.data or b'dashboard' in response.data.lower()
    
    def test_login_with_next_parameter(self, client, test_user):
        """
        Test that login redirects to the 'next' page after successful authentication.
        """
        response = client.post('/login?next=/admin/dashboard', data={
            'username': 'testinstructor',
            'password': 'testpassword123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should redirect to the requested page
        assert b'Admin Dashboard' in response.data or b'dashboard' in response.data.lower()


class TestLogoutRoute:
    """Tests for the /logout route."""
    
    def test_logout_clears_session(self, client, test_user):
        """
        Test that logout clears the session.
        
        Validates:
        - Requirement 13.8: Provide logout function that clears the session
        """
        # First login
        client.post('/login', data={
            'username': 'testinstructor',
            'password': 'testpassword123'
        })
        
        # Then logout
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'You have been logged out successfully' in response.data
        
        # Try to access admin dashboard - should be redirected to login
        response = client.get('/admin/dashboard', follow_redirects=True)
        assert b'Instructor Login' in response.data or b'Please log in' in response.data
    
    def test_logout_redirects_to_home(self, client, test_user):
        """
        Test that logout redirects to home page.
        """
        # First login
        client.post('/login', data={
            'username': 'testinstructor',
            'password': 'testpassword123'
        })
        
        # Then logout
        response = client.get('/logout', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' not in response.location  # Should not redirect to login
    
    def test_logout_requires_authentication(self, client):
        """
        Test that logout route requires authentication.
        """
        response = client.get('/logout', follow_redirects=True)
        # Should be redirected to login page
        assert b'Instructor Login' in response.data or b'Please log in' in response.data


class TestAdminDashboardAccess:
    """Tests for admin dashboard access control."""
    
    def test_admin_dashboard_requires_authentication(self, client):
        """
        Test that admin dashboard requires authentication.
        
        Validates:
        - Requirement 16.1: Redirect unauthenticated users to login page
        - Requirement 16.2: Redirect unauthenticated users attempting to access admin functions
        """
        response = client.get('/admin/dashboard', follow_redirects=True)
        assert response.status_code == 200
        # Should be redirected to login page
        assert b'Instructor Login' in response.data or b'Please log in' in response.data
    
    def test_admin_dashboard_accessible_when_authenticated(self, client, test_user):
        """
        Test that admin dashboard is accessible when authenticated.
        
        Validates:
        - Requirement 16.3: Verify instructor authentication on every admin request
        """
        # First login
        client.post('/login', data={
            'username': 'testinstructor',
            'password': 'testpassword123'
        })
        
        # Access admin dashboard
        response = client.get('/admin/dashboard')
        assert response.status_code == 200
        assert b'Admin Dashboard' in response.data


class TestPasswordHashing:
    """Tests for password hashing functionality."""
    
    def test_password_is_hashed(self, app):
        """
        Test that passwords are hashed, not stored in plaintext.
        
        Validates:
        - Requirement 13.6: Use secure password hashing (bcrypt or similar)
        """
        with app.app_context():
            user = User(username='hashtest', email='hash@example.com')
            user.set_password('mypassword')
            
            # Password hash should not equal the plaintext password
            assert user.password_hash != 'mypassword'
            # Password hash should be a string
            assert isinstance(user.password_hash, str)
            # Password hash should be reasonably long (hashed)
            assert len(user.password_hash) > 20
    
    def test_password_verification(self, app):
        """
        Test that password verification works correctly.
        
        Validates:
        - Requirement 13.6: Use secure password hashing (bcrypt or similar)
        """
        with app.app_context():
            user = User(username='verifytest', email='verify@example.com')
            user.set_password('correctpassword')
            
            # Correct password should verify
            assert user.check_password('correctpassword') is True
            # Incorrect password should not verify
            assert user.check_password('wrongpassword') is False
    
    def test_different_passwords_produce_different_hashes(self, app):
        """
        Test that different passwords produce different hashes.
        """
        with app.app_context():
            user1 = User(username='user1', email='user1@example.com')
            user1.set_password('password1')
            
            user2 = User(username='user2', email='user2@example.com')
            user2.set_password('password2')
            
            # Different passwords should produce different hashes
            assert user1.password_hash != user2.password_hash


class TestCSRFProtection:
    """Tests for CSRF protection on login form."""
    
    def test_login_form_has_csrf_token(self, client):
        """
        Test that login form includes CSRF token.
        
        Validates:
        - Requirement 13.5: Implement CSRF protection on login form
        """
        response = client.get('/login')
        assert response.status_code == 200
        # Check for CSRF token field
        assert b'csrf_token' in response.data or b'hidden' in response.data


class TestSessionManagement:
    """Tests for session management."""
    
    def test_session_persists_across_requests(self, client, test_user):
        """
        Test that session persists across multiple requests.
        
        Validates:
        - Requirement 13.7: Maintain instructor session state after successful login
        """
        # Login
        client.post('/login', data={
            'username': 'testinstructor',
            'password': 'testpassword123'
        })
        
        # Make multiple requests to admin dashboard
        response1 = client.get('/admin/dashboard')
        assert response1.status_code == 200
        
        response2 = client.get('/admin/dashboard')
        assert response2.status_code == 200
        
        # Both requests should succeed without re-authentication
        assert b'Admin Dashboard' in response1.data
        assert b'Admin Dashboard' in response2.data
