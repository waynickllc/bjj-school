"""
Unit tests for form classes

Tests the ContactForm and TrialBookingForm validation logic.
"""

import unittest
from werkzeug.datastructures import MultiDict
from app import create_app
from app.forms import ContactForm


class TestContactForm(unittest.TestCase):
    """Test cases for ContactForm"""
    
    def setUp(self):
        """Set up test client and app context"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
    
    def tearDown(self):
        """Clean up after tests"""
        self.app_context.pop()
    
    def test_contact_form_valid_data(self):
        """Test ContactForm with valid data"""
        formdata = MultiDict([
            ('name', 'John Doe'),
            ('email', 'john@example.com'),
            ('phone', '+1234567890'),
            ('message', 'This is a test message with enough characters.')
        ])
        form = ContactForm(formdata=formdata)
        
        self.assertTrue(form.validate())
    
    def test_contact_form_valid_without_phone(self):
        """Test ContactForm with valid data but no phone (optional field)"""
        formdata = MultiDict([
            ('name', 'Jane Smith'),
            ('email', 'jane@example.com'),
            ('phone', ''),
            ('message', 'This is another test message.')
        ])
        form = ContactForm(formdata=formdata)
        
        self.assertTrue(form.validate())
    
    def test_contact_form_missing_name(self):
        """Test ContactForm validation fails when name is missing"""
        formdata = MultiDict([
            ('name', ''),
            ('email', 'test@example.com'),
            ('phone', '+1234567890'),
            ('message', 'This is a test message.')
        ])
        form = ContactForm(formdata=formdata)
        
        self.assertFalse(form.validate())
        self.assertIn('name', form.errors)
        self.assertIn('Name is required', form.errors['name'][0])
    
    def test_contact_form_missing_email(self):
        """Test ContactForm validation fails when email is missing"""
        formdata = MultiDict([
            ('name', 'John Doe'),
            ('email', ''),
            ('phone', '+1234567890'),
            ('message', 'This is a test message.')
        ])
        form = ContactForm(formdata=formdata)
        
        self.assertFalse(form.validate())
        self.assertIn('email', form.errors)
        self.assertIn('Email is required', form.errors['email'][0])
    
    def test_contact_form_invalid_email(self):
        """Test ContactForm validation fails with invalid email format"""
        formdata = MultiDict([
            ('name', 'John Doe'),
            ('email', 'not-an-email'),
            ('phone', '+1234567890'),
            ('message', 'This is a test message.')
        ])
        form = ContactForm(formdata=formdata)
        
        self.assertFalse(form.validate())
        self.assertIn('email', form.errors)
        self.assertIn('Invalid email format', form.errors['email'][0])
    
    def test_contact_form_missing_message(self):
        """Test ContactForm validation fails when message is missing"""
        formdata = MultiDict([
            ('name', 'John Doe'),
            ('email', 'john@example.com'),
            ('phone', '+1234567890'),
            ('message', '')
        ])
        form = ContactForm(formdata=formdata)
        
        self.assertFalse(form.validate())
        self.assertIn('message', form.errors)
        self.assertIn('Message is required', form.errors['message'][0])
    
    def test_contact_form_message_too_short(self):
        """Test ContactForm validation fails when message is too short"""
        formdata = MultiDict([
            ('name', 'John Doe'),
            ('email', 'john@example.com'),
            ('phone', '+1234567890'),
            ('message', 'Short')
        ])
        form = ContactForm(formdata=formdata)
        
        self.assertFalse(form.validate())
        self.assertIn('message', form.errors)
        self.assertIn('Message must be 10-1000 characters', form.errors['message'][0])
    
    def test_contact_form_message_too_long(self):
        """Test ContactForm validation fails when message is too long"""
        formdata = MultiDict([
            ('name', 'John Doe'),
            ('email', 'john@example.com'),
            ('phone', '+1234567890'),
            ('message', 'x' * 1001)  # 1001 characters
        ])
        form = ContactForm(formdata=formdata)
        
        self.assertFalse(form.validate())
        self.assertIn('message', form.errors)
        self.assertIn('Message must be 10-1000 characters', form.errors['message'][0])
    
    def test_contact_form_name_too_short(self):
        """Test ContactForm validation fails when name is too short"""
        formdata = MultiDict([
            ('name', 'A'),
            ('email', 'john@example.com'),
            ('phone', '+1234567890'),
            ('message', 'This is a test message.')
        ])
        form = ContactForm(formdata=formdata)
        
        self.assertFalse(form.validate())
        self.assertIn('name', form.errors)
        self.assertIn('Name must be 2-100 characters', form.errors['name'][0])
    
    def test_contact_form_name_too_long(self):
        """Test ContactForm validation fails when name is too long"""
        formdata = MultiDict([
            ('name', 'x' * 101),  # 101 characters
            ('email', 'john@example.com'),
            ('phone', '+1234567890'),
            ('message', 'This is a test message.')
        ])
        form = ContactForm(formdata=formdata)
        
        self.assertFalse(form.validate())
        self.assertIn('name', form.errors)
        self.assertIn('Name must be 2-100 characters', form.errors['name'][0])
    
    def test_contact_form_invalid_phone_format(self):
        """Test ContactForm validation fails with invalid phone format"""
        invalid_phones = [
            'abc123',  # Contains letters
            '123-456-7890',  # Contains dashes
            '(123) 456-7890',  # Contains parentheses and spaces
            '12345',  # Too few digits (less than 9)
        ]
        
        for phone in invalid_phones:
            formdata = MultiDict([
                ('name', 'John Doe'),
                ('email', 'john@example.com'),
                ('phone', phone),
                ('message', 'This is a test message.')
            ])
            form = ContactForm(formdata=formdata)
            
            self.assertFalse(form.validate(), f"Phone {phone} should be invalid")
            self.assertIn('phone', form.errors)
    
    def test_contact_form_valid_phone_formats(self):
        """Test ContactForm accepts various valid phone formats"""
        valid_phones = [
            '1234567890',  # 10 digits
            '+1234567890',  # With + prefix
            '+11234567890',  # With +1 country code
            '123456789012345',  # 15 digits (max without country code)
            '1234567890123456',  # 16 digits (1 + 15 digits, valid with optional 1)
        ]
        
        for phone in valid_phones:
            formdata = MultiDict([
                ('name', 'John Doe'),
                ('email', 'john@example.com'),
                ('phone', phone),
                ('message', 'This is a test message.')
            ])
            form = ContactForm(formdata=formdata)
            
            self.assertTrue(form.validate(), f"Phone {phone} should be valid")
    
    def test_contact_form_phone_too_short(self):
        """Test ContactForm validation fails when phone has too few digits"""
        formdata = MultiDict([
            ('name', 'John Doe'),
            ('email', 'john@example.com'),
            ('phone', '12345678'),  # Only 8 digits (needs at least 9)
            ('message', 'This is a test message.')
        ])
        form = ContactForm(formdata=formdata)
        
        self.assertFalse(form.validate())
        self.assertIn('phone', form.errors)
    
    def test_contact_form_phone_too_long(self):
        """Test ContactForm validation fails when phone has too many digits"""
        formdata = MultiDict([
            ('name', 'John Doe'),
            ('email', 'john@example.com'),
            ('phone', '+12345678901234567'),  # +1 + 16 digits = too long
            ('message', 'This is a test message.')
        ])
        form = ContactForm(formdata=formdata)
        
        self.assertFalse(form.validate())
        self.assertIn('phone', form.errors)


if __name__ == '__main__':
    unittest.main()


class TestTrialBookingForm(unittest.TestCase):
    """Test cases for TrialBookingForm"""
    
    def setUp(self):
        """Set up test client and app context"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
    
    def tearDown(self):
        """Clean up after tests"""
        self.app_context.pop()
    
    def test_trial_booking_form_valid_data(self):
        """Test TrialBookingForm with valid data"""
        from datetime import date, timedelta
        future_date = date.today() + timedelta(days=7)
        
        formdata = MultiDict([
            ('name', 'John Doe'),
            ('email', 'john@example.com'),
            ('phone', '+1234567890'),
            ('preferred_date', future_date.strftime('%Y-%m-%d')),
            ('preferred_time', 'morning')
        ])
        
        from app.forms import TrialBookingForm
        form = TrialBookingForm(formdata=formdata)
        
        self.assertTrue(form.validate())
    
    def test_trial_booking_form_missing_name(self):
        """Test TrialBookingForm validation fails when name is missing"""
        from datetime import date, timedelta
        future_date = date.today() + timedelta(days=7)
        
        formdata = MultiDict([
            ('name', ''),
            ('email', 'john@example.com'),
            ('phone', '+1234567890'),
            ('preferred_date', future_date.strftime('%Y-%m-%d')),
            ('preferred_time', 'morning')
        ])
        
        from app.forms import TrialBookingForm
        form = TrialBookingForm(formdata=formdata)
        
        self.assertFalse(form.validate())
        self.assertIn('name', form.errors)
        self.assertIn('Name is required', form.errors['name'][0])
    
    def test_trial_booking_form_missing_email(self):
        """Test TrialBookingForm validation fails when email is missing"""
        from datetime import date, timedelta
        future_date = date.today() + timedelta(days=7)
        
        formdata = MultiDict([
            ('name', 'John Doe'),
            ('email', ''),
            ('phone', '+1234567890'),
            ('preferred_date', future_date.strftime('%Y-%m-%d')),
            ('preferred_time', 'morning')
        ])
        
        from app.forms import TrialBookingForm
        form = TrialBookingForm(formdata=formdata)
        
        self.assertFalse(form.validate())
        self.assertIn('email', form.errors)
        self.assertIn('Email is required', form.errors['email'][0])
    
    def test_trial_booking_form_invalid_email(self):
        """Test TrialBookingForm validation fails with invalid email format"""
        from datetime import date, timedelta
        future_date = date.today() + timedelta(days=7)
        
        formdata = MultiDict([
            ('name', 'John Doe'),
            ('email', 'not-an-email'),
            ('phone', '+1234567890'),
            ('preferred_date', future_date.strftime('%Y-%m-%d')),
            ('preferred_time', 'morning')
        ])
        
        from app.forms import TrialBookingForm
        form = TrialBookingForm(formdata=formdata)
        
        self.assertFalse(form.validate())
        self.assertIn('email', form.errors)
        self.assertIn('Invalid email format', form.errors['email'][0])
    
    def test_trial_booking_form_missing_phone(self):
        """Test TrialBookingForm validation fails when phone is missing (required field)"""
        from datetime import date, timedelta
        future_date = date.today() + timedelta(days=7)
        
        formdata = MultiDict([
            ('name', 'John Doe'),
            ('email', 'john@example.com'),
            ('phone', ''),
            ('preferred_date', future_date.strftime('%Y-%m-%d')),
            ('preferred_time', 'morning')
        ])
        
        from app.forms import TrialBookingForm
        form = TrialBookingForm(formdata=formdata)
        
        self.assertFalse(form.validate())
        self.assertIn('phone', form.errors)
        self.assertIn('Phone is required', form.errors['phone'][0])
    
    def test_trial_booking_form_invalid_phone_format(self):
        """Test TrialBookingForm validation fails with invalid phone format"""
        from datetime import date, timedelta
        future_date = date.today() + timedelta(days=7)
        
        invalid_phones = [
            'abc123',  # Contains letters
            '123-456-7890',  # Contains dashes
            '(123) 456-7890',  # Contains parentheses and spaces
            '12345',  # Too few digits (less than 9)
        ]
        
        from app.forms import TrialBookingForm
        for phone in invalid_phones:
            formdata = MultiDict([
                ('name', 'John Doe'),
                ('email', 'john@example.com'),
                ('phone', phone),
                ('preferred_date', future_date.strftime('%Y-%m-%d')),
                ('preferred_time', 'morning')
            ])
            form = TrialBookingForm(formdata=formdata)
            
            self.assertFalse(form.validate(), f"Phone {phone} should be invalid")
            self.assertIn('phone', form.errors)
    
    def test_trial_booking_form_valid_phone_formats(self):
        """Test TrialBookingForm accepts various valid phone formats"""
        from datetime import date, timedelta
        future_date = date.today() + timedelta(days=7)
        
        valid_phones = [
            '1234567890',  # 10 digits
            '+1234567890',  # With + prefix
            '+11234567890',  # With +1 country code
            '123456789012345',  # 15 digits (max without country code)
            '1234567890123456',  # 16 digits (1 + 15 digits, valid with optional 1)
        ]
        
        from app.forms import TrialBookingForm
        for phone in valid_phones:
            formdata = MultiDict([
                ('name', 'John Doe'),
                ('email', 'john@example.com'),
                ('phone', phone),
                ('preferred_date', future_date.strftime('%Y-%m-%d')),
                ('preferred_time', 'morning')
            ])
            form = TrialBookingForm(formdata=formdata)
            
            self.assertTrue(form.validate(), f"Phone {phone} should be valid. Errors: {form.errors}")
    
    def test_trial_booking_form_missing_preferred_date(self):
        """Test TrialBookingForm validation fails when preferred_date is missing"""
        formdata = MultiDict([
            ('name', 'John Doe'),
            ('email', 'john@example.com'),
            ('phone', '+1234567890'),
            ('preferred_date', ''),
            ('preferred_time', 'morning')
        ])
        
        from app.forms import TrialBookingForm
        form = TrialBookingForm(formdata=formdata)
        
        self.assertFalse(form.validate())
        self.assertIn('preferred_date', form.errors)
    
    def test_trial_booking_form_missing_preferred_time(self):
        """Test TrialBookingForm validation fails when preferred_time is missing"""
        from datetime import date, timedelta
        future_date = date.today() + timedelta(days=7)
        
        formdata = MultiDict([
            ('name', 'John Doe'),
            ('email', 'john@example.com'),
            ('phone', '+1234567890'),
            ('preferred_date', future_date.strftime('%Y-%m-%d')),
            ('preferred_time', '')
        ])
        
        from app.forms import TrialBookingForm
        form = TrialBookingForm(formdata=formdata)
        
        self.assertFalse(form.validate())
        self.assertIn('preferred_time', form.errors)
    
    def test_trial_booking_form_valid_time_choices(self):
        """Test TrialBookingForm accepts all valid time choices"""
        from datetime import date, timedelta
        future_date = date.today() + timedelta(days=7)
        
        valid_times = ['morning', 'afternoon', 'evening']
        
        from app.forms import TrialBookingForm
        for time_choice in valid_times:
            formdata = MultiDict([
                ('name', 'John Doe'),
                ('email', 'john@example.com'),
                ('phone', '+1234567890'),
                ('preferred_date', future_date.strftime('%Y-%m-%d')),
                ('preferred_time', time_choice)
            ])
            form = TrialBookingForm(formdata=formdata)
            
            self.assertTrue(form.validate(), f"Time choice {time_choice} should be valid. Errors: {form.errors}")
    
    def test_trial_booking_form_invalid_time_choice(self):
        """Test TrialBookingForm validation fails with invalid time choice"""
        from datetime import date, timedelta
        future_date = date.today() + timedelta(days=7)
        
        formdata = MultiDict([
            ('name', 'John Doe'),
            ('email', 'john@example.com'),
            ('phone', '+1234567890'),
            ('preferred_date', future_date.strftime('%Y-%m-%d')),
            ('preferred_time', 'invalid_time')
        ])
        
        from app.forms import TrialBookingForm
        form = TrialBookingForm(formdata=formdata)
        
        self.assertFalse(form.validate())
        self.assertIn('preferred_time', form.errors)
    
    def test_trial_booking_form_name_length_validation(self):
        """Test TrialBookingForm name length validation"""
        from datetime import date, timedelta
        future_date = date.today() + timedelta(days=7)
        
        from app.forms import TrialBookingForm
        
        # Test name too short
        formdata = MultiDict([
            ('name', 'A'),
            ('email', 'john@example.com'),
            ('phone', '+1234567890'),
            ('preferred_date', future_date.strftime('%Y-%m-%d')),
            ('preferred_time', 'morning')
        ])
        form = TrialBookingForm(formdata=formdata)
        self.assertFalse(form.validate())
        self.assertIn('name', form.errors)
        self.assertIn('Name must be 2-100 characters', form.errors['name'][0])
        
        # Test name too long
        formdata = MultiDict([
            ('name', 'x' * 101),
            ('email', 'john@example.com'),
            ('phone', '+1234567890'),
            ('preferred_date', future_date.strftime('%Y-%m-%d')),
            ('preferred_time', 'morning')
        ])
        form = TrialBookingForm(formdata=formdata)
        self.assertFalse(form.validate())
        self.assertIn('name', form.errors)
        self.assertIn('Name must be 2-100 characters', form.errors['name'][0])
