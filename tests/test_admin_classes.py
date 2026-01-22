"""
Tests for Admin Class Management Routes

This module tests the admin class management functionality including:
- Listing classes
- Creating new classes
- Editing existing classes
- Deleting classes
- CSRF protection
- Authentication requirements
"""

import unittest
from datetime import time
from flask import Flask
from app import db
from app.models import Class, User
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
import os


class TestAdminClassManagement(unittest.TestCase):
    """Test cases for admin class management routes"""
    
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
    
    def test_list_classes_requires_login(self):
        """Test that listing classes requires authentication"""
        response = self.client.get('/admin/classes')
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn('/login', response.location)
    
    def test_create_class_requires_login(self):
        """Test that creating a class requires authentication"""
        response = self.client.get('/admin/classes/create')
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn('/login', response.location)
    
    def test_edit_class_requires_login(self):
        """Test that editing a class requires authentication"""
        # Create a test class
        test_class = Class(
            name='Test Class',
            day_of_week='Monday',
            start_time=time(18, 0),
            end_time=time(19, 0)
        )
        db.session.add(test_class)
        db.session.commit()
        
        response = self.client.get(f'/admin/classes/{test_class.id}/edit')
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn('/login', response.location)
    
    def test_delete_class_requires_login(self):
        """Test that deleting a class requires authentication"""
        # Create a test class
        test_class = Class(
            name='Test Class',
            day_of_week='Monday',
            start_time=time(18, 0),
            end_time=time(19, 0)
        )
        db.session.add(test_class)
        db.session.commit()
        
        response = self.client.post(f'/admin/classes/{test_class.id}/delete')
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn('/login', response.location)
    
    # ========================================================================
    # List Classes Tests
    # ========================================================================
    
    def test_list_classes_empty(self):
        """Test listing classes when no classes exist"""
        self.login()
        
        response = self.client.get('/admin/classes')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No classes have been created yet', response.data)
    
    def test_list_classes_with_data(self):
        """Test listing classes when classes exist"""
        self.login()
        
        # Create test classes
        class1 = Class(
            name='Fundamentals',
            day_of_week='Monday',
            start_time=time(18, 0),
            end_time=time(19, 30)
        )
        class2 = Class(
            name='Advanced',
            day_of_week='Wednesday',
            start_time=time(19, 0),
            end_time=time(20, 30)
        )
        db.session.add(class1)
        db.session.add(class2)
        db.session.commit()
        
        response = self.client.get('/admin/classes')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Fundamentals', response.data)
        self.assertIn(b'Advanced', response.data)
        self.assertIn(b'Monday', response.data)
        self.assertIn(b'Wednesday', response.data)
    
    # ========================================================================
    # Create Class Tests
    # ========================================================================
    
    def test_create_class_get(self):
        """Test GET request to create class form"""
        self.login()
        
        response = self.client.get('/admin/classes/create')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Create Class', response.data)
        self.assertIn(b'Class Name', response.data)
        self.assertIn(b'Day of Week', response.data)
    
    def test_create_class_post_valid(self):
        """Test POST request to create a new class with valid data"""
        self.login()
        
        response = self.client.post('/admin/classes/create', data={
            'name': 'Advanced Training',
            'day_of_week': 'Tuesday',
            'start_time': '19:00',
            'end_time': '20:30'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'created successfully', response.data)
        
        # Check if class was created
        new_class = Class.query.filter_by(name='Advanced Training').first()
        self.assertIsNotNone(new_class)
        self.assertEqual(new_class.day_of_week, 'Tuesday')
        self.assertEqual(new_class.start_time, time(19, 0))
        self.assertEqual(new_class.end_time, time(20, 30))
    
    def test_create_class_post_missing_name(self):
        """Test POST request with missing class name"""
        self.login()
        
        response = self.client.post('/admin/classes/create', data={
            'day_of_week': 'Wednesday',
            'start_time': '18:00',
            'end_time': '19:00'
        })
        
        self.assertEqual(response.status_code, 200)
        # Should show validation error
        self.assertIn(b'Class name is required', response.data)
    
    # ========================================================================
    # Edit Class Tests
    # ========================================================================
    
    def test_edit_class_get(self):
        """Test GET request to edit class form"""
        self.login()
        
        # Create test class
        test_class = Class(
            name='Fundamentals',
            day_of_week='Monday',
            start_time=time(18, 0),
            end_time=time(19, 30)
        )
        db.session.add(test_class)
        db.session.commit()
        
        response = self.client.get(f'/admin/classes/{test_class.id}/edit')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Edit Class', response.data)
        self.assertIn(b'Fundamentals', response.data)
    
    def test_edit_class_post_valid(self):
        """Test POST request to edit a class with valid data"""
        self.login()
        
        # Create test class
        test_class = Class(
            name='Fundamentals',
            day_of_week='Monday',
            start_time=time(18, 0),
            end_time=time(19, 30)
        )
        db.session.add(test_class)
        db.session.commit()
        class_id = test_class.id
        
        response = self.client.post(f'/admin/classes/{class_id}/edit', data={
            'name': 'Updated Fundamentals',
            'day_of_week': 'Tuesday',
            'start_time': '19:00',
            'end_time': '20:30'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'updated successfully', response.data)
        
        # Check if class was updated
        updated_class = Class.query.get(class_id)
        self.assertEqual(updated_class.name, 'Updated Fundamentals')
        self.assertEqual(updated_class.day_of_week, 'Tuesday')
    
    def test_edit_class_not_found(self):
        """Test editing a non-existent class"""
        self.login()
        
        response = self.client.get('/admin/classes/99999/edit')
        self.assertEqual(response.status_code, 404)
    
    # ========================================================================
    # Delete Class Tests
    # ========================================================================
    
    def test_delete_class_post(self):
        """Test POST request to delete a class"""
        self.login()
        
        # Create test class
        test_class = Class(
            name='Test Class',
            day_of_week='Monday',
            start_time=time(18, 0),
            end_time=time(19, 0)
        )
        db.session.add(test_class)
        db.session.commit()
        class_id = test_class.id
        
        response = self.client.post(f'/admin/classes/{class_id}/delete', follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'deleted successfully', response.data)
        
        # Check if class was deleted
        deleted_class = Class.query.get(class_id)
        self.assertIsNone(deleted_class)
    
    def test_delete_class_not_found(self):
        """Test deleting a non-existent class"""
        self.login()
        
        response = self.client.post('/admin/classes/99999/delete')
        self.assertEqual(response.status_code, 404)
    
    def test_delete_class_get_not_allowed(self):
        """Test that GET request to delete is not allowed"""
        self.login()
        
        # Create test class
        test_class = Class(
            name='Test Class',
            day_of_week='Monday',
            start_time=time(18, 0),
            end_time=time(19, 0)
        )
        db.session.add(test_class)
        db.session.commit()
        
        response = self.client.get(f'/admin/classes/{test_class.id}/delete')
        self.assertEqual(response.status_code, 405)  # Method Not Allowed


if __name__ == '__main__':
    unittest.main()
