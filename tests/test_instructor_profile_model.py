"""
Unit tests for InstructorProfile model.

Tests the InstructorProfile model including relationships with User model.
"""

import unittest
from datetime import datetime
from app import create_app, db
from app.models import User, InstructorProfile


class TestInstructorProfileModel(unittest.TestCase):
    """Test cases for InstructorProfile model."""
    
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
    
    def test_create_instructor_profile(self):
        """Test creating an InstructorProfile instance."""
        # First create a user
        user = User(
            username='instructor1',
            email='instructor1@example.com'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # Create instructor profile
        profile = InstructorProfile(
            user_id=user.id,
            photo_path='/uploads/profiles/instructor1.jpg',
            biography='I have been training BJJ for 10 years and teaching for 5 years.',
            title='Instructor',
            is_head_instructor=False
        )
        db.session.add(profile)
        db.session.commit()
        
        # Verify the profile was saved
        self.assertIsNotNone(profile.id)
        self.assertEqual(profile.user_id, user.id)
        self.assertEqual(profile.photo_path, '/uploads/profiles/instructor1.jpg')
        self.assertEqual(profile.biography, 'I have been training BJJ for 10 years and teaching for 5 years.')
        self.assertEqual(profile.title, 'Instructor')
        self.assertFalse(profile.is_head_instructor)
    
    def test_instructor_profile_without_photo(self):
        """Test creating an InstructorProfile without photo (optional field)."""
        # Create a user
        user = User(
            username='instructor2',
            email='instructor2@example.com'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # Create profile without photo
        profile = InstructorProfile(
            user_id=user.id,
            biography='Passionate about teaching Brazilian Jiu-Jitsu.',
            title='Assistant Instructor',
            is_head_instructor=False
        )
        db.session.add(profile)
        db.session.commit()
        
        # Verify the profile was saved without photo
        self.assertIsNotNone(profile.id)
        self.assertIsNone(profile.photo_path)
    
    def test_instructor_profile_head_instructor(self):
        """Test creating a head instructor profile."""
        # Create a user
        user = User(
            username='professor',
            email='professor@example.com'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # Create head instructor profile
        profile = InstructorProfile(
            user_id=user.id,
            photo_path='/uploads/profiles/professor.jpg',
            biography='Black belt with 20 years of experience.',
            title='Professor',
            is_head_instructor=True
        )
        db.session.add(profile)
        db.session.commit()
        
        # Verify the profile was saved as head instructor
        self.assertIsNotNone(profile.id)
        self.assertTrue(profile.is_head_instructor)
        self.assertEqual(profile.title, 'Professor')
    
    def test_instructor_profile_repr(self):
        """Test the string representation of InstructorProfile."""
        # Create a user
        user = User(
            username='instructor3',
            email='instructor3@example.com'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # Create profile
        profile = InstructorProfile(
            user_id=user.id,
            biography='Experienced instructor.',
            title='Instructor',
            is_head_instructor=False
        )
        db.session.add(profile)
        db.session.commit()
        
        repr_str = repr(profile)
        self.assertIn('InstructorProfile', repr_str)
        self.assertIn(str(user.id), repr_str)
        self.assertIn('Instructor', repr_str)
    
    def test_instructor_profile_to_dict(self):
        """Test converting InstructorProfile to dictionary."""
        # Create a user
        user = User(
            username='instructor4',
            email='instructor4@example.com'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # Create profile
        profile = InstructorProfile(
            user_id=user.id,
            photo_path='/uploads/profiles/instructor4.jpg',
            biography='Dedicated to teaching the art of BJJ.',
            title='Senior Instructor',
            is_head_instructor=False
        )
        db.session.add(profile)
        db.session.commit()
        
        profile_dict = profile.to_dict()
        self.assertEqual(profile_dict['user_id'], user.id)
        self.assertEqual(profile_dict['photo_path'], '/uploads/profiles/instructor4.jpg')
        self.assertEqual(profile_dict['biography'], 'Dedicated to teaching the art of BJJ.')
        self.assertEqual(profile_dict['title'], 'Senior Instructor')
        self.assertFalse(profile_dict['is_head_instructor'])
        self.assertIsNotNone(profile_dict['id'])
    
    def test_instructor_profile_required_fields(self):
        """Test that required fields are enforced."""
        # Create a user
        user = User(
            username='instructor5',
            email='instructor5@example.com'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # Test missing user_id
        profile = InstructorProfile(
            biography='Test biography.',
            title='Instructor',
            is_head_instructor=False
        )
        db.session.add(profile)
        with self.assertRaises(Exception):  # SQLAlchemy will raise IntegrityError
            db.session.commit()
        db.session.rollback()
        
        # Test missing biography
        profile = InstructorProfile(
            user_id=user.id,
            title='Instructor',
            is_head_instructor=False
        )
        db.session.add(profile)
        with self.assertRaises(Exception):
            db.session.commit()
        db.session.rollback()
        
        # Test missing title
        profile = InstructorProfile(
            user_id=user.id,
            biography='Test biography.',
            is_head_instructor=False
        )
        db.session.add(profile)
        with self.assertRaises(Exception):
            db.session.commit()
        db.session.rollback()
    
    def test_instructor_profile_relationship_with_user(self):
        """Test the relationship between InstructorProfile and User."""
        # Create a user
        user = User(
            username='instructor6',
            email='instructor6@example.com'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # Create profile
        profile = InstructorProfile(
            user_id=user.id,
            biography='Test biography for relationship.',
            title='Instructor',
            is_head_instructor=False
        )
        db.session.add(profile)
        db.session.commit()
        
        # Test accessing user from profile
        self.assertEqual(profile.user.username, 'instructor6')
        self.assertEqual(profile.user.email, 'instructor6@example.com')
        
        # Test accessing profile from user
        self.assertEqual(user.instructor_profile.biography, 'Test biography for relationship.')
        self.assertEqual(user.instructor_profile.title, 'Instructor')
    
    def test_query_by_is_head_instructor(self):
        """Test querying profiles by is_head_instructor (verifies index)."""
        # Create multiple users and profiles
        user1 = User(username='instructor7', email='instructor7@example.com')
        user1.set_password('password123')
        db.session.add(user1)
        
        user2 = User(username='instructor8', email='instructor8@example.com')
        user2.set_password('password123')
        db.session.add(user2)
        
        user3 = User(username='professor1', email='professor1@example.com')
        user3.set_password('password123')
        db.session.add(user3)
        
        db.session.commit()
        
        profile1 = InstructorProfile(
            user_id=user1.id,
            biography='Regular instructor.',
            title='Instructor',
            is_head_instructor=False
        )
        profile2 = InstructorProfile(
            user_id=user2.id,
            biography='Another instructor.',
            title='Instructor',
            is_head_instructor=False
        )
        profile3 = InstructorProfile(
            user_id=user3.id,
            biography='Head instructor.',
            title='Professor',
            is_head_instructor=True
        )
        db.session.add(profile1)
        db.session.add(profile2)
        db.session.add(profile3)
        db.session.commit()
        
        # Query for head instructor
        head_instructor = InstructorProfile.query.filter_by(is_head_instructor=True).first()
        self.assertIsNotNone(head_instructor)
        self.assertEqual(head_instructor.title, 'Professor')
        self.assertEqual(head_instructor.user.username, 'professor1')
        
        # Query for regular instructors
        regular_instructors = InstructorProfile.query.filter_by(is_head_instructor=False).all()
        self.assertEqual(len(regular_instructors), 2)
    
    def test_cascade_delete_on_user_deletion(self):
        """Test that deleting a user cascades to delete the instructor profile."""
        # Create a user
        user = User(
            username='instructor9',
            email='instructor9@example.com'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # Create profile
        profile = InstructorProfile(
            user_id=user.id,
            biography='This profile should be deleted with the user.',
            title='Instructor',
            is_head_instructor=False
        )
        db.session.add(profile)
        db.session.commit()
        
        profile_id = profile.id
        
        # Delete the user
        db.session.delete(user)
        db.session.commit()
        
        # Verify the profile was also deleted
        deleted_profile = InstructorProfile.query.get(profile_id)
        self.assertIsNone(deleted_profile)
    
    def test_query_by_user_id(self):
        """Test querying profiles by user_id (verifies index)."""
        # Create multiple users and profiles
        user1 = User(username='instructor10', email='instructor10@example.com')
        user1.set_password('password123')
        db.session.add(user1)
        
        user2 = User(username='instructor11', email='instructor11@example.com')
        user2.set_password('password123')
        db.session.add(user2)
        
        db.session.commit()
        
        profile1 = InstructorProfile(
            user_id=user1.id,
            biography='First instructor profile.',
            title='Instructor',
            is_head_instructor=False
        )
        profile2 = InstructorProfile(
            user_id=user2.id,
            biography='Second instructor profile.',
            title='Instructor',
            is_head_instructor=False
        )
        db.session.add(profile1)
        db.session.add(profile2)
        db.session.commit()
        
        # Query by user_id
        found_profile = InstructorProfile.query.filter_by(user_id=user1.id).first()
        self.assertIsNotNone(found_profile)
        self.assertEqual(found_profile.biography, 'First instructor profile.')
        self.assertEqual(found_profile.user.username, 'instructor10')


if __name__ == '__main__':
    unittest.main()
