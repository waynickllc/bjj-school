"""
Tests for Admin Announcement Management Routes

This module tests the admin announcement management functionality including:
- Listing announcements
- Creating new announcements
- Editing existing announcements
- Deleting announcements
- CSRF protection
- Authentication requirements
"""

import unittest
from datetime import datetime
from flask import Flask
from app import db
from app.models import Announcement, User
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
import os


class TestAdminAnnouncementManagement(unittest.TestCase):
    """Test cases for admin announcement management routes"""
    
    def setUp(self):
        """Set up test client and app context"""
        # Create app
        root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.app = Flask(__name__, 
                        template_folder=os.path.join(root_path, 'app', 'templates'),
                        static_folder=os.path.join(root_path, 'app', 'static'),
                        root_path=root_path)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        self.app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        
        # Initialize extensions
        db.init_app(self.app)
        csrf = CSRFProtect(self.app)
        login_manager = LoginManager(self.app)
        login_manager.login_view = 'auth.login'
        
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))
        
        # Register all blueprints
        from app.routes.main import main_bp
        from app.routes.contact import contact_bp
        from app.routes.booking import booking_bp
        from app.routes.auth import auth_bp
        from app.routes.admin import admin_bp
        
        self.app.register_blueprint(main_bp)
        self.app.register_blueprint(contact_bp)
        self.app.register_blueprint(booking_bp)
        self.app.register_blueprint(auth_bp)
        self.app.register_blueprint(admin_bp)
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        
        # Create all database tables
        db.create_all()
        
        # Create test admin user
        self.admin_user = User(username='testadmin', email='admin@test.com')
        self.admin_user.set_password('testpass123')
        db.session.add(self.admin_user)
        db.session.commit()
    
    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def login(self):
        """Helper method to log in as admin"""
        return self.client.post('/login', data={
            'username': 'testadmin',
            'password': 'testpass123'
        }, follow_redirects=True)
    
    # ========================================================================
    # Authentication Tests
    # ========================================================================
    
    def test_list_announcements_requires_login(self):
        """Test that listing announcements requires authentication"""
        response = self.client.get('/admin/announcements')
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn('/login', response.location)
    
    def test_create_announcement_requires_login(self):
        """Test that creating an announcement requires authentication"""
        response = self.client.get('/admin/announcements/create')
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn('/login', response.location)
    
    def test_edit_announcement_requires_login(self):
        """Test that editing an announcement requires authentication"""
        # Create a test announcement
        test_announcement = Announcement(
            title='Test Announcement',
            content='This is a test announcement.'
        )
        db.session.add(test_announcement)
        db.session.commit()
        
        response = self.client.get(f'/admin/announcements/{test_announcement.id}/edit')
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn('/login', response.location)
    
    def test_delete_announcement_requires_login(self):
        """Test that deleting an announcement requires authentication"""
        # Create a test announcement
        test_announcement = Announcement(
            title='Test Announcement',
            content='This is a test announcement.'
        )
        db.session.add(test_announcement)
        db.session.commit()
        
        response = self.client.post(f'/admin/announcements/{test_announcement.id}/delete')
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn('/login', response.location)
    
    # ========================================================================
    # List Announcements Tests
    # ========================================================================
    
    def test_list_announcements_empty(self):
        """Test listing announcements when no announcements exist"""
        self.login()
        
        response = self.client.get('/admin/announcements')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No announcements have been created yet', response.data)
    
    def test_list_announcements_with_data(self):
        """Test listing announcements when announcements exist"""
        self.login()
        
        # Create test announcements
        announcement1 = Announcement(
            title='Welcome to Our School',
            content='We are excited to have you join us!'
        )
        announcement2 = Announcement(
            title='New Schedule',
            content='Check out our updated class schedule.'
        )
        db.session.add(announcement1)
        db.session.add(announcement2)
        db.session.commit()
        
        response = self.client.get('/admin/announcements')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to Our School', response.data)
        self.assertIn(b'New Schedule', response.data)
    
    def test_list_announcements_reverse_chronological(self):
        """Test that announcements are listed in reverse chronological order"""
        self.login()
        
        # Create test announcements with different timestamps
        announcement1 = Announcement(
            title='First Announcement',
            content='This was posted first.',
            published_date=datetime(2024, 1, 1, 10, 0, 0)
        )
        announcement2 = Announcement(
            title='Second Announcement',
            content='This was posted second.',
            published_date=datetime(2024, 1, 2, 10, 0, 0)
        )
        db.session.add(announcement1)
        db.session.add(announcement2)
        db.session.commit()
        
        response = self.client.get('/admin/announcements')
        self.assertEqual(response.status_code, 200)
        
        # Check that second announcement appears before first in the HTML
        data = response.data.decode('utf-8')
        second_pos = data.find('Second Announcement')
        first_pos = data.find('First Announcement')
        self.assertLess(second_pos, first_pos)
    
    # ========================================================================
    # Create Announcement Tests
    # ========================================================================
    
    def test_create_announcement_get(self):
        """Test GET request to create announcement form"""
        self.login()
        
        response = self.client.get('/admin/announcements/create')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Create Announcement', response.data)
        self.assertIn(b'Title', response.data)
        self.assertIn(b'Content', response.data)
    
    def test_create_announcement_post_valid(self):
        """Test POST request to create a new announcement with valid data"""
        self.login()
        
        response = self.client.post('/admin/announcements/create', data={
            'title': 'Important Update',
            'content': 'This is an important update for all students.'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'created successfully', response.data)
        
        # Check if announcement was created
        new_announcement = Announcement.query.filter_by(title='Important Update').first()
        self.assertIsNotNone(new_announcement)
        self.assertEqual(new_announcement.content, 'This is an important update for all students.')
        self.assertIsNotNone(new_announcement.published_date)
    
    def test_create_announcement_post_missing_title(self):
        """Test POST request with missing title"""
        self.login()
        
        response = self.client.post('/admin/announcements/create', data={
            'content': 'This announcement has no title.'
        })
        
        self.assertEqual(response.status_code, 200)
        # Should show validation error
        self.assertIn(b'Title is required', response.data)
    
    def test_create_announcement_post_missing_content(self):
        """Test POST request with missing content"""
        self.login()
        
        response = self.client.post('/admin/announcements/create', data={
            'title': 'Empty Announcement'
        })
        
        self.assertEqual(response.status_code, 200)
        # Should show validation error
        self.assertIn(b'Content is required', response.data)
    
    def test_create_announcement_sets_timestamp(self):
        """Test that creating an announcement sets the published_date automatically"""
        self.login()
        
        before = datetime.utcnow()
        response = self.client.post('/admin/announcements/create', data={
            'title': 'Timestamped Announcement',
            'content': 'This should have a timestamp.'
        }, follow_redirects=True)
        after = datetime.utcnow()
        
        self.assertEqual(response.status_code, 200)
        
        # Check if announcement has timestamp
        announcement = Announcement.query.filter_by(title='Timestamped Announcement').first()
        self.assertIsNotNone(announcement.published_date)
        self.assertGreaterEqual(announcement.published_date, before)
        self.assertLessEqual(announcement.published_date, after)
    
    # ========================================================================
    # Edit Announcement Tests
    # ========================================================================
    
    def test_edit_announcement_get(self):
        """Test GET request to edit announcement form"""
        self.login()
        
        # Create test announcement
        test_announcement = Announcement(
            title='Original Title',
            content='Original content.'
        )
        db.session.add(test_announcement)
        db.session.commit()
        
        response = self.client.get(f'/admin/announcements/{test_announcement.id}/edit')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Edit Announcement', response.data)
        self.assertIn(b'Original Title', response.data)
    
    def test_edit_announcement_post_valid(self):
        """Test POST request to edit an announcement with valid data"""
        self.login()
        
        # Create test announcement
        test_announcement = Announcement(
            title='Original Title',
            content='Original content.'
        )
        db.session.add(test_announcement)
        db.session.commit()
        announcement_id = test_announcement.id
        
        response = self.client.post(f'/admin/announcements/{announcement_id}/edit', data={
            'title': 'Updated Title',
            'content': 'Updated content.'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'updated successfully', response.data)
        
        # Check if announcement was updated
        updated_announcement = Announcement.query.get(announcement_id)
        self.assertEqual(updated_announcement.title, 'Updated Title')
        self.assertEqual(updated_announcement.content, 'Updated content.')
    
    def test_edit_announcement_not_found(self):
        """Test editing a non-existent announcement"""
        self.login()
        
        response = self.client.get('/admin/announcements/99999/edit')
        self.assertEqual(response.status_code, 404)
    
    # ========================================================================
    # Delete Announcement Tests
    # ========================================================================
    
    def test_delete_announcement_post(self):
        """Test POST request to delete an announcement"""
        self.login()
        
        # Create test announcement
        test_announcement = Announcement(
            title='To Be Deleted',
            content='This announcement will be deleted.'
        )
        db.session.add(test_announcement)
        db.session.commit()
        announcement_id = test_announcement.id
        
        response = self.client.post(f'/admin/announcements/{announcement_id}/delete', follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'deleted successfully', response.data)
        
        # Check if announcement was deleted
        deleted_announcement = Announcement.query.get(announcement_id)
        self.assertIsNone(deleted_announcement)
    
    def test_delete_announcement_not_found(self):
        """Test deleting a non-existent announcement"""
        self.login()
        
        response = self.client.post('/admin/announcements/99999/delete')
        self.assertEqual(response.status_code, 404)
    
    def test_delete_announcement_get_not_allowed(self):
        """Test that GET request to delete is not allowed"""
        self.login()
        
        # Create test announcement
        test_announcement = Announcement(
            title='Test Announcement',
            content='This is a test.'
        )
        db.session.add(test_announcement)
        db.session.commit()
        
        response = self.client.get(f'/admin/announcements/{test_announcement.id}/delete')
        self.assertEqual(response.status_code, 405)  # Method Not Allowed


if __name__ == '__main__':
    unittest.main()
