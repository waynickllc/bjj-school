"""
Tests for admin user initialization script.

This module tests the init_admin.py script functionality including
user creation, validation, and error handling.
"""

import pytest
from app import create_app, db
from app.models import User, InstructorProfile
from init_admin import (
    validate_email,
    validate_password,
    create_admin_user
)


@pytest.fixture
def app():
    """Create application for testing."""
    from flask import Flask
    
    # Create app directly without loading config
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['WTF_CSRF_ENABLED'] = False
    
    # Initialize extensions with test app
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


class TestEmailValidation:
    """Test email validation function."""
    
    def test_valid_emails(self):
        """Test that valid email formats are accepted."""
        valid_emails = [
            'user@example.com',
            'test.user@example.com',
            'user+tag@example.co.uk',
            'user123@test-domain.com',
            'first.last@subdomain.example.com'
        ]
        
        for email in valid_emails:
            assert validate_email(email), f"Should accept valid email: {email}"
    
    def test_invalid_emails(self):
        """Test that invalid email formats are rejected."""
        invalid_emails = [
            'notanemail',
            '@example.com',
            'user@',
            'user @example.com',
            'user@.com',
            'user@domain',
            ''
        ]
        
        for email in invalid_emails:
            assert not validate_email(email), f"Should reject invalid email: {email}"


class TestPasswordValidation:
    """Test password validation function."""
    
    def test_valid_passwords(self):
        """Test that valid passwords are accepted."""
        valid_passwords = [
            'password123',
            'MySecurePass1',
            'a1b2c3d4e5f6',
            '12345678',
            'LongPasswordWithManyCharacters123'
        ]
        
        for password in valid_passwords:
            is_valid, error = validate_password(password)
            assert is_valid, f"Should accept valid password: {password}"
            assert error == ""
    
    def test_short_passwords(self):
        """Test that passwords shorter than 8 characters are rejected."""
        short_passwords = [
            'pass',
            '1234567',
            'abc',
            ''
        ]
        
        for password in short_passwords:
            is_valid, error = validate_password(password)
            assert not is_valid, f"Should reject short password: {password}"
            assert "at least 8 characters" in error


class TestCreateAdminUser:
    """Test admin user creation function."""
    
    def test_create_basic_user(self, app):
        """Test creating a basic admin user with default profile."""
        with app.app_context():
            success, message = create_admin_user(
                username='testadmin',
                email='test@example.com',
                password='testpass123'
            )
            
            assert success, f"User creation should succeed: {message}"
            assert "created successfully" in message
            
            # Verify user was created
            user = User.query.filter_by(username='testadmin').first()
            assert user is not None
            assert user.email == 'test@example.com'
            assert user.check_password('testpass123')
            
            # Verify profile was created with defaults
            profile = InstructorProfile.query.filter_by(user_id=user.id).first()
            assert profile is not None
            assert profile.title == 'Instructor'
            assert len(profile.biography) > 0
            assert profile.is_head_instructor is False
    
    def test_create_user_with_custom_profile(self, app):
        """Test creating admin user with custom profile information."""
        with app.app_context():
            custom_bio = "Expert BJJ instructor with 15 years of experience."
            custom_title = "Head Professor"
            
            success, message = create_admin_user(
                username='professor',
                email='prof@example.com',
                password='profpass123',
                biography=custom_bio,
                title=custom_title,
                is_head_instructor=True
            )
            
            assert success
            
            # Verify custom profile data
            user = User.query.filter_by(username='professor').first()
            profile = InstructorProfile.query.filter_by(user_id=user.id).first()
            
            assert profile.biography == custom_bio
            assert profile.title == custom_title
            assert profile.is_head_instructor is True
    
    def test_duplicate_username(self, app):
        """Test that duplicate usernames are rejected."""
        with app.app_context():
            # Create first user
            success1, _ = create_admin_user(
                username='duplicate',
                email='user1@example.com',
                password='password123'
            )
            assert success1
            
            # Try to create second user with same username
            success2, message2 = create_admin_user(
                username='duplicate',
                email='user2@example.com',
                password='password456'
            )
            
            assert not success2
            assert "already exists" in message2.lower()
    
    def test_duplicate_email(self, app):
        """Test that duplicate emails are rejected."""
        with app.app_context():
            # Create first user
            success1, _ = create_admin_user(
                username='user1',
                email='duplicate@example.com',
                password='password123'
            )
            assert success1
            
            # Try to create second user with same email
            success2, message2 = create_admin_user(
                username='user2',
                email='duplicate@example.com',
                password='password456'
            )
            
            assert not success2
            assert "already registered" in message2.lower()
    
    def test_head_instructor_uniqueness(self, app):
        """Test that only one head instructor can exist at a time."""
        with app.app_context():
            # Create first head instructor
            success1, _ = create_admin_user(
                username='head1',
                email='head1@example.com',
                password='password123',
                is_head_instructor=True
            )
            assert success1
            
            # Verify first is head instructor
            user1 = User.query.filter_by(username='head1').first()
            profile1 = InstructorProfile.query.filter_by(user_id=user1.id).first()
            assert profile1.is_head_instructor is True
            
            # Create second head instructor
            success2, _ = create_admin_user(
                username='head2',
                email='head2@example.com',
                password='password456',
                is_head_instructor=True
            )
            assert success2
            
            # Verify first is no longer head instructor
            db.session.refresh(profile1)
            assert profile1.is_head_instructor is False
            
            # Verify second is now head instructor
            user2 = User.query.filter_by(username='head2').first()
            profile2 = InstructorProfile.query.filter_by(user_id=user2.id).first()
            assert profile2.is_head_instructor is True
    
    def test_password_hashing(self, app):
        """Test that passwords are properly hashed."""
        with app.app_context():
            password = 'mysecretpassword'
            
            success, _ = create_admin_user(
                username='hashtest',
                email='hash@example.com',
                password=password
            )
            assert success
            
            user = User.query.filter_by(username='hashtest').first()
            
            # Password should not be stored in plain text
            assert user.password_hash != password
            
            # But should verify correctly
            assert user.check_password(password)
            
            # Wrong password should not verify
            assert not user.check_password('wrongpassword')
    
    def test_user_profile_relationship(self, app):
        """Test that user and profile are properly linked."""
        with app.app_context():
            success, _ = create_admin_user(
                username='reltest',
                email='rel@example.com',
                password='password123'
            )
            assert success
            
            user = User.query.filter_by(username='reltest').first()
            
            # Access profile through relationship
            assert user.instructor_profile is not None
            assert user.instructor_profile.user_id == user.id
            
            # Access user through profile relationship
            profile = user.instructor_profile
            assert profile.user.username == 'reltest'
