"""
Unit tests for booking routes

Tests the trial booking form GET and POST handlers.
Validates Requirements 3.2, 3.3, 3.4, 3.6, 3.8, 7.5
"""

import unittest
from datetime import date, datetime, timedelta
from flask import Flask
from app import db
from app.models import TrialBooking
from app.routes.booking import booking_bp
from flask_wtf.csrf import CSRFProtect


class TestBookingRoutes(unittest.TestCase):
    """Test cases for booking routes"""
    
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
        from app.routes.contact import contact_bp
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
    
    def test_booking_get_displays_form(self):
        """Test GET /booking displays the trial booking form"""
        response = self.client.get('/booking')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Book a Trial Class', response.data)
        self.assertIn(b'name', response.data.lower())
        self.assertIn(b'email', response.data.lower())
        self.assertIn(b'phone', response.data.lower())
        self.assertIn(b'preferred_date', response.data.lower())
        self.assertIn(b'preferred_time', response.data.lower())
    
    def test_booking_post_valid_submission(self):
        """Test POST /booking with valid data saves to database and shows confirmation (Requirements 3.3, 3.4)"""
        tomorrow = date.today() + timedelta(days=1)
        form_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '+1234567890',
            'preferred_date': tomorrow.isoformat(),
            'preferred_time': 'morning'
        }
        
        response = self.client.post('/booking', data=form_data, follow_redirects=True)
        
        # Check response - should show confirmation with booking details (Requirement 3.4)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your trial class has been booked', response.data)
        self.assertIn(b'john@example.com', response.data)
        self.assertIn(b'Morning', response.data)
        
        # Check database (Requirement 3.3)
        booking = TrialBooking.query.first()
        self.assertIsNotNone(booking)
        self.assertEqual(booking.name, 'John Doe')
        self.assertEqual(booking.email, 'john@example.com')
        self.assertEqual(booking.phone, '+1234567890')
        self.assertEqual(booking.preferred_date, tomorrow)
        self.assertEqual(booking.preferred_time, 'morning')
        self.assertIsNotNone(booking.submitted_at)
    
    def test_booking_post_missing_name(self):
        """Test POST /booking with missing name shows validation error (Requirement 3.6)"""
        tomorrow = date.today() + timedelta(days=1)
        form_data = {
            'name': '',
            'email': 'john@example.com',
            'phone': '+1234567890',
            'preferred_date': tomorrow.isoformat(),
            'preferred_time': 'morning'
        }
        
        response = self.client.post('/booking', data=form_data)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Name is required', response.data)
        
        # Check database - should be empty
        booking = TrialBooking.query.first()
        self.assertIsNone(booking)
    
    def test_booking_post_missing_email(self):
        """Test POST /booking with missing email shows validation error (Requirement 3.6)"""
        tomorrow = date.today() + timedelta(days=1)
        form_data = {
            'name': 'John Doe',
            'email': '',
            'phone': '+1234567890',
            'preferred_date': tomorrow.isoformat(),
            'preferred_time': 'morning'
        }
        
        response = self.client.post('/booking', data=form_data)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Email is required', response.data)
        
        # Check database - should be empty
        booking = TrialBooking.query.first()
        self.assertIsNone(booking)
    
    def test_booking_post_invalid_email(self):
        """Test POST /booking with invalid email shows validation error (Requirement 3.6)"""
        tomorrow = date.today() + timedelta(days=1)
        form_data = {
            'name': 'John Doe',
            'email': 'not-an-email',
            'phone': '+1234567890',
            'preferred_date': tomorrow.isoformat(),
            'preferred_time': 'morning'
        }
        
        response = self.client.post('/booking', data=form_data)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid email format', response.data)
        
        # Check database - should be empty
        booking = TrialBooking.query.first()
        self.assertIsNone(booking)
    
    def test_booking_post_missing_phone(self):
        """Test POST /booking with missing phone shows validation error (Requirement 3.6)"""
        tomorrow = date.today() + timedelta(days=1)
        form_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '',
            'preferred_date': tomorrow.isoformat(),
            'preferred_time': 'morning'
        }
        
        response = self.client.post('/booking', data=form_data)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Phone is required', response.data)
        
        # Check database - should be empty
        booking = TrialBooking.query.first()
        self.assertIsNone(booking)
    
    def test_booking_post_invalid_phone_format(self):
        """Test POST /booking with invalid phone format shows validation error (Requirement 3.6)"""
        tomorrow = date.today() + timedelta(days=1)
        form_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': 'abc123',  # Invalid phone
            'preferred_date': tomorrow.isoformat(),
            'preferred_time': 'morning'
        }
        
        response = self.client.post('/booking', data=form_data)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid phone format', response.data)
        
        # Check database - should be empty
        booking = TrialBooking.query.first()
        self.assertIsNone(booking)
    
    def test_booking_post_missing_date(self):
        """Test POST /booking with missing date shows validation error (Requirement 3.6)"""
        form_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '+1234567890',
            'preferred_date': '',
            'preferred_time': 'morning'
        }
        
        response = self.client.post('/booking', data=form_data)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Preferred date is required', response.data)
        
        # Check database - should be empty
        booking = TrialBooking.query.first()
        self.assertIsNone(booking)
    
    def test_booking_post_missing_time(self):
        """Test POST /booking with missing time shows validation error (Requirement 3.6)"""
        tomorrow = date.today() + timedelta(days=1)
        form_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '+1234567890',
            'preferred_date': tomorrow.isoformat(),
            'preferred_time': ''
        }
        
        response = self.client.post('/booking', data=form_data)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Preferred time is required', response.data)
        
        # Check database - should be empty
        booking = TrialBooking.query.first()
        self.assertIsNone(booking)
    
    def test_booking_post_duplicate_within_24_hours(self):
        """Test POST /booking prevents duplicate bookings within 24 hours (Requirement 3.8)"""
        tomorrow = date.today() + timedelta(days=1)
        
        # Create first booking
        first_booking = TrialBooking(
            name='John Doe',
            email='john@example.com',
            phone='+1234567890',
            preferred_date=tomorrow,
            preferred_time='morning',
            submitted_at=datetime.utcnow()
        )
        db.session.add(first_booking)
        db.session.commit()
        
        # Try to create second booking with same email
        form_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '+1234567890',
            'preferred_date': tomorrow.isoformat(),
            'preferred_time': 'afternoon'
        }
        
        response = self.client.post('/booking', data=form_data)
        
        # Check response - should show error message
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'already booked a trial class within the last 24 hours', response.data)
        
        # Check database - should only have one booking
        bookings = TrialBooking.query.all()
        self.assertEqual(len(bookings), 1)
    
    def test_booking_post_duplicate_after_24_hours_allowed(self):
        """Test POST /booking allows duplicate bookings after 24 hours (Requirement 3.8)"""
        tomorrow = date.today() + timedelta(days=1)
        
        # Create first booking 25 hours ago
        first_booking = TrialBooking(
            name='John Doe',
            email='john@example.com',
            phone='+1234567890',
            preferred_date=tomorrow,
            preferred_time='morning',
            submitted_at=datetime.utcnow() - timedelta(hours=25)
        )
        db.session.add(first_booking)
        db.session.commit()
        
        # Try to create second booking with same email
        form_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '+1234567890',
            'preferred_date': tomorrow.isoformat(),
            'preferred_time': 'afternoon'
        }
        
        response = self.client.post('/booking', data=form_data, follow_redirects=True)
        
        # Check response - should succeed
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your trial class has been booked', response.data)
        
        # Check database - should have two bookings
        bookings = TrialBooking.query.all()
        self.assertEqual(len(bookings), 2)
    
    def test_booking_post_duplicate_case_insensitive(self):
        """Test POST /booking duplicate check is case-insensitive (Requirement 3.8)"""
        tomorrow = date.today() + timedelta(days=1)
        
        # Create first booking with lowercase email
        first_booking = TrialBooking(
            name='John Doe',
            email='john@example.com',
            phone='+1234567890',
            preferred_date=tomorrow,
            preferred_time='morning',
            submitted_at=datetime.utcnow()
        )
        db.session.add(first_booking)
        db.session.commit()
        
        # Try to create second booking with uppercase email
        form_data = {
            'name': 'John Doe',
            'email': 'JOHN@EXAMPLE.COM',
            'phone': '+1234567890',
            'preferred_date': tomorrow.isoformat(),
            'preferred_time': 'afternoon'
        }
        
        response = self.client.post('/booking', data=form_data)
        
        # Check response - should show error message
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'already booked a trial class within the last 24 hours', response.data)
        
        # Check database - should only have one booking
        bookings = TrialBooking.query.all()
        self.assertEqual(len(bookings), 1)
    
    def test_booking_post_sanitizes_html(self):
        """Test POST /booking sanitizes HTML in user input (Requirement 7.5)"""
        tomorrow = date.today() + timedelta(days=1)
        form_data = {
            'name': 'John <script>alert("xss")</script> Doe',
            'email': 'john@example.com',
            'phone': '+1234567890',
            'preferred_date': tomorrow.isoformat(),
            'preferred_time': 'morning'
        }
        
        response = self.client.post('/booking', data=form_data, follow_redirects=True)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your trial class has been booked', response.data)
        
        # Check database - HTML should be escaped
        booking = TrialBooking.query.first()
        self.assertIsNotNone(booking)
        # markupsafe.escape converts < to &lt; and > to &gt;
        self.assertIn('&lt;script&gt;', booking.name)
        # Should not contain raw HTML tags
        self.assertNotIn('<script>', booking.name)
    
    def test_booking_post_preserves_input_on_validation_error(self):
        """Test POST /booking preserves user input when validation fails (Requirement 8.5)"""
        tomorrow = date.today() + timedelta(days=1)
        form_data = {
            'name': 'John Doe',
            'email': 'not-an-email',  # Invalid email
            'phone': '+1234567890',
            'preferred_date': tomorrow.isoformat(),
            'preferred_time': 'morning'
        }
        
        response = self.client.post('/booking', data=form_data)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid email format', response.data)
        # Check that valid fields are preserved
        self.assertIn(b'John Doe', response.data)
        self.assertIn(b'+1234567890', response.data)
    
    def test_booking_post_confirmation_includes_details(self):
        """Test POST /booking confirmation message includes booking details (Requirement 3.4)"""
        tomorrow = date.today() + timedelta(days=1)
        form_data = {
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'phone': '+9876543210',
            'preferred_date': tomorrow.isoformat(),
            'preferred_time': 'evening'
        }
        
        response = self.client.post('/booking', data=form_data, follow_redirects=True)
        
        # Check response includes booking details
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your trial class has been booked', response.data)
        self.assertIn(b'jane@example.com', response.data)
        self.assertIn(b'Evening', response.data)  # Time label should be displayed
        # Date should be formatted nicely (e.g., "January 15, 2024")
        self.assertIn(tomorrow.strftime('%B').encode(), response.data)


if __name__ == '__main__':
    unittest.main()
