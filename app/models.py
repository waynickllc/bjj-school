"""
Database Models

This module defines SQLAlchemy models for the BJJ school website.
"""

from app import db
from datetime import datetime, date


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
