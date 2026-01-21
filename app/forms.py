"""
Form Classes

This module defines Flask-WTF form classes for the BJJ school website.
Forms will be implemented in task 3.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SelectField, SubmitField
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
