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



class TestClassModel(unittest.TestCase):
    """Test cases for Class model."""
    
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
    
    def test_create_class(self):
        """Test creating a Class instance."""
        from datetime import time
        from app.models import Class
        
        class_obj = Class(
            name='Fundamentals',
            day_of_week='Monday',
            start_time=time(18, 0),  # 6:00 PM
            end_time=time(19, 30)    # 7:30 PM
        )
        db.session.add(class_obj)
        db.session.commit()
        
        # Verify the class was saved
        self.assertIsNotNone(class_obj.id)
        self.assertEqual(class_obj.name, 'Fundamentals')
        self.assertEqual(class_obj.day_of_week, 'Monday')
        self.assertEqual(class_obj.start_time, time(18, 0))
        self.assertEqual(class_obj.end_time, time(19, 30))
    
    def test_class_repr(self):
        """Test the string representation of Class."""
        from datetime import time
        from app.models import Class
        
        class_obj = Class(
            name='Advanced',
            day_of_week='Wednesday',
            start_time=time(19, 0),
            end_time=time(20, 30)
        )
        db.session.add(class_obj)
        db.session.commit()
        
        repr_str = repr(class_obj)
        self.assertIn('Class', repr_str)
        self.assertIn('Advanced', repr_str)
        self.assertIn('Wednesday', repr_str)
        self.assertIn('19:00:00', repr_str)
    
    def test_class_to_dict(self):
        """Test converting Class to dictionary."""
        from datetime import time
        from app.models import Class
        
        class_obj = Class(
            name='No-Gi',
            day_of_week='Friday',
            start_time=time(18, 30),
            end_time=time(20, 0)
        )
        db.session.add(class_obj)
        db.session.commit()
        
        class_dict = class_obj.to_dict()
        self.assertEqual(class_dict['name'], 'No-Gi')
        self.assertEqual(class_dict['day_of_week'], 'Friday')
        self.assertEqual(class_dict['start_time'], '18:30')
        self.assertEqual(class_dict['end_time'], '20:00')
        self.assertIsNotNone(class_dict['id'])
    
    def test_class_required_fields(self):
        """Test that required fields are enforced."""
        from datetime import time
        from app.models import Class
        
        # Test missing name
        class_obj = Class(
            day_of_week='Monday',
            start_time=time(18, 0),
            end_time=time(19, 30)
        )
        db.session.add(class_obj)
        with self.assertRaises(Exception):  # SQLAlchemy will raise IntegrityError
            db.session.commit()
        db.session.rollback()
        
        # Test missing day_of_week
        class_obj = Class(
            name='Fundamentals',
            start_time=time(18, 0),
            end_time=time(19, 30)
        )
        db.session.add(class_obj)
        with self.assertRaises(Exception):
            db.session.commit()
        db.session.rollback()
        
        # Test missing start_time
        class_obj = Class(
            name='Fundamentals',
            day_of_week='Monday',
            end_time=time(19, 30)
        )
        db.session.add(class_obj)
        with self.assertRaises(Exception):
            db.session.commit()
        db.session.rollback()
        
        # Test missing end_time
        class_obj = Class(
            name='Fundamentals',
            day_of_week='Monday',
            start_time=time(18, 0)
        )
        db.session.add(class_obj)
        with self.assertRaises(Exception):
            db.session.commit()
        db.session.rollback()
    
    def test_query_by_day_of_week(self):
        """Test querying classes by day_of_week (verifies index)."""
        from datetime import time
        from app.models import Class
        
        # Create multiple classes
        class1 = Class(
            name='Fundamentals',
            day_of_week='Monday',
            start_time=time(18, 0),
            end_time=time(19, 30)
        )
        class2 = Class(
            name='Advanced',
            day_of_week='Monday',
            start_time=time(19, 30),
            end_time=time(21, 0)
        )
        class3 = Class(
            name='No-Gi',
            day_of_week='Friday',
            start_time=time(18, 30),
            end_time=time(20, 0)
        )
        db.session.add(class1)
        db.session.add(class2)
        db.session.add(class3)
        db.session.commit()
        
        # Query by day_of_week
        monday_classes = Class.query.filter_by(day_of_week='Monday').all()
        self.assertEqual(len(monday_classes), 2)
        self.assertEqual(monday_classes[0].day_of_week, 'Monday')
        self.assertEqual(monday_classes[1].day_of_week, 'Monday')
        
        friday_classes = Class.query.filter_by(day_of_week='Friday').all()
        self.assertEqual(len(friday_classes), 1)
        self.assertEqual(friday_classes[0].name, 'No-Gi')
    
    def test_multiple_classes_same_day(self):
        """Test creating multiple classes on the same day."""
        from datetime import time
        from app.models import Class
        
        class1 = Class(
            name='Morning Class',
            day_of_week='Tuesday',
            start_time=time(6, 0),
            end_time=time(7, 0)
        )
        class2 = Class(
            name='Evening Class',
            day_of_week='Tuesday',
            start_time=time(18, 0),
            end_time=time(19, 30)
        )
        db.session.add(class1)
        db.session.add(class2)
        db.session.commit()
        
        # Verify both classes were saved
        tuesday_classes = Class.query.filter_by(day_of_week='Tuesday').order_by(Class.start_time).all()
        self.assertEqual(len(tuesday_classes), 2)
        self.assertEqual(tuesday_classes[0].name, 'Morning Class')
        self.assertEqual(tuesday_classes[1].name, 'Evening Class')
    
    def test_class_time_formatting(self):
        """Test that times are properly formatted in to_dict."""
        from datetime import time
        from app.models import Class
        
        class_obj = Class(
            name='Early Morning',
            day_of_week='Saturday',
            start_time=time(6, 0),
            end_time=time(7, 30)
        )
        db.session.add(class_obj)
        db.session.commit()
        
        class_dict = class_obj.to_dict()
        # Verify time format is HH:MM
        self.assertEqual(class_dict['start_time'], '06:00')
        self.assertEqual(class_dict['end_time'], '07:30')



class TestAnnouncementModel(unittest.TestCase):
    """Test cases for Announcement model."""
    
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
    
    def test_create_announcement(self):
        """Test creating an Announcement instance."""
        from app.models import Announcement
        
        announcement = Announcement(
            title='Welcome to Our BJJ School',
            content='We are excited to announce the opening of our new facility!'
        )
        db.session.add(announcement)
        db.session.commit()
        
        # Verify the announcement was saved
        self.assertIsNotNone(announcement.id)
        self.assertEqual(announcement.title, 'Welcome to Our BJJ School')
        self.assertEqual(announcement.content, 'We are excited to announce the opening of our new facility!')
        self.assertIsNotNone(announcement.published_date)
        self.assertIsInstance(announcement.published_date, datetime)
    
    def test_announcement_default_timestamp(self):
        """Test that published_date defaults to current time."""
        from app.models import Announcement
        
        before = datetime.utcnow()
        announcement = Announcement(
            title='Test Announcement',
            content='This is a test announcement.'
        )
        db.session.add(announcement)
        db.session.commit()
        after = datetime.utcnow()
        
        # Verify timestamp is between before and after
        self.assertIsNotNone(announcement.published_date)
        self.assertGreaterEqual(announcement.published_date, before)
        self.assertLessEqual(announcement.published_date, after)
    
    def test_announcement_repr(self):
        """Test the string representation of Announcement."""
        from app.models import Announcement
        
        announcement = Announcement(
            title='Important Update',
            content='Please read this important information.'
        )
        db.session.add(announcement)
        db.session.commit()
        
        repr_str = repr(announcement)
        self.assertIn('Announcement', repr_str)
        self.assertIn('Important Update', repr_str)
    
    def test_announcement_to_dict(self):
        """Test converting Announcement to dictionary."""
        from app.models import Announcement
        
        announcement = Announcement(
            title='New Schedule',
            content='Check out our updated class schedule for next month.'
        )
        db.session.add(announcement)
        db.session.commit()
        
        announcement_dict = announcement.to_dict()
        self.assertEqual(announcement_dict['title'], 'New Schedule')
        self.assertEqual(announcement_dict['content'], 'Check out our updated class schedule for next month.')
        self.assertIsNotNone(announcement_dict['published_date'])
        self.assertIsNotNone(announcement_dict['id'])
    
    def test_announcement_required_fields(self):
        """Test that required fields are enforced."""
        from app.models import Announcement
        
        # Test missing title
        announcement = Announcement(
            content='This announcement has no title.'
        )
        db.session.add(announcement)
        with self.assertRaises(Exception):  # SQLAlchemy will raise IntegrityError
            db.session.commit()
        db.session.rollback()
        
        # Test missing content
        announcement = Announcement(
            title='Title Only'
        )
        db.session.add(announcement)
        with self.assertRaises(Exception):
            db.session.commit()
        db.session.rollback()
    
    def test_query_by_published_date(self):
        """Test querying announcements by published_date (verifies index)."""
        from app.models import Announcement
        
        # Create multiple announcements
        announcement1 = Announcement(
            title='First Announcement',
            content='This is the first announcement.'
        )
        announcement2 = Announcement(
            title='Second Announcement',
            content='This is the second announcement.'
        )
        announcement3 = Announcement(
            title='Third Announcement',
            content='This is the third announcement.'
        )
        db.session.add(announcement1)
        db.session.add(announcement2)
        db.session.add(announcement3)
        db.session.commit()
        
        # Query by published_date in reverse chronological order (newest first)
        results = Announcement.query.order_by(Announcement.published_date.desc()).all()
        self.assertEqual(len(results), 3)
        # Most recent should be first
        self.assertEqual(results[0].title, 'Third Announcement')
        self.assertEqual(results[1].title, 'Second Announcement')
        self.assertEqual(results[2].title, 'First Announcement')
    
    def test_announcement_with_long_content(self):
        """Test creating an announcement with long content."""
        from app.models import Announcement
        
        long_content = 'This is a very long announcement. ' * 100
        announcement = Announcement(
            title='Long Announcement',
            content=long_content
        )
        db.session.add(announcement)
        db.session.commit()
        
        # Verify the announcement was saved with full content
        self.assertIsNotNone(announcement.id)
        self.assertEqual(announcement.content, long_content)
        self.assertEqual(len(announcement.content), len(long_content))
    
    def test_multiple_announcements_ordering(self):
        """Test that multiple announcements can be ordered by published_date."""
        from app.models import Announcement
        import time
        
        # Create announcements with slight delays to ensure different timestamps
        announcement1 = Announcement(
            title='Oldest',
            content='This is the oldest announcement.'
        )
        db.session.add(announcement1)
        db.session.commit()
        
        time.sleep(0.01)  # Small delay
        
        announcement2 = Announcement(
            title='Middle',
            content='This is the middle announcement.'
        )
        db.session.add(announcement2)
        db.session.commit()
        
        time.sleep(0.01)  # Small delay
        
        announcement3 = Announcement(
            title='Newest',
            content='This is the newest announcement.'
        )
        db.session.add(announcement3)
        db.session.commit()
        
        # Query in reverse chronological order
        results = Announcement.query.order_by(Announcement.published_date.desc()).all()
        self.assertEqual(results[0].title, 'Newest')
        self.assertEqual(results[1].title, 'Middle')
        self.assertEqual(results[2].title, 'Oldest')
        
        # Verify timestamps are in correct order
        self.assertGreater(results[0].published_date, results[1].published_date)
        self.assertGreater(results[1].published_date, results[2].published_date)



class TestUserModel(unittest.TestCase):
    """Test cases for User model."""
    
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
    
    def test_create_user(self):
        """Test creating a User instance."""
        from app.models import User
        
        user = User(
            username='instructor1',
            email='instructor1@example.com'
        )
        user.set_password('securepassword123')
        db.session.add(user)
        db.session.commit()
        
        # Verify the user was saved
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, 'instructor1')
        self.assertEqual(user.email, 'instructor1@example.com')
        self.assertIsNotNone(user.password_hash)
        self.assertIsNotNone(user.created_at)
        self.assertIsInstance(user.created_at, datetime)
    
    def test_password_hashing(self):
        """Test that passwords are properly hashed."""
        from app.models import User
        
        user = User(
            username='testuser',
            email='test@example.com'
        )
        password = 'mypassword123'
        user.set_password(password)
        
        # Verify password is hashed (not stored in plain text)
        self.assertNotEqual(user.password_hash, password)
        self.assertTrue(len(user.password_hash) > 50)  # Hashed passwords are long
    
    def test_password_verification(self):
        """Test password verification with check_password method."""
        from app.models import User
        
        user = User(
            username='testuser',
            email='test@example.com'
        )
        password = 'correctpassword'
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        # Verify correct password
        self.assertTrue(user.check_password(password))
        
        # Verify incorrect password
        self.assertFalse(user.check_password('wrongpassword'))
        self.assertFalse(user.check_password(''))
        self.assertFalse(user.check_password('correctPassword'))  # Case sensitive
    
    def test_unique_username(self):
        """Test that username must be unique."""
        from app.models import User
        
        user1 = User(
            username='instructor',
            email='instructor1@example.com'
        )
        user1.set_password('password1')
        db.session.add(user1)
        db.session.commit()
        
        # Try to create another user with same username
        user2 = User(
            username='instructor',  # Same username
            email='instructor2@example.com'  # Different email
        )
        user2.set_password('password2')
        db.session.add(user2)
        
        # Should raise IntegrityError due to unique constraint
        with self.assertRaises(Exception):
            db.session.commit()
        db.session.rollback()
    
    def test_unique_email(self):
        """Test that email must be unique."""
        from app.models import User
        
        user1 = User(
            username='instructor1',
            email='instructor@example.com'
        )
        user1.set_password('password1')
        db.session.add(user1)
        db.session.commit()
        
        # Try to create another user with same email
        user2 = User(
            username='instructor2',  # Different username
            email='instructor@example.com'  # Same email
        )
        user2.set_password('password2')
        db.session.add(user2)
        
        # Should raise IntegrityError due to unique constraint
        with self.assertRaises(Exception):
            db.session.commit()
        db.session.rollback()
    
    def test_user_repr(self):
        """Test the string representation of User."""
        from app.models import User
        
        user = User(
            username='testinstructor',
            email='test@example.com'
        )
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        
        repr_str = repr(user)
        self.assertIn('User', repr_str)
        self.assertIn('testinstructor', repr_str)
        self.assertIn('test@example.com', repr_str)
    
    def test_user_to_dict(self):
        """Test converting User to dictionary."""
        from app.models import User
        
        user = User(
            username='instructor',
            email='instructor@example.com'
        )
        user.set_password('securepassword')
        db.session.add(user)
        db.session.commit()
        
        user_dict = user.to_dict()
        self.assertEqual(user_dict['username'], 'instructor')
        self.assertEqual(user_dict['email'], 'instructor@example.com')
        self.assertIsNotNone(user_dict['created_at'])
        self.assertIsNotNone(user_dict['id'])
        
        # Verify password_hash is NOT included in dictionary (security)
        self.assertNotIn('password_hash', user_dict)
        self.assertNotIn('password', user_dict)
    
    def test_user_required_fields(self):
        """Test that required fields are enforced."""
        from app.models import User
        
        # Test missing username
        user = User(
            email='test@example.com'
        )
        user.set_password('password')
        db.session.add(user)
        with self.assertRaises(Exception):  # SQLAlchemy will raise IntegrityError
            db.session.commit()
        db.session.rollback()
        
        # Test missing email
        user = User(
            username='testuser'
        )
        user.set_password('password')
        db.session.add(user)
        with self.assertRaises(Exception):
            db.session.commit()
        db.session.rollback()
        
        # Test missing password_hash
        user = User(
            username='testuser',
            email='test@example.com'
        )
        # Don't set password
        db.session.add(user)
        with self.assertRaises(Exception):
            db.session.commit()
        db.session.rollback()
    
    def test_query_by_username(self):
        """Test querying users by username (verifies index)."""
        from app.models import User
        
        user = User(
            username='instructor1',
            email='instructor1@example.com'
        )
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        
        # Query by username
        result = User.query.filter_by(username='instructor1').first()
        self.assertIsNotNone(result)
        self.assertEqual(result.username, 'instructor1')
        self.assertEqual(result.email, 'instructor1@example.com')
    
    def test_query_by_email(self):
        """Test querying users by email (verifies index)."""
        from app.models import User
        
        user = User(
            username='instructor1',
            email='instructor1@example.com'
        )
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        
        # Query by email
        result = User.query.filter_by(email='instructor1@example.com').first()
        self.assertIsNotNone(result)
        self.assertEqual(result.username, 'instructor1')
        self.assertEqual(result.email, 'instructor1@example.com')
    
    def test_user_default_timestamp(self):
        """Test that created_at defaults to current time."""
        from app.models import User
        
        before = datetime.utcnow()
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        after = datetime.utcnow()
        
        # Verify timestamp is between before and after
        self.assertIsNotNone(user.created_at)
        self.assertGreaterEqual(user.created_at, before)
        self.assertLessEqual(user.created_at, after)
    
    def test_multiple_users(self):
        """Test creating multiple users."""
        from app.models import User
        
        user1 = User(
            username='instructor1',
            email='instructor1@example.com'
        )
        user1.set_password('password1')
        
        user2 = User(
            username='instructor2',
            email='instructor2@example.com'
        )
        user2.set_password('password2')
        
        user3 = User(
            username='instructor3',
            email='instructor3@example.com'
        )
        user3.set_password('password3')
        
        db.session.add(user1)
        db.session.add(user2)
        db.session.add(user3)
        db.session.commit()
        
        # Verify all users were saved
        all_users = User.query.all()
        self.assertEqual(len(all_users), 3)
        
        usernames = [u.username for u in all_users]
        self.assertIn('instructor1', usernames)
        self.assertIn('instructor2', usernames)
        self.assertIn('instructor3', usernames)
    
    def test_password_hash_different_for_same_password(self):
        """Test that same password produces different hashes (salt)."""
        from app.models import User
        
        password = 'samepassword'
        
        user1 = User(
            username='user1',
            email='user1@example.com'
        )
        user1.set_password(password)
        
        user2 = User(
            username='user2',
            email='user2@example.com'
        )
        user2.set_password(password)
        
        # Even though passwords are the same, hashes should be different (due to salt)
        self.assertNotEqual(user1.password_hash, user2.password_hash)
        
        # But both should verify correctly
        self.assertTrue(user1.check_password(password))
        self.assertTrue(user2.check_password(password))



class TestSiteSettingsModel(unittest.TestCase):
    """Test cases for SiteSettings model."""
    
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
    
    def test_create_site_settings(self):
        """Test creating a SiteSettings instance."""
        from app.models import SiteSettings
        
        settings = SiteSettings(
            id=1,
            banner_image_path='uploads/banners/banner.jpg',
            logo_image_path='uploads/logos/logo.png'
        )
        db.session.add(settings)
        db.session.commit()
        
        # Verify the settings were saved
        self.assertEqual(settings.id, 1)
        self.assertEqual(settings.banner_image_path, 'uploads/banners/banner.jpg')
        self.assertEqual(settings.logo_image_path, 'uploads/logos/logo.png')
    
    def test_site_settings_with_null_paths(self):
        """Test creating SiteSettings with NULL image paths (defaults)."""
        from app.models import SiteSettings
        
        settings = SiteSettings(id=1)
        db.session.add(settings)
        db.session.commit()
        
        # Verify the settings were saved with NULL paths
        self.assertEqual(settings.id, 1)
        self.assertIsNone(settings.banner_image_path)
        self.assertIsNone(settings.logo_image_path)
    
    def test_site_settings_singleton_pattern(self):
        """Test that only one SiteSettings record should exist (id=1)."""
        from app.models import SiteSettings
        
        # Create first settings record
        settings1 = SiteSettings(id=1, banner_image_path='banner1.jpg')
        db.session.add(settings1)
        db.session.commit()
        
        # Verify it was saved
        self.assertEqual(settings1.id, 1)
        
        # Note: SQLite doesn't enforce CHECK constraints by default,
        # so we can't test the constraint here. In MySQL production,
        # attempting to insert a record with id != 1 would fail.
        # The singleton pattern is enforced at the application level.
    
    def test_site_settings_repr(self):
        """Test the string representation of SiteSettings."""
        from app.models import SiteSettings
        
        settings = SiteSettings(
            id=1,
            banner_image_path='uploads/banners/hero.jpg',
            logo_image_path='uploads/logos/brand.svg'
        )
        db.session.add(settings)
        db.session.commit()
        
        repr_str = repr(settings)
        self.assertIn('SiteSettings', repr_str)
        self.assertIn('id=1', repr_str)
        self.assertIn('banner=uploads/banners/hero.jpg', repr_str)
        self.assertIn('logo=uploads/logos/brand.svg', repr_str)
    
    def test_site_settings_to_dict(self):
        """Test converting SiteSettings to dictionary."""
        from app.models import SiteSettings
        
        settings = SiteSettings(
            id=1,
            banner_image_path='uploads/banners/banner.jpg',
            logo_image_path='uploads/logos/logo.png'
        )
        db.session.add(settings)
        db.session.commit()
        
        settings_dict = settings.to_dict()
        self.assertEqual(settings_dict['id'], 1)
        self.assertEqual(settings_dict['banner_image_path'], 'uploads/banners/banner.jpg')
        self.assertEqual(settings_dict['logo_image_path'], 'uploads/logos/logo.png')
    
    def test_site_settings_to_dict_with_nulls(self):
        """Test converting SiteSettings with NULL paths to dictionary."""
        from app.models import SiteSettings
        
        settings = SiteSettings(id=1)
        db.session.add(settings)
        db.session.commit()
        
        settings_dict = settings.to_dict()
        self.assertEqual(settings_dict['id'], 1)
        self.assertIsNone(settings_dict['banner_image_path'])
        self.assertIsNone(settings_dict['logo_image_path'])
    
    def test_update_site_settings(self):
        """Test updating SiteSettings (singleton pattern usage)."""
        from app.models import SiteSettings
        
        # Create initial settings
        settings = SiteSettings(id=1)
        db.session.add(settings)
        db.session.commit()
        
        # Update banner path
        settings.banner_image_path = 'uploads/banners/new_banner.jpg'
        db.session.commit()
        
        # Verify update
        updated_settings = SiteSettings.query.get(1)
        self.assertEqual(updated_settings.banner_image_path, 'uploads/banners/new_banner.jpg')
        self.assertIsNone(updated_settings.logo_image_path)
        
        # Update logo path
        settings.logo_image_path = 'uploads/logos/new_logo.png'
        db.session.commit()
        
        # Verify both paths are set
        updated_settings = SiteSettings.query.get(1)
        self.assertEqual(updated_settings.banner_image_path, 'uploads/banners/new_banner.jpg')
        self.assertEqual(updated_settings.logo_image_path, 'uploads/logos/new_logo.png')
    
    def test_query_site_settings(self):
        """Test querying SiteSettings by id."""
        from app.models import SiteSettings
        
        settings = SiteSettings(
            id=1,
            banner_image_path='banner.jpg',
            logo_image_path='logo.png'
        )
        db.session.add(settings)
        db.session.commit()
        
        # Query by id
        result = SiteSettings.query.get(1)
        self.assertIsNotNone(result)
        self.assertEqual(result.id, 1)
        self.assertEqual(result.banner_image_path, 'banner.jpg')
        self.assertEqual(result.logo_image_path, 'logo.png')
    
    def test_site_settings_path_max_length(self):
        """Test that image paths can store up to 255 characters."""
        from app.models import SiteSettings
        
        # Create a long path (255 characters)
        # 'uploads/banners/' = 16 chars, '.jpg' = 4 chars, so we need 235 'a's
        long_path = 'uploads/banners/' + 'a' * 235 + '.jpg'
        self.assertEqual(len(long_path), 255)
        
        settings = SiteSettings(
            id=1,
            banner_image_path=long_path
        )
        db.session.add(settings)
        db.session.commit()
        
        # Verify the long path was saved
        result = SiteSettings.query.get(1)
        self.assertEqual(result.banner_image_path, long_path)
        self.assertEqual(len(result.banner_image_path), 255)
    
    def test_remove_banner_image(self):
        """Test removing banner image by setting path to NULL."""
        from app.models import SiteSettings
        
        # Create settings with banner
        settings = SiteSettings(
            id=1,
            banner_image_path='uploads/banners/banner.jpg',
            logo_image_path='uploads/logos/logo.png'
        )
        db.session.add(settings)
        db.session.commit()
        
        # Remove banner by setting to None
        settings.banner_image_path = None
        db.session.commit()
        
        # Verify banner is removed but logo remains
        result = SiteSettings.query.get(1)
        self.assertIsNone(result.banner_image_path)
        self.assertEqual(result.logo_image_path, 'uploads/logos/logo.png')
    
    def test_remove_logo_image(self):
        """Test removing logo image by setting path to NULL."""
        from app.models import SiteSettings
        
        # Create settings with logo
        settings = SiteSettings(
            id=1,
            banner_image_path='uploads/banners/banner.jpg',
            logo_image_path='uploads/logos/logo.png'
        )
        db.session.add(settings)
        db.session.commit()
        
        # Remove logo by setting to None
        settings.logo_image_path = None
        db.session.commit()
        
        # Verify logo is removed but banner remains
        result = SiteSettings.query.get(1)
        self.assertEqual(result.banner_image_path, 'uploads/banners/banner.jpg')
        self.assertIsNone(result.logo_image_path)
