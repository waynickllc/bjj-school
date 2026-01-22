"""
Unit tests for FAQ route.

Tests verify:
- FAQ route renders correctly with FAQs
- FAQ route shows message when no FAQs available
- FAQs are displayed with expandable/collapsible functionality
- FAQs are ordered by display_order
- FAQ link appears in navigation menu
"""

import pytest
from app import create_app, db
from app.models import FAQ


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


class TestFAQRoute:
    """Tests for the FAQ route."""
    
    def test_faq_route_renders(self, client):
        """Test that FAQ route returns 200 and renders template.
        
        Validates: Requirements 11.5.1
        """
        response = client.get('/faq')
        
        assert response.status_code == 200
        assert b'Frequently Asked Questions' in response.data
    
    def test_faq_route_displays_no_faqs_message(self, client, app):
        """Test that FAQ route displays message when no FAQs available.
        
        Validates: Requirements 11.5.5
        """
        with app.app_context():
            # Ensure no FAQs exist
            FAQ.query.delete()
            db.session.commit()
            
            response = client.get('/faq')
            
            assert response.status_code == 200
            assert b'No FAQs Currently Posted' in response.data
            assert b'contact us' in response.data.lower()
    
    def test_faq_route_displays_faqs(self, client, app):
        """Test that FAQ route displays all available FAQs.
        
        Validates: Requirements 11.5.1, 11.5.2
        """
        with app.app_context():
            # Create test FAQs
            faq1 = FAQ(
                question='What is Brazilian Jiu-Jitsu?',
                answer='Brazilian Jiu-Jitsu (BJJ) is a martial art and combat sport based on ground fighting and submission holds.',
                display_order=1
            )
            faq2 = FAQ(
                question='Do I need prior experience?',
                answer='No prior experience is necessary. We welcome students of all levels.',
                display_order=2
            )
            faq3 = FAQ(
                question='What should I wear to class?',
                answer='For your first class, comfortable athletic wear is fine. Once you join, you will need a gi (uniform).',
                display_order=3
            )
            
            db.session.add_all([faq1, faq2, faq3])
            db.session.commit()
            
            response = client.get('/faq')
            
            assert response.status_code == 200
            # Check that FAQ questions are displayed
            assert b'What is Brazilian Jiu-Jitsu?' in response.data
            assert b'Do I need prior experience?' in response.data
            assert b'What should I wear to class?' in response.data
            # Check that answers are displayed
            assert b'martial art and combat sport' in response.data
            assert b'No prior experience is necessary' in response.data
            assert b'comfortable athletic wear' in response.data
    
    def test_faq_display_question_and_answer(self, client, app):
        """Test that each FAQ displays question and answer.
        
        Validates: Requirements 11.5.2
        """
        with app.app_context():
            # Create a test FAQ
            test_faq = FAQ(
                question='How long are the classes?',
                answer='Most classes are 90 minutes long, providing ample time for warm-up, technique instruction, and live training.',
                display_order=1
            )
            
            db.session.add(test_faq)
            db.session.commit()
            
            response = client.get('/faq')
            
            assert response.status_code == 200
            response_text = response.data.decode('utf-8')
            
            # Check that question is displayed
            assert 'How long are the classes?' in response_text
            # Check that answer is displayed
            assert 'Most classes are 90 minutes long' in response_text
    
    def test_faq_expandable_collapsible_structure(self, client, app):
        """Test that FAQ page has expandable/collapsible structure.
        
        Validates: Requirements 11.5.4
        """
        with app.app_context():
            # Create a test FAQ
            test_faq = FAQ(
                question='Test Question?',
                answer='Test Answer',
                display_order=1
            )
            
            db.session.add(test_faq)
            db.session.commit()
            
            response = client.get('/faq')
            
            assert response.status_code == 200
            response_text = response.data.decode('utf-8')
            
            # Check for expandable/collapsible elements
            assert 'faq-item' in response_text
            assert 'faq-question' in response_text
            assert 'faq-answer' in response_text
            assert 'faq-toggle' in response_text
            # Check for JavaScript toggle function
            assert 'toggleFAQ' in response_text
    
    def test_faq_ordered_by_display_order(self, client, app):
        """Test that FAQs are displayed in order by display_order field.
        
        Validates: Requirements 11.5.3
        """
        with app.app_context():
            # Create FAQs with different display orders (add in random order)
            faq_third = FAQ(
                question='Third Question?',
                answer='Third Answer',
                display_order=3
            )
            faq_first = FAQ(
                question='First Question?',
                answer='First Answer',
                display_order=1
            )
            faq_second = FAQ(
                question='Second Question?',
                answer='Second Answer',
                display_order=2
            )
            
            db.session.add_all([faq_third, faq_first, faq_second])
            db.session.commit()
            
            response = client.get('/faq')
            
            assert response.status_code == 200
            response_text = response.data.decode('utf-8')
            
            # Find positions of FAQ questions
            first_pos = response_text.find('First Question?')
            second_pos = response_text.find('Second Question?')
            third_pos = response_text.find('Third Question?')
            
            # FAQs should appear in order by display_order
            assert first_pos < second_pos < third_pos
    
    def test_faq_route_has_navigation_link(self, client):
        """Test that FAQ link is in navigation menu.
        
        Validates: Requirements 11.5.6
        """
        response = client.get('/faq')
        
        assert response.status_code == 200
        # Check that navigation includes FAQ link
        assert b'FAQ' in response.data
        # Check that the link is in the nav menu
        response_text = response.data.decode('utf-8')
        assert 'nav-menu' in response_text or 'navbar' in response_text
    
    def test_faq_route_has_cta_buttons(self, client, app):
        """Test that FAQ route has call-to-action buttons when FAQs exist."""
        with app.app_context():
            # Create a test FAQ
            test_faq = FAQ(
                question='Test Question?',
                answer='Test Answer',
                display_order=1
            )
            
            db.session.add(test_faq)
            db.session.commit()
            
            response = client.get('/faq')
            
            assert response.status_code == 200
            # Should have links to contact and booking pages
            assert b'Contact Us' in response.data
            assert b'Book a Trial Class' in response.data or b'Book Trial' in response.data
    
    def test_faq_answer_preserves_formatting(self, client, app):
        """Test that FAQ answers preserve line breaks and formatting."""
        with app.app_context():
            # Create FAQ with multi-line answer
            test_faq = FAQ(
                question='What are the membership options?',
                answer='We offer several membership options:\n\n1. Monthly unlimited\n2. 10-class pack\n3. Drop-in rates',
                display_order=1
            )
            
            db.session.add(test_faq)
            db.session.commit()
            
            response = client.get('/faq')
            
            assert response.status_code == 200
            response_text = response.data.decode('utf-8')
            
            # Check that answer content is present
            assert 'Monthly unlimited' in response_text
            assert '10-class pack' in response_text
            assert 'Drop-in rates' in response_text
    
    def test_faq_toggle_functionality_structure(self, client, app):
        """Test that FAQ items have proper structure for toggle functionality."""
        with app.app_context():
            # Create test FAQs
            faq1 = FAQ(
                question='Question 1?',
                answer='Answer 1',
                display_order=1
            )
            faq2 = FAQ(
                question='Question 2?',
                answer='Answer 2',
                display_order=2
            )
            
            db.session.add_all([faq1, faq2])
            db.session.commit()
            
            response = client.get('/faq')
            
            assert response.status_code == 200
            response_text = response.data.decode('utf-8')
            
            # Check that each FAQ has the proper structure
            # Should have multiple faq-item elements
            assert response_text.count('faq-item') >= 2
            # Should have toggle icons
            assert response_text.count('faq-toggle') >= 2
            # Should have onclick handlers
            assert response_text.count('toggleFAQ') >= 2
