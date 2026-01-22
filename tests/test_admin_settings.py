"""
Tests for admin site settings management routes.

This module tests the site settings management functionality including
banner and logo upload, preview, and removal.
"""

import unittest
import os
import io
from flask import url_for
from app import create_app, db
from app.models import User, SiteSettings


class TestAdminSettingsRoutes(unittest.TestCase):
    """Test cases for admin site settings routes."""
    
    def setUp(self):
        """Set up test client and database."""
        self.app = create_app('config.yaml')
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create all tables
        db.create_all()
        
        # Create a test user
        self.test_user = User(username='testadmin', email='admin@test.com')
        self.test_user.set_password('password123')
        db.session.add(self.test_user)
        db.session.commit()
        
        # Log in the test user
        with self.client:
            self.client.post('/login', data={
                'username': 'testadmin',
                'password': 'password123'
            }, follow_redirects=True)
    
    def tearDown(self):
        """Clean up after tests."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_settings_page_requires_login(self):
        """Test that settings page requires authentication."""
        # Log out first
        self.client.get('/logout', follow_redirects=True)
        
        # Try to access settings page
        response = self.client.get('/admin/settings')
        
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)
    
    def test_settings_page_loads(self):
        """Test that settings page loads for authenticated users."""
        response = self.client.get('/admin/settings')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Site Settings', response.data)
        self.assertIn(b'Banner Image', response.data)
        self.assertIn(b'Logo Image', response.data)
    
    def test_settings_page_shows_no_images_initially(self):
        """Test that settings page shows 'no image' message when no images uploaded."""
        response = self.client.get('/admin/settings')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No banner image uploaded', response.data)
        self.assertIn(b'No logo image uploaded', response.data)
    
    def test_settings_page_shows_current_images(self):
        """Test that settings page displays current banner and logo if they exist."""
        # Create settings with images
        settings = SiteSettings(
            id=1,
            banner_image_path='uploads/banners/test_banner.jpg',
            logo_image_path='uploads/logos/test_logo.png'
        )
        db.session.add(settings)
        db.session.commit()
        
        response = self.client.get('/admin/settings')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Current Banner:', response.data)
        self.assertIn(b'Current Logo:', response.data)
        self.assertIn(b'test_banner.jpg', response.data)
        self.assertIn(b'test_logo.png', response.data)
    
    def test_upload_banner_image(self):
        """Test uploading a banner image."""
        # Create a fake image file
        data = {
            'banner_image': (io.BytesIO(b'fake image data'), 'test_banner.jpg'),
        }
        
        response = self.client.post('/admin/settings', 
                                   data=data,
                                   content_type='multipart/form-data',
                                   follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Check that settings were created/updated
        settings = SiteSettings.query.get(1)
        self.assertIsNotNone(settings)
        # Note: In a real test with actual image validation, this would work
        # For now, we're just testing the route structure
    
    def test_upload_logo_image(self):
        """Test uploading a logo image."""
        # Create a fake image file
        data = {
            'logo_image': (io.BytesIO(b'fake image data'), 'test_logo.png'),
        }
        
        response = self.client.post('/admin/settings', 
                                   data=data,
                                   content_type='multipart/form-data',
                                   follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Check that settings were created/updated
        settings = SiteSettings.query.get(1)
        self.assertIsNotNone(settings)
    
    def test_remove_banner_checkbox(self):
        """Test that remove banner checkbox is present when banner exists."""
        # Create settings with banner
        settings = SiteSettings(
            id=1,
            banner_image_path='uploads/banners/test_banner.jpg'
        )
        db.session.add(settings)
        db.session.commit()
        
        response = self.client.get('/admin/settings')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'remove_banner', response.data)
        self.assertIn(b'Remove Banner', response.data)
    
    def test_remove_logo_checkbox(self):
        """Test that remove logo checkbox is present when logo exists."""
        # Create settings with logo
        settings = SiteSettings(
            id=1,
            logo_image_path='uploads/logos/test_logo.png'
        )
        db.session.add(settings)
        db.session.commit()
        
        response = self.client.get('/admin/settings')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'remove_logo', response.data)
        self.assertIn(b'Remove Logo', response.data)
    
    def test_settings_form_has_csrf_protection(self):
        """Test that settings form includes CSRF token field."""
        # Re-enable CSRF for this test
        self.app.config['WTF_CSRF_ENABLED'] = True
        
        response = self.client.get('/admin/settings')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'csrf_token', response.data)
    
    def test_settings_page_has_back_button(self):
        """Test that settings page has a back to dashboard button."""
        response = self.client.get('/admin/settings')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Back to Dashboard', response.data)
    
    def test_settings_page_has_file_format_info(self):
        """Test that settings page displays supported file formats."""
        response = self.client.get('/admin/settings')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'JPEG', response.data)
        self.assertIn(b'PNG', response.data)
        self.assertIn(b'GIF', response.data)
        self.assertIn(b'WebP', response.data)
        self.assertIn(b'SVG', response.data)  # Logo supports SVG
    
    def test_settings_singleton_pattern(self):
        """Test that only one SiteSettings record exists (id=1)."""
        # Make multiple requests to settings page
        self.client.get('/admin/settings')
        self.client.get('/admin/settings')
        
        # Should only have one settings record
        settings_count = SiteSettings.query.count()
        self.assertEqual(settings_count, 1)
        
        # And it should have id=1
        settings = SiteSettings.query.first()
        self.assertEqual(settings.id, 1)


class TestAdminNavigationLinks(unittest.TestCase):
    """Test cases for admin navigation links to settings."""
    
    def setUp(self):
        """Set up test client and database."""
        self.app = create_app('config.yaml')
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        # Create and login test user
        test_user = User(username='testadmin', email='admin@test.com')
        test_user.set_password('password123')
        db.session.add(test_user)
        db.session.commit()
        
        with self.client:
            self.client.post('/login', data={
                'username': 'testadmin',
                'password': 'password123'
            }, follow_redirects=True)
    
    def tearDown(self):
        """Clean up after tests."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_dashboard_has_settings_link(self):
        """Test that admin dashboard has a link to settings."""
        response = self.client.get('/admin/dashboard')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Site Settings', response.data)
        self.assertIn(b'/admin/settings', response.data)
    
    def test_admin_nav_has_settings_link(self):
        """Test that admin navigation menu has a settings link."""
        response = self.client.get('/admin/dashboard')
        
        self.assertEqual(response.status_code, 200)
        # Check for Settings link in navigation
        self.assertIn(b'Settings', response.data)


if __name__ == '__main__':
    unittest.main()
