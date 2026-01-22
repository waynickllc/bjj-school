"""
Tests for admin profile management routes.

This module tests the instructor profile management functionality including:
- Profile form display
- Photo upload and validation
- Biography validation
- Head instructor designation logic
- Profile updates
"""

import unittest
import os
import io
from app import create_app, db
from app.models import User, InstructorProfile


class TestAdminProfile(unittest.TestCase):
    """Test cases for admin profile management routes."""
    
    def setUp(self):
        """Set up test client and database."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        # Create test user
        self.test_user = User(
            username='testinstructor',
            email='test@example.com'
        )
        self.test_user.set_password('password123')
        db.session.add(self.test_user)
        db.session.commit()
        
        # Log in the test user
        self.client.post('/login', data={
            'username': 'testinstructor',
            'password': 'password123'
        }, follow_redirects=True)
    
    def tearDown(self):
        """Clean up after tests."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_profile_page_requires_login(self):
        """Test that profile page requires authentication."""
        # Log out
        self.client.get('/logout', follow_redirects=True)
        
        # Try to access profile page
        response = self.client.get('/admin/profile')
        
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)
    
    def test_profile_page_displays_form(self):
        """Test that profile page displays the form correctly."""
        response = self.client.get('/admin/profile')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'My Profile', response.data)
        self.assertIn(b'Biography', response.data)
        self.assertIn(b'Title/Designation', response.data)
        self.assertIn(b'Head Instructor', response.data)
    
    def test_create_profile_on_first_access(self):
        """Test that a profile is created automatically if it doesn't exist."""
        # Ensure no profile exists
        profile = InstructorProfile.query.filter_by(user_id=self.test_user.id).first()
        self.assertIsNone(profile)
        
        # Access profile page
        response = self.client.get('/admin/profile')
        
        self.assertEqual(response.status_code, 200)
        
        # Check that profile was created
        profile = InstructorProfile.query.filter_by(user_id=self.test_user.id).first()
        self.assertIsNotNone(profile)
        self.assertEqual(profile.title, 'Instructor')
        self.assertFalse(profile.is_head_instructor)
    
    def test_update_profile_biography_and_title(self):
        """Test updating profile biography and title."""
        # Create initial profile
        self.client.get('/admin/profile')
        
        # Update profile
        response = self.client.post('/admin/profile', data={
            'biography': 'This is my updated biography with more than 10 characters.',
            'title': 'Black Belt Instructor',
            'is_head_instructor': False
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Profile updated successfully', response.data)
        
        # Verify changes in database
        profile = InstructorProfile.query.filter_by(user_id=self.test_user.id).first()
        self.assertEqual(profile.biography, 'This is my updated biography with more than 10 characters.')
        self.assertEqual(profile.title, 'Black Belt Instructor')
    
    def test_biography_validation_min_length(self):
        """Test that biography must be at least 10 characters."""
        # Create initial profile
        self.client.get('/admin/profile')
        
        # Try to update with short biography
        response = self.client.post('/admin/profile', data={
            'biography': 'Short',
            'title': 'Instructor',
            'is_head_instructor': False
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Biography must be 10-5000 characters', response.data)
    
    def test_biography_validation_max_length(self):
        """Test that biography cannot exceed 5000 characters."""
        # Create initial profile
        self.client.get('/admin/profile')
        
        # Try to update with very long biography
        long_bio = 'A' * 5001
        response = self.client.post('/admin/profile', data={
            'biography': long_bio,
            'title': 'Instructor',
            'is_head_instructor': False
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Biography must be 10-5000 characters', response.data)
    
    def test_set_head_instructor(self):
        """Test setting an instructor as head instructor."""
        # Create initial profile
        self.client.get('/admin/profile')
        
        # Set as head instructor
        response = self.client.post('/admin/profile', data={
            'biography': 'I am the head instructor with extensive experience.',
            'title': 'Head Instructor',
            'is_head_instructor': True
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Head Instructor', response.data)
        
        # Verify in database
        profile = InstructorProfile.query.filter_by(user_id=self.test_user.id).first()
        self.assertTrue(profile.is_head_instructor)
    
    def test_only_one_head_instructor(self):
        """Test that only one instructor can be head instructor at a time."""
        # Create first instructor profile
        self.client.get('/admin/profile')
        self.client.post('/admin/profile', data={
            'biography': 'First instructor biography.',
            'title': 'Head Instructor',
            'is_head_instructor': True
        }, follow_redirects=True)
        
        # Create second user and profile
        second_user = User(
            username='secondinstructor',
            email='second@example.com'
        )
        second_user.set_password('password123')
        db.session.add(second_user)
        db.session.commit()
        
        second_profile = InstructorProfile(
            user_id=second_user.id,
            biography='Second instructor biography.',
            title='Instructor',
            is_head_instructor=False
        )
        db.session.add(second_profile)
        db.session.commit()
        
        # Log in as second user
        self.client.get('/logout')
        self.client.post('/login', data={
            'username': 'secondinstructor',
            'password': 'password123'
        }, follow_redirects=True)
        
        # Set second instructor as head instructor
        response = self.client.post('/admin/profile', data={
            'biography': 'Second instructor is now head instructor.',
            'title': 'Head Instructor',
            'is_head_instructor': True
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Verify that first instructor is no longer head instructor
        first_profile = InstructorProfile.query.filter_by(user_id=self.test_user.id).first()
        self.assertFalse(first_profile.is_head_instructor)
        
        # Verify that second instructor is now head instructor
        second_profile = InstructorProfile.query.filter_by(user_id=second_user.id).first()
        self.assertTrue(second_profile.is_head_instructor)
    
    def test_photo_upload_validation(self):
        """Test that photo upload validates file types."""
        # Create initial profile
        self.client.get('/admin/profile')
        
        # Try to upload invalid file type (text file)
        data = {
            'biography': 'Biography with photo upload test.',
            'title': 'Instructor',
            'is_head_instructor': False,
            'photo': (io.BytesIO(b'not an image'), 'test.txt')
        }
        
        response = self.client.post('/admin/profile', 
                                   data=data,
                                   content_type='multipart/form-data',
                                   follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        # Should show error about invalid file type
        self.assertIn(b'Only image files allowed', response.data)
    
    def test_remove_head_instructor_designation(self):
        """Test removing head instructor designation."""
        # Create profile and set as head instructor
        self.client.get('/admin/profile')
        self.client.post('/admin/profile', data={
            'biography': 'Head instructor biography.',
            'title': 'Head Instructor',
            'is_head_instructor': True
        }, follow_redirects=True)
        
        # Remove head instructor designation
        response = self.client.post('/admin/profile', data={
            'biography': 'No longer head instructor.',
            'title': 'Instructor',
            'is_head_instructor': False
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Head Instructor designation removed', response.data)
        
        # Verify in database
        profile = InstructorProfile.query.filter_by(user_id=self.test_user.id).first()
        self.assertFalse(profile.is_head_instructor)
    
    def test_profile_displays_current_info(self):
        """Test that profile page displays current profile information."""
        # Create profile with specific data
        profile = InstructorProfile(
            user_id=self.test_user.id,
            biography='My existing biography.',
            title='Senior Instructor',
            is_head_instructor=False
        )
        db.session.add(profile)
        db.session.commit()
        
        # Access profile page
        response = self.client.get('/admin/profile')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'My existing biography', response.data)
        self.assertIn(b'Senior Instructor', response.data)
        self.assertIn(b'testinstructor', response.data)
        self.assertIn(b'test@example.com', response.data)


if __name__ == '__main__':
    unittest.main()
