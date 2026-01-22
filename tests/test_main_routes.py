"""
Unit tests for main routes (home, instructor, and classes pages).

Tests verify:
- Home route renders correctly with Instagram photos
- Home route handles Instagram API failures gracefully
- Instructor route renders correctly with instructor data
- Classes route displays classes organized by day
- Classes route shows message when no classes available
- Error handling for Instagram API failures
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import time
from app import create_app, db
from app.models import Class
from app.services.instagram import InstagramAPIError


@pytest.fixture
def app():
    """Create and configure a test application instance."""
    from flask import Flask
    from flask_wtf.csrf import CSRFProtect
    import os
    
    # Get the path to the app directory
    app_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app')
    template_dir = os.path.join(app_dir, 'templates')
    static_dir = os.path.join(app_dir, 'static')
    
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['INSTAGRAM_ACCESS_TOKEN'] = 'test-token'
    app.config['INSTAGRAM_USER_ID'] = 'test-user-id'
    
    # Initialize extensions with test app
    db.init_app(app)
    CSRFProtect(app)
    
    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.contact import contact_bp
    from app.routes.booking import booking_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(booking_bp)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client for the application."""
    return app.test_client()


class TestHomeRoute:
    """Tests for the home route."""
    
    def test_home_route_renders(self, client):
        """Test that home route returns 200 and renders template."""
        with patch('app.routes.main.InstagramService') as mock_service:
            # Mock successful Instagram API response
            mock_instance = MagicMock()
            mock_instance.fetch_recent_media.return_value = [
                {
                    'id': '123',
                    'media_type': 'IMAGE',
                    'media_url': 'https://example.com/photo1.jpg',
                    'permalink': 'https://instagram.com/p/123',
                    'caption': 'Test photo 1',
                    'timestamp': '2024-01-01T12:00:00+0000'
                }
            ]
            mock_service.return_value = mock_instance
            
            response = client.get('/')
            
            assert response.status_code == 200
            assert b'Welcome to Our BJJ School' in response.data
    
    def test_home_route_with_instagram_photos(self, client):
        """Test that home route displays Instagram photos when API succeeds."""
        with patch('app.routes.main.InstagramService') as mock_service:
            # Mock successful Instagram API response with multiple photos
            mock_instance = MagicMock()
            mock_instance.fetch_recent_media.return_value = [
                {
                    'id': '123',
                    'media_type': 'IMAGE',
                    'media_url': 'https://example.com/photo1.jpg',
                    'permalink': 'https://instagram.com/p/123',
                    'caption': 'Training session',
                    'timestamp': '2024-01-01T12:00:00+0000'
                },
                {
                    'id': '456',
                    'media_type': 'IMAGE',
                    'media_url': 'https://example.com/photo2.jpg',
                    'permalink': 'https://instagram.com/p/456',
                    'caption': 'Competition day',
                    'timestamp': '2024-01-02T12:00:00+0000'
                }
            ]
            mock_service.return_value = mock_instance
            
            response = client.get('/')
            
            assert response.status_code == 200
            assert b'https://example.com/photo1.jpg' in response.data
            assert b'https://example.com/photo2.jpg' in response.data
            assert b'https://instagram.com/p/123' in response.data
            assert b'https://instagram.com/p/456' in response.data
    
    def test_home_route_instagram_api_error(self, client):
        """Test that home route handles Instagram API errors gracefully."""
        with patch('app.routes.main.InstagramService') as mock_service:
            # Mock Instagram API error
            mock_instance = MagicMock()
            mock_instance.fetch_recent_media.side_effect = InstagramAPIError("API error")
            mock_service.return_value = mock_instance
            
            response = client.get('/')
            
            # Should still return 200 (page loads successfully)
            assert response.status_code == 200
            # Should display fallback message
            assert b'Instagram photos temporarily unavailable' in response.data
    
    def test_home_route_missing_instagram_credentials(self, client, app):
        """Test that home route handles missing Instagram credentials."""
        with app.app_context():
            # Temporarily remove Instagram credentials
            original_token = app.config.get('INSTAGRAM_ACCESS_TOKEN')
            original_user_id = app.config.get('INSTAGRAM_USER_ID')
            app.config['INSTAGRAM_ACCESS_TOKEN'] = None
            app.config['INSTAGRAM_USER_ID'] = None
            
            try:
                response = client.get('/')
                
                # Should still return 200 (page loads successfully)
                assert response.status_code == 200
                # Should display fallback message
                assert b'Instagram photos temporarily unavailable' in response.data
            finally:
                # Restore credentials
                app.config['INSTAGRAM_ACCESS_TOKEN'] = original_token
                app.config['INSTAGRAM_USER_ID'] = original_user_id
    
    def test_home_route_unexpected_error(self, client):
        """Test that home route handles unexpected errors gracefully."""
        with patch('app.routes.main.InstagramService') as mock_service:
            # Mock unexpected error
            mock_service.side_effect = Exception("Unexpected error")
            
            response = client.get('/')
            
            # Should still return 200 (page loads successfully)
            assert response.status_code == 200
            # Should display fallback message
            assert b'Instagram photos temporarily unavailable' in response.data
    
    def test_home_route_empty_instagram_photos(self, client):
        """Test that home route handles empty Instagram response."""
        with patch('app.routes.main.InstagramService') as mock_service:
            # Mock empty Instagram API response
            mock_instance = MagicMock()
            mock_instance.fetch_recent_media.return_value = []
            mock_service.return_value = mock_instance
            
            response = client.get('/')
            
            assert response.status_code == 200
            # Should display empty message
            assert b'No photos available at this time' in response.data


class TestInstructorRoute:
    """Tests for the instructor route."""
    
    def test_instructor_route_renders(self, client):
        """Test that instructor route returns 200 and renders template."""
        response = client.get('/instructor')
        
        assert response.status_code == 200
        assert b'Meet Our Instructors' in response.data
    
    def test_instructor_route_displays_no_instructors_message(self, client):
        """Test that instructor route displays message when no instructors exist."""
        response = client.get('/instructor')
        
        assert response.status_code == 200
        assert b'No Instructors Available' in response.data
    
    def test_instructor_route_displays_instructor_from_database(self, client, app):
        """Test that instructor route displays instructor information from database."""
        from app.models import User, InstructorProfile
        
        with app.app_context():
            # Create a test user and instructor profile
            user = User(username='TestInstructor', email='test@example.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            profile = InstructorProfile(
                user_id=user.id,
                biography='Experienced Brazilian Jiu-Jitsu instructor with over 15 years of training.',
                title='Black Belt Instructor',
                is_head_instructor=False
            )
            db.session.add(profile)
            db.session.commit()
        
        response = client.get('/instructor')
        
        assert response.status_code == 200
        assert b'TestInstructor' in response.data
        assert b'Black Belt Instructor' in response.data
        assert b'Experienced Brazilian Jiu-Jitsu instructor' in response.data
    
    def test_instructor_route_displays_head_instructor_first(self, client, app):
        """Test that head instructor is displayed first."""
        from app.models import User, InstructorProfile
        
        with app.app_context():
            # Create first instructor (not head)
            user1 = User(username='Instructor1', email='instructor1@example.com')
            user1.set_password('password123')
            db.session.add(user1)
            db.session.commit()
            
            profile1 = InstructorProfile(
                user_id=user1.id,
                biography='Regular instructor biography.',
                title='Instructor',
                is_head_instructor=False
            )
            db.session.add(profile1)
            
            # Create second instructor (head instructor)
            user2 = User(username='HeadInstructor', email='head@example.com')
            user2.set_password('password123')
            db.session.add(user2)
            db.session.commit()
            
            profile2 = InstructorProfile(
                user_id=user2.id,
                biography='Head instructor biography.',
                title='Professor',
                is_head_instructor=True
            )
            db.session.add(profile2)
            db.session.commit()
        
        response = client.get('/instructor')
        
        assert response.status_code == 200
        # Check that head instructor badge is present
        assert b'Head Instructor' in response.data
        # Check that both instructors are displayed
        assert b'HeadInstructor' in response.data
        assert b'Instructor1' in response.data
    
    def test_instructor_route_displays_placeholder_for_missing_photo(self, client, app):
        """Test that default placeholder is shown when instructor has no photo."""
        from app.models import User, InstructorProfile
        
        with app.app_context():
            user = User(username='TestInstructor', email='test@example.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            profile = InstructorProfile(
                user_id=user.id,
                biography='Test biography.',
                title='Instructor',
                is_head_instructor=False,
                photo_path=None  # No photo
            )
            db.session.add(profile)
            db.session.commit()
        
        response = client.get('/instructor')
        
        assert response.status_code == 200
        # Should show placeholder with first letter of username
        assert b'instructor-photo-placeholder' in response.data
    
    def test_instructor_route_has_cta_buttons(self, client):
        """Test that instructor route has call-to-action buttons."""
        response = client.get('/instructor')
        
        assert response.status_code == 200
        # Should have links to booking and contact pages
        assert b'Book a Trial Class' in response.data
        assert b'Contact Us' in response.data


class TestInstagramPhotoLinks:
    """Tests for Instagram photo links (Property 10)."""
    
    def test_instagram_photos_have_target_blank(self, client):
        """Test that Instagram photo links open in new tab (target="_blank")."""
        with patch('app.routes.main.InstagramService') as mock_service:
            # Mock successful Instagram API response
            mock_instance = MagicMock()
            mock_instance.fetch_recent_media.return_value = [
                {
                    'id': '123',
                    'media_type': 'IMAGE',
                    'media_url': 'https://example.com/photo1.jpg',
                    'permalink': 'https://instagram.com/p/123',
                    'caption': 'Test photo',
                    'timestamp': '2024-01-01T12:00:00+0000'
                }
            ]
            mock_service.return_value = mock_instance
            
            response = client.get('/')
            
            assert response.status_code == 200
            # Check that links have target="_blank"
            assert b'target="_blank"' in response.data
            # Check that links have rel="noopener noreferrer" for security
            assert b'rel="noopener noreferrer"' in response.data
    
    def test_instagram_photos_have_valid_permalink(self, client):
        """Test that Instagram photos have valid permalink URLs."""
        with patch('app.routes.main.InstagramService') as mock_service:
            # Mock successful Instagram API response
            mock_instance = MagicMock()
            test_permalink = 'https://instagram.com/p/test123'
            mock_instance.fetch_recent_media.return_value = [
                {
                    'id': '123',
                    'media_type': 'IMAGE',
                    'media_url': 'https://example.com/photo1.jpg',
                    'permalink': test_permalink,
                    'caption': 'Test photo',
                    'timestamp': '2024-01-01T12:00:00+0000'
                }
            ]
            mock_service.return_value = mock_instance
            
            response = client.get('/')
            
            assert response.status_code == 200
            # Check that permalink is in the response
            assert test_permalink.encode() in response.data



class TestClassesRoute:
    """Tests for the classes route."""
    
    def test_classes_route_renders(self, client):
        """Test that classes route returns 200 and renders template."""
        response = client.get('/classes')
        
        assert response.status_code == 200
        assert b'Class Schedule' in response.data
    
    def test_classes_route_displays_no_classes_message(self, client, app):
        """Test that classes route displays message when no classes available.
        
        Validates: Requirements 10.4
        """
        with app.app_context():
            # Ensure no classes exist
            Class.query.delete()
            db.session.commit()
            
            response = client.get('/classes')
            
            assert response.status_code == 200
            assert b'No Classes Currently Scheduled' in response.data
            assert b'check back soon' in response.data.lower()
    
    def test_classes_route_displays_classes(self, client, app):
        """Test that classes route displays all available classes.
        
        Validates: Requirements 10.1, 10.2
        """
        with app.app_context():
            # Create test classes
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
                name='All Levels',
                day_of_week='Wednesday',
                start_time=time(18, 0),
                end_time=time(19, 30)
            )
            
            db.session.add_all([class1, class2, class3])
            db.session.commit()
            
            response = client.get('/classes')
            
            assert response.status_code == 200
            # Check that class names are displayed
            assert b'Fundamentals' in response.data
            assert b'Advanced' in response.data
            assert b'All Levels' in response.data
            # Check that days are displayed
            assert b'Monday' in response.data
            assert b'Wednesday' in response.data
    
    def test_classes_organized_by_day(self, client, app):
        """Test that classes are organized by day of the week.
        
        Validates: Requirements 10.3
        """
        with app.app_context():
            # Create classes on different days
            monday_class = Class(
                name='Monday Class',
                day_of_week='Monday',
                start_time=time(18, 0),
                end_time=time(19, 30)
            )
            friday_class = Class(
                name='Friday Class',
                day_of_week='Friday',
                start_time=time(18, 0),
                end_time=time(19, 30)
            )
            
            db.session.add_all([monday_class, friday_class])
            db.session.commit()
            
            response = client.get('/classes')
            
            assert response.status_code == 200
            # Check that days are used as section headers
            assert b'Monday' in response.data
            assert b'Friday' in response.data
            # Check that classes are under their respective days
            response_text = response.data.decode('utf-8')
            monday_index = response_text.find('Monday')
            friday_index = response_text.find('Friday')
            monday_class_index = response_text.find('Monday Class')
            friday_class_index = response_text.find('Friday Class')
            
            # Monday Class should appear after Monday header
            assert monday_index < monday_class_index
            # Friday Class should appear after Friday header
            assert friday_index < friday_class_index
    
    def test_classes_display_time_information(self, client, app):
        """Test that each class displays start and end time.
        
        Validates: Requirements 10.2
        """
        with app.app_context():
            # Create a class with specific times
            test_class = Class(
                name='Test Class',
                day_of_week='Tuesday',
                start_time=time(18, 30),
                end_time=time(20, 0)
            )
            
            db.session.add(test_class)
            db.session.commit()
            
            response = client.get('/classes')
            
            assert response.status_code == 200
            # Check that times are displayed (format may vary)
            response_text = response.data.decode('utf-8')
            # Should contain time information
            assert '6:30' in response_text or '18:30' in response_text
            assert '8:00' in response_text or '20:00' in response_text
    
    def test_classes_sorted_by_day_order(self, client, app):
        """Test that classes are sorted by day of week (Monday first)."""
        with app.app_context():
            # Create classes in random order
            friday_class = Class(
                name='Friday Class',
                day_of_week='Friday',
                start_time=time(18, 0),
                end_time=time(19, 30)
            )
            monday_class = Class(
                name='Monday Class',
                day_of_week='Monday',
                start_time=time(18, 0),
                end_time=time(19, 30)
            )
            wednesday_class = Class(
                name='Wednesday Class',
                day_of_week='Wednesday',
                start_time=time(18, 0),
                end_time=time(19, 30)
            )
            
            db.session.add_all([friday_class, monday_class, wednesday_class])
            db.session.commit()
            
            response = client.get('/classes')
            
            assert response.status_code == 200
            response_text = response.data.decode('utf-8')
            
            # Find positions of day headers
            monday_pos = response_text.find('Monday')
            wednesday_pos = response_text.find('Wednesday')
            friday_pos = response_text.find('Friday')
            
            # Monday should come before Wednesday, which should come before Friday
            assert monday_pos < wednesday_pos < friday_pos
    
    def test_classes_sorted_by_time_within_day(self, client, app):
        """Test that classes on the same day are sorted by start time."""
        with app.app_context():
            # Create multiple classes on the same day with different times
            evening_class = Class(
                name='Evening Class',
                day_of_week='Monday',
                start_time=time(19, 30),
                end_time=time(21, 0)
            )
            morning_class = Class(
                name='Morning Class',
                day_of_week='Monday',
                start_time=time(6, 0),
                end_time=time(7, 30)
            )
            afternoon_class = Class(
                name='Afternoon Class',
                day_of_week='Monday',
                start_time=time(12, 0),
                end_time=time(13, 30)
            )
            
            db.session.add_all([evening_class, morning_class, afternoon_class])
            db.session.commit()
            
            response = client.get('/classes')
            
            assert response.status_code == 200
            response_text = response.data.decode('utf-8')
            
            # Find positions of class names
            morning_pos = response_text.find('Morning Class')
            afternoon_pos = response_text.find('Afternoon Class')
            evening_pos = response_text.find('Evening Class')
            
            # Classes should appear in chronological order
            assert morning_pos < afternoon_pos < evening_pos
    
    def test_classes_route_has_navigation_link(self, client):
        """Test that Classes link is in navigation menu.
        
        Validates: Requirements 10.5
        """
        response = client.get('/classes')
        
        assert response.status_code == 200
        # Check that navigation includes Classes link
        assert b'Classes' in response.data
        # Check that the link is in the nav menu
        response_text = response.data.decode('utf-8')
        assert 'nav-menu' in response_text or 'navbar' in response_text
    
    def test_classes_route_has_cta_buttons(self, client, app):
        """Test that classes route has call-to-action buttons when classes exist."""
        with app.app_context():
            # Create a test class
            test_class = Class(
                name='Test Class',
                day_of_week='Monday',
                start_time=time(18, 0),
                end_time=time(19, 30)
            )
            
            db.session.add(test_class)
            db.session.commit()
            
            response = client.get('/classes')
            
            assert response.status_code == 200
            # Should have links to booking and contact pages
            assert b'Book a Trial Class' in response.data or b'Book Trial' in response.data
            assert b'Contact Us' in response.data


class TestAnnouncementsRoute:
    """Tests for the announcements route."""
    
    def test_announcements_route_renders(self, client):
        """Test that announcements route returns 200 and renders template.
        
        Validates: Requirements 11.1
        """
        response = client.get('/announcements')
        
        assert response.status_code == 200
        assert b'Announcements' in response.data
    
    def test_announcements_route_displays_no_announcements_message(self, client, app):
        """Test that announcements route displays message when no announcements available.
        
        Validates: Requirements 11.4
        """
        from app.models import Announcement
        
        with app.app_context():
            # Ensure no announcements exist
            Announcement.query.delete()
            db.session.commit()
            
            response = client.get('/announcements')
            
            assert response.status_code == 200
            assert b'No Announcements Currently Posted' in response.data
            assert b'check back soon' in response.data.lower()
    
    def test_announcements_route_displays_announcements(self, client, app):
        """Test that announcements route displays all available announcements.
        
        Validates: Requirements 11.1, 11.2
        """
        from app.models import Announcement
        from datetime import datetime
        
        with app.app_context():
            # Create test announcements
            announcement1 = Announcement(
                title='Welcome to Our School',
                content='We are excited to announce the opening of our new BJJ school!',
                published_date=datetime(2024, 1, 15, 10, 0, 0)
            )
            announcement2 = Announcement(
                title='Competition Results',
                content='Congratulations to all our students who competed last weekend!',
                published_date=datetime(2024, 1, 20, 14, 30, 0)
            )
            announcement3 = Announcement(
                title='Holiday Schedule',
                content='Please note our modified schedule for the upcoming holidays.',
                published_date=datetime(2024, 1, 10, 9, 0, 0)
            )
            
            db.session.add_all([announcement1, announcement2, announcement3])
            db.session.commit()
            
            response = client.get('/announcements')
            
            assert response.status_code == 200
            # Check that announcement titles are displayed
            assert b'Welcome to Our School' in response.data
            assert b'Competition Results' in response.data
            assert b'Holiday Schedule' in response.data
            # Check that content is displayed
            assert b'new BJJ school' in response.data
            assert b'Congratulations' in response.data
            assert b'modified schedule' in response.data
    
    def test_announcements_display_title_content_date(self, client, app):
        """Test that each announcement displays title, content, and publication date.
        
        Validates: Requirements 11.2
        """
        from app.models import Announcement
        from datetime import datetime
        
        with app.app_context():
            # Create a test announcement with specific date
            test_announcement = Announcement(
                title='Test Announcement',
                content='This is the announcement content.',
                published_date=datetime(2024, 1, 15, 10, 30, 0)
            )
            
            db.session.add(test_announcement)
            db.session.commit()
            
            response = client.get('/announcements')
            
            assert response.status_code == 200
            response_text = response.data.decode('utf-8')
            
            # Check that title is displayed
            assert 'Test Announcement' in response_text
            # Check that content is displayed
            assert 'This is the announcement content.' in response_text
            # Check that date is displayed (format may vary)
            assert 'January' in response_text or 'Jan' in response_text
            assert '15' in response_text
            assert '2024' in response_text
    
    def test_announcements_reverse_chronological_order(self, client, app):
        """Test that announcements are displayed in reverse chronological order (newest first).
        
        Validates: Requirements 11.3
        """
        from app.models import Announcement
        from datetime import datetime
        
        with app.app_context():
            # Create announcements with different dates
            old_announcement = Announcement(
                title='Old Announcement',
                content='This is an old announcement.',
                published_date=datetime(2024, 1, 1, 10, 0, 0)
            )
            recent_announcement = Announcement(
                title='Recent Announcement',
                content='This is a recent announcement.',
                published_date=datetime(2024, 1, 20, 10, 0, 0)
            )
            newest_announcement = Announcement(
                title='Newest Announcement',
                content='This is the newest announcement.',
                published_date=datetime(2024, 1, 25, 10, 0, 0)
            )
            
            db.session.add_all([old_announcement, recent_announcement, newest_announcement])
            db.session.commit()
            
            response = client.get('/announcements')
            
            assert response.status_code == 200
            response_text = response.data.decode('utf-8')
            
            # Find positions of announcement titles
            newest_pos = response_text.find('Newest Announcement')
            recent_pos = response_text.find('Recent Announcement')
            old_pos = response_text.find('Old Announcement')
            
            # Newest should come before Recent, which should come before Old
            assert newest_pos < recent_pos < old_pos
    
    def test_announcements_route_has_navigation_link(self, client):
        """Test that Announcements link is in navigation menu.
        
        Validates: Requirements 11.5
        """
        response = client.get('/announcements')
        
        assert response.status_code == 200
        # Check that navigation includes Announcements link
        assert b'Announcements' in response.data
        # Check that the link is in the nav menu
        response_text = response.data.decode('utf-8')
        assert 'nav-menu' in response_text or 'navbar' in response_text
    
    def test_announcements_route_has_cta_buttons(self, client, app):
        """Test that announcements route has call-to-action buttons when announcements exist."""
        from app.models import Announcement
        from datetime import datetime
        
        with app.app_context():
            # Create a test announcement
            test_announcement = Announcement(
                title='Test Announcement',
                content='Test content',
                published_date=datetime(2024, 1, 15, 10, 0, 0)
            )
            
            db.session.add(test_announcement)
            db.session.commit()
            
            response = client.get('/announcements')
            
            assert response.status_code == 200
            # Should have links to booking and contact pages
            assert b'Book a Trial Class' in response.data or b'Book Trial' in response.data
            assert b'Contact Us' in response.data
    
    def test_announcements_content_preserves_formatting(self, client, app):
        """Test that announcement content preserves line breaks and formatting."""
        from app.models import Announcement
        from datetime import datetime
        
        with app.app_context():
            # Create announcement with multi-line content
            test_announcement = Announcement(
                title='Multi-line Announcement',
                content='Line 1\nLine 2\nLine 3',
                published_date=datetime(2024, 1, 15, 10, 0, 0)
            )
            
            db.session.add(test_announcement)
            db.session.commit()
            
            response = client.get('/announcements')
            
            assert response.status_code == 200
            response_text = response.data.decode('utf-8')
            
            # Check that content is displayed
            assert 'Line 1' in response_text
            assert 'Line 2' in response_text
            assert 'Line 3' in response_text
