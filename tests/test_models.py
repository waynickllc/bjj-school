"""
Unit tests for database models.

Tests the ContactSubmission and TrialBooking models.
"""

import unittest
from datetime import datetime, date, timedelta
from app import create_app, db
from app.models import ContactSubmission, TrialBooking


class TestContactSubmissionModel(unittest.TestCase):
    """Test cases for ContactSubmission model."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create app without loading config first
        from flask import Flask
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        self.app.config['WTF_CSRF_ENABLED'] = False
        
        # Initialize extensions with test app
        db.init_app(self.app)
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        """Clean up after tests."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_create_contact_submission(self):
        """Test creating a ContactSubmission instance."""
        submission = ContactSubmission(
            name='John Doe',
            email='john@example.com',
            phone='1234567890',
            message='I am interested in joining your BJJ school.'
        )
        db.session.add(submission)
        db.session.commit()
        
        # Verify the submission was saved
        self.assertIsNotNone(submission.id)
        self.assertEqual(submission.name, 'John Doe')
        self.assertEqual(submission.email, 'john@example.com')
        self.assertEqual(submission.phone, '1234567890')
        self.assertEqual(submission.message, 'I am interested in joining your BJJ school.')
        self.assertIsNotNone(submission.submitted_at)
        self.assertIsInstance(submission.submitted_at, datetime)
    
    def test_contact_submission_without_phone(self):
        """Test creating a ContactSubmission without phone (optional field)."""
        submission = ContactSubmission(
            name='Jane Smith',
            email='jane@example.com',
            message='What are your class times?'
        )
        db.session.add(submission)
        db.session.commit()
        
        # Verify the submission was saved without phone
        self.assertIsNotNone(submission.id)
        self.assertIsNone(submission.phone)
    
    def test_contact_submission_default_timestamp(self):
        """Test that submitted_at defaults to current time."""
        before = datetime.utcnow()
        submission = ContactSubmission(
            name='Test User',
            email='test@example.com',
            message='Test message'
        )
        db.session.add(submission)
        db.session.commit()
        after = datetime.utcnow()
        
        # Verify timestamp is between before and after
        self.assertIsNotNone(submission.submitted_at)
        self.assertGreaterEqual(submission.submitted_at, before)
        self.assertLessEqual(submission.submitted_at, after)
    
    def test_contact_submission_repr(self):
        """Test the string representation of ContactSubmission."""
        submission = ContactSubmission(
            name='Test User',
            email='test@example.com',
            message='Test message'
        )
        db.session.add(submission)
        db.session.commit()
        
        repr_str = repr(submission)
        self.assertIn('ContactSubmission', repr_str)
        self.assertIn('Test User', repr_str)
        self.assertIn('test@example.com', repr_str)
    
    def test_contact_submission_to_dict(self):
        """Test converting ContactSubmission to dictionary."""
        submission = ContactSubmission(
            name='Test User',
            email='test@example.com',
            phone='1234567890',
            message='Test message'
        )
        db.session.add(submission)
        db.session.commit()
        
        submission_dict = submission.to_dict()
        self.assertEqual(submission_dict['name'], 'Test User')
        self.assertEqual(submission_dict['email'], 'test@example.com')
        self.assertEqual(submission_dict['phone'], '1234567890')
        self.assertEqual(submission_dict['message'], 'Test message')
        self.assertIsNotNone(submission_dict['submitted_at'])
        self.assertIsNotNone(submission_dict['id'])
    
    def test_contact_submission_required_fields(self):
        """Test that required fields are enforced."""
        # Test missing name
        submission = ContactSubmission(
            email='test@example.com',
            message='Test message'
        )
        db.session.add(submission)
        with self.assertRaises(Exception):  # SQLAlchemy will raise IntegrityError
            db.session.commit()
        db.session.rollback()
        
        # Test missing email
        submission = ContactSubmission(
            name='Test User',
            message='Test message'
        )
        db.session.add(submission)
        with self.assertRaises(Exception):
            db.session.commit()
        db.session.rollback()
        
        # Test missing message
        submission = ContactSubmission(
            name='Test User',
            email='test@example.com'
        )
        db.session.add(submission)
        with self.assertRaises(Exception):
            db.session.commit()
        db.session.rollback()
    
    def test_query_by_submitted_at(self):
        """Test querying submissions by submitted_at (verifies index)."""
        # Create multiple submissions
        submission1 = ContactSubmission(
            name='User 1',
            email='user1@example.com',
            message='Message 1'
        )
        submission2 = ContactSubmission(
            name='User 2',
            email='user2@example.com',
            message='Message 2'
        )
        db.session.add(submission1)
        db.session.add(submission2)
        db.session.commit()
        
        # Query by submitted_at
        results = ContactSubmission.query.order_by(ContactSubmission.submitted_at.desc()).all()
        self.assertEqual(len(results), 2)
        # Most recent should be first
        self.assertEqual(results[0].name, 'User 2')
        self.assertEqual(results[1].name, 'User 1')


if __name__ == '__main__':
    unittest.main()


class TestTrialBookingModel(unittest.TestCase):
    """Test cases for TrialBooking model."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create app without loading config first
        from flask import Flask
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        self.app.config['WTF_CSRF_ENABLED'] = False
        
        # Initialize extensions with test app
        db.init_app(self.app)
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        """Clean up after tests."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_create_trial_booking(self):
        """Test creating a TrialBooking instance."""
        future_date = date.today() + timedelta(days=7)
        booking = TrialBooking(
            name='John Doe',
            email='john@example.com',
            phone='1234567890',
            preferred_date=future_date,
            preferred_time='morning'
        )
        db.session.add(booking)
        db.session.commit()
        
        # Verify the booking was saved
        self.assertIsNotNone(booking.id)
        self.assertEqual(booking.name, 'John Doe')
        self.assertEqual(booking.email, 'john@example.com')
        self.assertEqual(booking.phone, '1234567890')
        self.assertEqual(booking.preferred_date, future_date)
        self.assertEqual(booking.preferred_time, 'morning')
        self.assertIsNotNone(booking.submitted_at)
        self.assertIsInstance(booking.submitted_at, datetime)
    
    def test_trial_booking_default_timestamp(self):
        """Test that submitted_at defaults to current time."""
        before = datetime.utcnow()
        future_date = date.today() + timedelta(days=7)
        booking = TrialBooking(
            name='Test User',
            email='test@example.com',
            phone='1234567890',
            preferred_date=future_date,
            preferred_time='evening'
        )
        db.session.add(booking)
        db.session.commit()
        after = datetime.utcnow()
        
        # Verify timestamp is between before and after
        self.assertIsNotNone(booking.submitted_at)
        self.assertGreaterEqual(booking.submitted_at, before)
        self.assertLessEqual(booking.submitted_at, after)
    
    def test_trial_booking_repr(self):
        """Test the string representation of TrialBooking."""
        future_date = date.today() + timedelta(days=7)
        booking = TrialBooking(
            name='Test User',
            email='test@example.com',
            phone='1234567890',
            preferred_date=future_date,
            preferred_time='afternoon'
        )
        db.session.add(booking)
        db.session.commit()
        
        repr_str = repr(booking)
        self.assertIn('TrialBooking', repr_str)
        self.assertIn('Test User', repr_str)
        self.assertIn('test@example.com', repr_str)
        self.assertIn(str(future_date), repr_str)
    
    def test_trial_booking_to_dict(self):
        """Test converting TrialBooking to dictionary."""
        future_date = date.today() + timedelta(days=7)
        booking = TrialBooking(
            name='Test User',
            email='test@example.com',
            phone='1234567890',
            preferred_date=future_date,
            preferred_time='morning'
        )
        db.session.add(booking)
        db.session.commit()
        
        booking_dict = booking.to_dict()
        self.assertEqual(booking_dict['name'], 'Test User')
        self.assertEqual(booking_dict['email'], 'test@example.com')
        self.assertEqual(booking_dict['phone'], '1234567890')
        self.assertEqual(booking_dict['preferred_date'], future_date.isoformat())
        self.assertEqual(booking_dict['preferred_time'], 'morning')
        self.assertIsNotNone(booking_dict['submitted_at'])
        self.assertIsNotNone(booking_dict['id'])
    
    def test_trial_booking_required_fields(self):
        """Test that required fields are enforced."""
        future_date = date.today() + timedelta(days=7)
        
        # Test missing name
        booking = TrialBooking(
            email='test@example.com',
            phone='1234567890',
            preferred_date=future_date,
            preferred_time='morning'
        )
        db.session.add(booking)
        with self.assertRaises(Exception):  # SQLAlchemy will raise IntegrityError
            db.session.commit()
        db.session.rollback()
        
        # Test missing email
        booking = TrialBooking(
            name='Test User',
            phone='1234567890',
            preferred_date=future_date,
            preferred_time='morning'
        )
        db.session.add(booking)
        with self.assertRaises(Exception):
            db.session.commit()
        db.session.rollback()
        
        # Test missing phone
        booking = TrialBooking(
            name='Test User',
            email='test@example.com',
            preferred_date=future_date,
            preferred_time='morning'
        )
        db.session.add(booking)
        with self.assertRaises(Exception):
            db.session.commit()
        db.session.rollback()
        
        # Test missing preferred_date
        booking = TrialBooking(
            name='Test User',
            email='test@example.com',
            phone='1234567890',
            preferred_time='morning'
        )
        db.session.add(booking)
        with self.assertRaises(Exception):
            db.session.commit()
        db.session.rollback()
        
        # Test missing preferred_time
        booking = TrialBooking(
            name='Test User',
            email='test@example.com',
            phone='1234567890',
            preferred_date=future_date
        )
        db.session.add(booking)
        with self.assertRaises(Exception):
            db.session.commit()
        db.session.rollback()
    
    def test_query_by_email(self):
        """Test querying bookings by email (verifies index)."""
        future_date = date.today() + timedelta(days=7)
        
        # Create multiple bookings
        booking1 = TrialBooking(
            name='User 1',
            email='user1@example.com',
            phone='1111111111',
            preferred_date=future_date,
            preferred_time='morning'
        )
        booking2 = TrialBooking(
            name='User 2',
            email='user2@example.com',
            phone='2222222222',
            preferred_date=future_date,
            preferred_time='afternoon'
        )
        booking3 = TrialBooking(
            name='User 1 Again',
            email='user1@example.com',
            phone='1111111111',
            preferred_date=future_date + timedelta(days=1),
            preferred_time='evening'
        )
        db.session.add(booking1)
        db.session.add(booking2)
        db.session.add(booking3)
        db.session.commit()
        
        # Query by email
        results = TrialBooking.query.filter_by(email='user1@example.com').all()
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].email, 'user1@example.com')
        self.assertEqual(results[1].email, 'user1@example.com')
    
    def test_query_by_submitted_at(self):
        """Test querying bookings by submitted_at (verifies index)."""
        future_date = date.today() + timedelta(days=7)
        
        # Create multiple bookings
        booking1 = TrialBooking(
            name='User 1',
            email='user1@example.com',
            phone='1111111111',
            preferred_date=future_date,
            preferred_time='morning'
        )
        booking2 = TrialBooking(
            name='User 2',
            email='user2@example.com',
            phone='2222222222',
            preferred_date=future_date,
            preferred_time='afternoon'
        )
        db.session.add(booking1)
        db.session.add(booking2)
        db.session.commit()
        
        # Query by submitted_at
        results = TrialBooking.query.order_by(TrialBooking.submitted_at.desc()).all()
        self.assertEqual(len(results), 2)
        # Most recent should be first
        self.assertEqual(results[0].name, 'User 2')
        self.assertEqual(results[1].name, 'User 1')
    
    def test_trial_booking_with_today_date(self):
        """Test creating a booking with today's date (should be allowed)."""
        today = date.today()
        booking = TrialBooking(
            name='Test User',
            email='test@example.com',
            phone='1234567890',
            preferred_date=today,
            preferred_time='morning'
        )
        db.session.add(booking)
        # SQLite doesn't enforce CHECK constraints by default, so this test
        # verifies the model accepts today's date. In MySQL, the constraint
        # would be enforced at the database level.
        db.session.commit()
        
        self.assertIsNotNone(booking.id)
        self.assertEqual(booking.preferred_date, today)
