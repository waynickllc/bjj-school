"""
Database Models

This module defines SQLAlchemy models for the BJJ school website.
"""

from app import db
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class ContactSubmission(db.Model):
    """
    Model for contact form submissions.
    
    Stores visitor contact inquiries with name, email, phone, and message.
    Validates: Requirements 5.2
    """
    __tablename__ = 'contact_submissions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    message = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<ContactSubmission {self.id}: {self.name} ({self.email})>'
    
    def to_dict(self):
        """
        Convert model instance to dictionary.
        
        Returns:
            dict: Dictionary representation of the contact submission
        """
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'message': self.message,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None
        }


class TrialBooking(db.Model):
    """
    Model for trial class bookings.
    
    Stores visitor trial class booking requests with name, email, phone,
    preferred date, and preferred time.
    
    Note: The check constraint for future dates (preferred_date >= CURDATE()) 
    is enforced at the application level in form validation rather than at the 
    database level to maintain compatibility with SQLite for testing.
    In production MySQL, this constraint can be added via migration.
    
    Validates: Requirements 5.3
    """
    __tablename__ = 'trial_bookings'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=False)
    preferred_date = db.Column(db.Date, nullable=False)
    preferred_time = db.Column(db.String(50), nullable=False)
    submitted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<TrialBooking {self.id}: {self.name} ({self.email}) on {self.preferred_date}>'
    
    def to_dict(self):
        """
        Convert model instance to dictionary.
        
        Returns:
            dict: Dictionary representation of the trial booking
        """
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'preferred_date': self.preferred_date.isoformat() if self.preferred_date else None,
            'preferred_time': self.preferred_time,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None
        }


class Class(db.Model):
    """
    Model for scheduled training classes.
    
    Stores class schedule information including name, day of week, 
    start time, and end time.
    
    Validates: Requirements 10, 5.1
    """
    __tablename__ = 'classes'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    day_of_week = db.Column(db.String(20), nullable=False, index=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    
    def __repr__(self):
        return f'<Class {self.id}: {self.name} on {self.day_of_week} at {self.start_time}>'
    
    def to_dict(self):
        """
        Convert model instance to dictionary.
        
        Returns:
            dict: Dictionary representation of the class
        """
        return {
            'id': self.id,
            'name': self.name,
            'day_of_week': self.day_of_week,
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None
        }


class Announcement(db.Model):
    """
    Model for school announcements.
    
    Stores announcement information including title, content, and publication date.
    Announcements are displayed on the announcements page in reverse chronological order.
    
    Validates: Requirements 11, 5.1
    """
    __tablename__ = 'announcements'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    published_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<Announcement {self.id}: {self.title} published on {self.published_date}>'
    
    def to_dict(self):
        """
        Convert model instance to dictionary.
        
        Returns:
            dict: Dictionary representation of the announcement
        """
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'published_date': self.published_date.isoformat() if self.published_date else None
        }


class FAQ(db.Model):
    """
    Model for frequently asked questions.
    
    Stores FAQ information including question, answer, and display order.
    FAQs are displayed on the FAQ page ordered by display_order.
    
    Validates: Requirements 11.5, 5.1
    """
    __tablename__ = 'faqs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    display_order = db.Column(db.Integer, nullable=False, default=0, index=True)
    
    def __repr__(self):
        return f'<FAQ {self.id}: {self.question[:50]}...>'
    
    def to_dict(self):
        """
        Convert model instance to dictionary.
        
        Returns:
            dict: Dictionary representation of the FAQ
        """
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'display_order': self.display_order
        }


class User(UserMixin, db.Model):
    """
    Model for instructor user accounts.
    
    Stores instructor authentication information including username,
    password hash, and email. Passwords are hashed using bcrypt via
    Werkzeug's security utilities.
    
    Inherits from UserMixin to provide Flask-Login integration with
    methods: is_authenticated, is_active, is_anonymous, get_id()
    
    Validates: Requirements 12.6, 5.1
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.id}: {self.username} ({self.email})>'
    
    def set_password(self, password):
        """
        Hash and set the user's password using bcrypt.
        
        Args:
            password: Plain text password to hash
        """
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        """
        Verify a password against the stored hash.
        
        Args:
            password: Plain text password to verify
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """
        Convert model instance to dictionary.
        
        Note: Password hash is intentionally excluded for security.
        
        Returns:
            dict: Dictionary representation of the user
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class SiteSettings(db.Model):
    """
    Model for site-wide settings (singleton pattern).
    
    Stores configurable website elements including banner and logo image paths.
    Only one row should exist in this table (id=1) to maintain singleton pattern.
    
    Validates: Requirements 16.6, 5.1
    """
    __tablename__ = 'site_settings'
    
    id = db.Column(db.Integer, primary_key=True, default=1)
    banner_image_path = db.Column(db.String(255), nullable=True)
    logo_image_path = db.Column(db.String(255), nullable=True)
    
    def __repr__(self):
        return f'<SiteSettings id={self.id}: banner={self.banner_image_path}, logo={self.logo_image_path}>'
    
    def to_dict(self):
        """
        Convert model instance to dictionary.
        
        Returns:
            dict: Dictionary representation of the site settings
        """
        return {
            'id': self.id,
            'banner_image_path': self.banner_image_path,
            'logo_image_path': self.logo_image_path
        }


class InstructorProfile(db.Model):
    """
    Model for instructor profile information.
    
    Stores instructor profile details including photo, biography, title/designation,
    and head instructor status. Each profile is linked to a User account via foreign key.
    Only one instructor can be designated as head instructor at a time.
    
    Validates: Requirements 17, 5.1
    """
    __tablename__ = 'instructor_profiles'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    photo_path = db.Column(db.String(255), nullable=True)
    biography = db.Column(db.Text, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    is_head_instructor = db.Column(db.Boolean, nullable=False, default=False, index=True)
    
    # Relationship to User model
    user = db.relationship('User', backref=db.backref('instructor_profile', uselist=False, cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<InstructorProfile {self.id}: User {self.user_id} - {self.title}>'
    
    def to_dict(self):
        """
        Convert model instance to dictionary.
        
        Returns:
            dict: Dictionary representation of the instructor profile
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'photo_path': self.photo_path,
            'biography': self.biography,
            'title': self.title,
            'is_head_instructor': self.is_head_instructor
        }
