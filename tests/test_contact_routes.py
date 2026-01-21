"""
Unit tests for contact routes

Tests the contact form GET and POST handlers.
"""

import unittest
from flask import Flask
from app import db
from app.models import ContactSubmission
from app.routes.contact import contact_bp
from flask_wtf.csrf import CSRFProtect


class TestContactRoutes(unittest.TestCase):
    """Test cases for contact routes"""
    
    def setUp(self):
        """Set up test client and app context"""
        # Create app without loading config first
        # Need to specify template_folder and root_path for Flask to find templates
        import os
        root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.app = Flask(__name__, 
                        template_folder=os.path.join(root_path, 'app', 'templates'),
                        root_path=root_path)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        self.app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        
        # Initialize extensions with test app
        db.init_app(self.app)
        csrf = CSRFProtect(self.app)
        
        # Register all blueprints (needed for base.html navigation)
        from app.routes.main import main_bp
        from app.routes.booking import booking_bp
        self.app.register_blueprint(main_bp)
        self.app.register_blueprint(contact_bp)
        self.app.register_blueprint(booking_bp)
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        
        # Create all database tables
        db.create_all()
    
    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_contact_get_displays_form(self):
        """Test GET /contact displays the contact form"""
        response = self.client.get('/contact')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Contact Us', response.data)
        self.assertIn(b'name', response.data.lower())
        self.assertIn(b'email', response.data.lower())
        self.assertIn(b'message', response.data.lower())
    
    def test_contact_post_valid_submission(self):
        """Test POST /contact with valid data saves to database and shows confirmation"""
        form_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '+1234567890',
            'message': 'This is a test message with enough characters.'
        }
        
        response = self.client.post('/contact', data=form_data, follow_redirects=True)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Thank you for your message', response.data)
        
        # Check database
        submission = ContactSubmission.query.first()
        self.assertIsNotNone(submission)
        self.assertEqual(submission.name, 'John Doe')
        self.assertEqual(submission.email, 'john@example.com')
        self.assertEqual(submission.phone, '+1234567890')
        self.assertEqual(submission.message, 'This is a test message with enough characters.')
        self.assertIsNotNone(submission.submitted_at)
    
    def test_contact_post_valid_without_phone(self):
        """Test POST /contact with valid data but no phone (optional field)"""
        form_data = {
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'phone': '',
            'message': 'This is another test message.'
        }
        
        response = self.client.post('/contact', data=form_data, follow_redirects=True)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Thank you for your message', response.data)
        
        # Check database
        submission = ContactSubmission.query.first()
        self.assertIsNotNone(submission)
        self.assertEqual(submission.name, 'Jane Smith')
        self.assertEqual(submission.email, 'jane@example.com')
        self.assertIsNone(submission.phone)
        self.assertEqual(submission.message, 'This is another test message.')
    
    def test_contact_post_missing_name(self):
        """Test POST /contact with missing name shows validation error"""
        form_data = {
            'name': '',
            'email': 'john@example.com',
            'phone': '+1234567890',
            'message': 'This is a test message.'
        }
        
        response = self.client.post('/contact', data=form_data)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Name is required', response.data)
        
        # Check database - should be empty
        submission = ContactSubmission.query.first()
        self.assertIsNone(submission)
    
    def test_contact_post_missing_email(self):
        """Test POST /contact with missing email shows validation error"""
        form_data = {
            'name': 'John Doe',
            'email': '',
            'phone': '+1234567890',
            'message': 'This is a test message.'
        }
        
        response = self.client.post('/contact', data=form_data)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Email is required', response.data)
        
        # Check database - should be empty
        submission = ContactSubmission.query.first()
        self.assertIsNone(submission)
    
    def test_contact_post_invalid_email(self):
        """Test POST /contact with invalid email shows validation error"""
        form_data = {
            'name': 'John Doe',
            'email': 'not-an-email',
            'phone': '+1234567890',
            'message': 'This is a test message.'
        }
        
        response = self.client.post('/contact', data=form_data)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid email format', response.data)
        
        # Check database - should be empty
        submission = ContactSubmission.query.first()
        self.assertIsNone(submission)
    
    def test_contact_post_missing_message(self):
        """Test POST /contact with missing message shows validation error"""
        form_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '+1234567890',
            'message': ''
        }
        
        response = self.client.post('/contact', data=form_data)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Message is required', response.data)
        
        # Check database - should be empty
        submission = ContactSubmission.query.first()
        self.assertIsNone(submission)
    
    def test_contact_post_message_too_short(self):
        """Test POST /contact with message too short shows validation error"""
        form_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '+1234567890',
            'message': 'Short'
        }
        
        response = self.client.post('/contact', data=form_data)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Message must be 10-1000 characters', response.data)
        
        # Check database - should be empty
        submission = ContactSubmission.query.first()
        self.assertIsNone(submission)
    
    def test_contact_post_sanitizes_html(self):
        """Test POST /contact sanitizes HTML in user input (Requirement 7.5)"""
        form_data = {
            'name': 'John <script>alert("xss")</script> Doe',
            'email': 'john@example.com',
            'phone': '+1234567890',
            'message': 'This is a test message with <b>HTML</b> tags.'
        }
        
        response = self.client.post('/contact', data=form_data, follow_redirects=True)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Thank you for your message', response.data)
        
        # Check database - HTML should be escaped
        submission = ContactSubmission.query.first()
        self.assertIsNotNone(submission)
        # markupsafe.escape converts < to &lt; and > to &gt;
        self.assertIn('&lt;script&gt;', submission.name)
        self.assertIn('&lt;b&gt;HTML&lt;/b&gt;', submission.message)
        # Should not contain raw HTML tags
        self.assertNotIn('<script>', submission.name)
        self.assertNotIn('<b>', submission.message)
    
    def test_contact_post_preserves_input_on_validation_error(self):
        """Test POST /contact preserves user input when validation fails (Requirement 8.5)"""
        form_data = {
            'name': 'John Doe',
            'email': 'not-an-email',  # Invalid email
            'phone': '+1234567890',
            'message': 'This is a test message.'
        }
        
        response = self.client.post('/contact', data=form_data)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid email format', response.data)
        # Check that valid fields are preserved
        self.assertIn(b'John Doe', response.data)
        self.assertIn(b'+1234567890', response.data)
        self.assertIn(b'This is a test message.', response.data)
    
    def test_contact_post_invalid_phone_format(self):
        """Test POST /contact with invalid phone format shows validation error"""
        form_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': 'abc123',  # Invalid phone
            'message': 'This is a test message.'
        }
        
        response = self.client.post('/contact', data=form_data)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid phone format', response.data)
        
        # Check database - should be empty
        submission = ContactSubmission.query.first()
        self.assertIsNone(submission)


if __name__ == '__main__':
    unittest.main()
