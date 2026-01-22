"""
Tests for Admin FAQ Management Routes

This module tests the admin FAQ management functionality including:
- Listing FAQs
- Creating new FAQs
- Editing existing FAQs
- Deleting FAQs
- Reordering FAQs
- CSRF protection
- Authentication requirements
"""

import unittest
from datetime import datetime
from flask import Flask
from app import db
from app.models import FAQ, User
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
import os


class TestAdminFAQManagement(unittest.TestCase):
    """Test cases for admin FAQ management routes"""
    
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
    
    def test_list_faqs_requires_login(self):
        """Test that listing FAQs requires authentication"""
        response = self.client.get('/admin/faqs')
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn('/login', response.location)
    
    def test_create_faq_requires_login(self):
        """Test that creating an FAQ requires authentication"""
        response = self.client.get('/admin/faqs/create')
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn('/login', response.location)
    
    def test_edit_faq_requires_login(self):
        """Test that editing an FAQ requires authentication"""
        # Create a test FAQ
        test_faq = FAQ(
            question='Test Question?',
            answer='This is a test answer.',
            display_order=1
        )
        db.session.add(test_faq)
        db.session.commit()
        
        response = self.client.get(f'/admin/faqs/{test_faq.id}/edit')
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn('/login', response.location)
    
    def test_delete_faq_requires_login(self):
        """Test that deleting an FAQ requires authentication"""
        # Create a test FAQ
        test_faq = FAQ(
            question='Test Question?',
            answer='This is a test answer.',
            display_order=1
        )
        db.session.add(test_faq)
        db.session.commit()
        
        response = self.client.post(f'/admin/faqs/{test_faq.id}/delete')
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn('/login', response.location)
    
    # ========================================================================
    # List FAQs Tests
    # ========================================================================
    
    def test_list_faqs_empty(self):
        """Test listing FAQs when no FAQs exist"""
        self.login()
        
        response = self.client.get('/admin/faqs')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No FAQs have been created yet', response.data)
    
    def test_list_faqs_with_data(self):
        """Test listing FAQs when FAQs exist"""
        self.login()
        
        # Create test FAQs
        faq1 = FAQ(
            question='What is BJJ?',
            answer='Brazilian Jiu-Jitsu is a martial art.',
            display_order=1
        )
        faq2 = FAQ(
            question='How long are classes?',
            answer='Classes are typically 90 minutes.',
            display_order=2
        )
        db.session.add(faq1)
        db.session.add(faq2)
        db.session.commit()
        
        response = self.client.get('/admin/faqs')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'What is BJJ?', response.data)
        self.assertIn(b'How long are classes?', response.data)
    
    def test_list_faqs_ordered_by_display_order(self):
        """Test that FAQs are listed ordered by display_order"""
        self.login()
        
        # Create test FAQs with different display_order
        faq1 = FAQ(
            question='Third Question?',
            answer='Third answer.',
            display_order=3
        )
        faq2 = FAQ(
            question='First Question?',
            answer='First answer.',
            display_order=1
        )
        faq3 = FAQ(
            question='Second Question?',
            answer='Second answer.',
            display_order=2
        )
        db.session.add(faq1)
        db.session.add(faq2)
        db.session.add(faq3)
        db.session.commit()
        
        response = self.client.get('/admin/faqs')
        self.assertEqual(response.status_code, 200)
        
        # Check that FAQs appear in correct order in the HTML
        data = response.data.decode('utf-8')
        first_pos = data.find('First Question?')
        second_pos = data.find('Second Question?')
        third_pos = data.find('Third Question?')
        self.assertLess(first_pos, second_pos)
        self.assertLess(second_pos, third_pos)
    
    # ========================================================================
    # Create FAQ Tests
    # ========================================================================
    
    def test_create_faq_get(self):
        """Test GET request to create FAQ form"""
        self.login()
        
        response = self.client.get('/admin/faqs/create')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Create FAQ', response.data)
        self.assertIn(b'Question', response.data)
        self.assertIn(b'Answer', response.data)
    
    def test_create_faq_post_valid(self):
        """Test POST request to create a new FAQ with valid data"""
        self.login()
        
        response = self.client.post('/admin/faqs/create', data={
            'question': 'What should I wear?',
            'answer': 'Wear comfortable athletic clothing.',
            'display_order': 1
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'created successfully', response.data)
        
        # Check if FAQ was created
        new_faq = FAQ.query.filter_by(question='What should I wear?').first()
        self.assertIsNotNone(new_faq)
        self.assertEqual(new_faq.answer, 'Wear comfortable athletic clothing.')
        self.assertEqual(new_faq.display_order, 1)
    
    def test_create_faq_post_missing_question(self):
        """Test POST request with missing question"""
        self.login()
        
        response = self.client.post('/admin/faqs/create', data={
            'answer': 'This FAQ has no question.'
        })
        
        self.assertEqual(response.status_code, 200)
        # Should show validation error
        self.assertIn(b'Question is required', response.data)
    
    def test_create_faq_post_missing_answer(self):
        """Test POST request with missing answer"""
        self.login()
        
        response = self.client.post('/admin/faqs/create', data={
            'question': 'Empty FAQ?'
        })
        
        self.assertEqual(response.status_code, 200)
        # Should show validation error
        self.assertIn(b'Answer is required', response.data)
    
    def test_create_faq_default_display_order(self):
        """Test that creating an FAQ without display_order uses default value"""
        self.login()
        
        response = self.client.post('/admin/faqs/create', data={
            'question': 'Test Question?',
            'answer': 'Test answer.',
            'display_order': ''
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Check if FAQ has default display_order
        faq = FAQ.query.filter_by(question='Test Question?').first()
        self.assertIsNotNone(faq)
        self.assertEqual(faq.display_order, 0)
    
    # ========================================================================
    # Edit FAQ Tests
    # ========================================================================
    
    def test_edit_faq_get(self):
        """Test GET request to edit FAQ form"""
        self.login()
        
        # Create test FAQ
        test_faq = FAQ(
            question='Original Question?',
            answer='Original answer.',
            display_order=1
        )
        db.session.add(test_faq)
        db.session.commit()
        
        response = self.client.get(f'/admin/faqs/{test_faq.id}/edit')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Edit FAQ', response.data)
        self.assertIn(b'Original Question?', response.data)
    
    def test_edit_faq_post_valid(self):
        """Test POST request to edit an FAQ with valid data"""
        self.login()
        
        # Create test FAQ
        test_faq = FAQ(
            question='Original Question?',
            answer='Original answer.',
            display_order=1
        )
        db.session.add(test_faq)
        db.session.commit()
        faq_id = test_faq.id
        
        response = self.client.post(f'/admin/faqs/{faq_id}/edit', data={
            'question': 'Updated Question?',
            'answer': 'Updated answer.',
            'display_order': 2
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'updated successfully', response.data)
        
        # Check if FAQ was updated
        updated_faq = FAQ.query.get(faq_id)
        self.assertEqual(updated_faq.question, 'Updated Question?')
        self.assertEqual(updated_faq.answer, 'Updated answer.')
        self.assertEqual(updated_faq.display_order, 2)
    
    def test_edit_faq_not_found(self):
        """Test editing a non-existent FAQ"""
        self.login()
        
        response = self.client.get('/admin/faqs/99999/edit')
        self.assertEqual(response.status_code, 404)
    
    # ========================================================================
    # Delete FAQ Tests
    # ========================================================================
    
    def test_delete_faq_post(self):
        """Test POST request to delete an FAQ"""
        self.login()
        
        # Create test FAQ
        test_faq = FAQ(
            question='To Be Deleted?',
            answer='This FAQ will be deleted.',
            display_order=1
        )
        db.session.add(test_faq)
        db.session.commit()
        faq_id = test_faq.id
        
        response = self.client.post(f'/admin/faqs/{faq_id}/delete', follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'deleted successfully', response.data)
        
        # Check if FAQ was deleted
        deleted_faq = FAQ.query.get(faq_id)
        self.assertIsNone(deleted_faq)
    
    def test_delete_faq_not_found(self):
        """Test deleting a non-existent FAQ"""
        self.login()
        
        response = self.client.post('/admin/faqs/99999/delete')
        self.assertEqual(response.status_code, 404)
    
    def test_delete_faq_get_not_allowed(self):
        """Test that GET request to delete is not allowed"""
        self.login()
        
        # Create test FAQ
        test_faq = FAQ(
            question='Test Question?',
            answer='This is a test.',
            display_order=1
        )
        db.session.add(test_faq)
        db.session.commit()
        
        response = self.client.get(f'/admin/faqs/{test_faq.id}/delete')
        self.assertEqual(response.status_code, 405)  # Method Not Allowed
    
    # ========================================================================
    # Reorder FAQs Tests
    # ========================================================================
    
    def test_reorder_faqs_post(self):
        """Test POST request to reorder FAQs"""
        self.login()
        
        # Create test FAQs
        faq1 = FAQ(question='Q1?', answer='A1', display_order=1)
        faq2 = FAQ(question='Q2?', answer='A2', display_order=2)
        faq3 = FAQ(question='Q3?', answer='A3', display_order=3)
        db.session.add_all([faq1, faq2, faq3])
        db.session.commit()
        
        # Reorder: 3, 1, 2
        new_order = [faq3.id, faq1.id, faq2.id]
        
        response = self.client.post('/admin/faqs/reorder',
                                   json={'faq_ids': new_order},
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        
        # Verify display_order was updated
        faq1_updated = FAQ.query.get(faq1.id)
        faq2_updated = FAQ.query.get(faq2.id)
        faq3_updated = FAQ.query.get(faq3.id)
        
        self.assertEqual(faq3_updated.display_order, 0)
        self.assertEqual(faq1_updated.display_order, 1)
        self.assertEqual(faq2_updated.display_order, 2)
    
    def test_reorder_faqs_empty_list(self):
        """Test reordering with empty list returns error"""
        self.login()
        
        response = self.client.post('/admin/faqs/reorder',
                                   json={'faq_ids': []},
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data['success'])


if __name__ == '__main__':
    unittest.main()
