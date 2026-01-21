"""
Contact Routes Blueprint

This module defines routes for the contact form.
Implements Requirements 2.2, 2.3, 2.4, 2.6, 7.5
"""

from flask import Blueprint, render_template, redirect, url_for, flash
from app import db
from app.forms import ContactForm
from app.models import ContactSubmission
from markupsafe import escape

contact_bp = Blueprint('contact', __name__)


@contact_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """
    Contact form page.
    
    GET: Display the contact form
    POST: Validate form, sanitize input, save to database, and show confirmation
    
    Implements:
    - Requirement 2.2: Form validation
    - Requirement 2.3: Store submission in database
    - Requirement 2.4: Display confirmation message
    - Requirement 2.6: Display validation errors
    - Requirement 7.5: Input sanitization
    
    Returns:
        Rendered contact template or redirect to contact page with flash message
    """
    form = ContactForm()
    
    if form.validate_on_submit():
        # Sanitize user input to prevent XSS attacks (Requirement 7.5)
        # Using escape() to convert HTML special characters to safe entities
        sanitized_name = escape(form.name.data.strip())
        sanitized_email = escape(form.email.data.strip())
        sanitized_phone = escape(form.phone.data.strip()) if form.phone.data else None
        sanitized_message = escape(form.message.data.strip())
        
        # Create new contact submission (Requirement 2.3)
        submission = ContactSubmission(
            name=sanitized_name,
            email=sanitized_email,
            phone=sanitized_phone,
            message=sanitized_message
        )
        
        try:
            # Save to database
            db.session.add(submission)
            db.session.commit()
            
            # Display confirmation message (Requirement 2.4)
            flash('Thank you for your message! We will get back to you soon.', 'success')
            
            # Redirect to clear form (POST-Redirect-GET pattern)
            return redirect(url_for('contact.contact'))
            
        except Exception as e:
            # Rollback on error
            db.session.rollback()
            
            # Log error (in production, use proper logging)
            print(f"Error saving contact submission: {e}")
            
            # Display error message to user
            flash('An error occurred while submitting your message. Please try again.', 'error')
    
    # GET request or validation failed - display form
    # Validation errors are automatically displayed by the template (Requirement 2.6)
    return render_template('contact.html', form=form)
