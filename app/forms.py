"""
Form Classes

This module defines Flask-WTF form classes for the BJJ school website.
Forms will be implemented in task 3.
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DateField, SelectField, SubmitField, PasswordField, TimeField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Email, Length, Optional, Regexp


class ContactForm(FlaskForm):
    """Contact form with validation
    
    Implements Requirements 2.1 (contact form fields) and 2.7 (Flask-WTF implementation).
    CSRF protection is automatically enabled by Flask-WTF.
    """
    name = StringField('Name', validators=[
        DataRequired(message='Name is required'),
        Length(min=2, max=100, message='Name must be 2-100 characters')
    ])
    
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email format'),
        Length(max=120)
    ])
    
    phone = StringField('Phone', validators=[
        Optional(),
        Regexp(r'^\+?1?\d{9,15}$', message='Invalid phone format')
    ])
    
    message = TextAreaField('Message', validators=[
        DataRequired(message='Message is required'),
        Length(min=10, max=1000, message='Message must be 10-1000 characters')
    ])
    
    submit = SubmitField('Send Message')


class TrialBookingForm(FlaskForm):
    """Trial booking form with validation
    
    Implements Requirements 3.1 (trial booking form fields) and 3.7 (Flask-WTF implementation).
    CSRF protection is automatically enabled by Flask-WTF.
    """
    name = StringField('Name', validators=[
        DataRequired(message='Name is required'),
        Length(min=2, max=100, message='Name must be 2-100 characters')
    ])
    
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email format'),
        Length(max=120)
    ])
    
    phone = StringField('Phone', validators=[
        DataRequired(message='Phone is required'),
        Regexp(r'^\+?1?\d{9,15}$', message='Invalid phone format')
    ])
    
    preferred_date = DateField('Preferred Date', validators=[
        DataRequired(message='Preferred date is required')
    ])
    
    preferred_time = SelectField('Preferred Time', choices=[
        ('morning', 'Morning (6am-12pm)'),
        ('afternoon', 'Afternoon (12pm-5pm)'),
        ('evening', 'Evening (5pm-9pm)')
    ], validators=[DataRequired(message='Preferred time is required')])
    
    submit = SubmitField('Book Trial Class')


class LoginForm(FlaskForm):
    """Login form for instructors
    
    Implements Requirements 13.1, 13.2 (login form with username and password).
    CSRF protection is automatically enabled by Flask-WTF.
    """
    username = StringField('Username', validators=[
        DataRequired(message='Username is required')
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    
    submit = SubmitField('Login')



class ClassForm(FlaskForm):
    """Form for creating/editing classes
    
    Implements Requirements 14.3, 14.4 (class creation/editing form).
    CSRF protection is automatically enabled by Flask-WTF.
    """
    name = StringField('Class Name', validators=[
        DataRequired(message='Class name is required'),
        Length(max=100)
    ])
    
    day_of_week = SelectField('Day of Week', choices=[
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday')
    ], validators=[DataRequired()])
    
    start_time = TimeField('Start Time', validators=[
        DataRequired(message='Start time is required')
    ])
    
    end_time = TimeField('End Time', validators=[
        DataRequired(message='End time is required')
    ])
    
    submit = SubmitField('Save Class')


class AnnouncementForm(FlaskForm):
    """Form for creating/editing announcements
    
    Implements Requirements 15.2, 15.3 (announcement creation/editing form).
    CSRF protection is automatically enabled by Flask-WTF.
    """
    title = StringField('Title', validators=[
        DataRequired(message='Title is required'),
        Length(max=200)
    ])
    
    content = TextAreaField('Content', validators=[
        DataRequired(message='Content is required')
    ])
    
    submit = SubmitField('Save Announcement')


class FAQForm(FlaskForm):
    """Form for creating/editing FAQs
    
    Implements Requirements 19.2, 19.3 (FAQ creation/editing form).
    CSRF protection is automatically enabled by Flask-WTF.
    """
    question = StringField('Question', validators=[
        DataRequired(message='Question is required'),
        Length(max=500)
    ])
    
    answer = TextAreaField('Answer', validators=[
        DataRequired(message='Answer is required')
    ])
    
    display_order = IntegerField('Display Order', validators=[
        Optional()
    ], default=0)
    
    submit = SubmitField('Save FAQ')



class SiteSettingsForm(FlaskForm):
    """Form for managing site settings (banner/logo)
    
    Implements Requirements 17.2, 17.3 (site settings form for banner and logo).
    CSRF protection is automatically enabled by Flask-WTF.
    """
    banner_image = FileField('Banner Image', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 
                   'Only image files allowed (JPEG, PNG, GIF, WebP)')
    ])
    
    logo_image = FileField('Logo Image', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'], 
                   'Only image files allowed (JPEG, PNG, GIF, WebP, SVG)')
    ])
    
    remove_banner = BooleanField('Remove Banner')
    remove_logo = BooleanField('Remove Logo')
    
    submit = SubmitField('Save Settings')


class InstructorProfileForm(FlaskForm):
    """Form for managing instructor profile
    
    Implements Requirements 18.2, 18.3, 18.4, 18.5 (instructor profile management form).
    CSRF protection is automatically enabled by Flask-WTF.
    """
    photo = FileField('Profile Photo', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 
                   'Only image files allowed (JPEG, PNG, GIF, WebP)')
    ])
    
    biography = TextAreaField('Biography', validators=[
        DataRequired(message='Biography is required'),
        Length(min=10, max=5000, message='Biography must be 10-5000 characters')
    ])
    
    title = StringField('Title/Designation', validators=[
        DataRequired(message='Title is required'),
        Length(max=100)
    ])
    
    is_head_instructor = BooleanField('Head Instructor/Professor')
    
    remove_photo = BooleanField('Remove Photo')
    
    submit = SubmitField('Save Profile')
