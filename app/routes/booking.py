"""
Booking Routes Blueprint

This module defines routes for the trial booking form.
Implements Requirements 3.2, 3.3, 3.4, 3.6, 3.8, 7.5
"""

from flask import Blueprint, render_template, redirect, url_for, flash
from datetime import datetime, timedelta
from app import db
from app.forms import TrialBookingForm
from app.models import TrialBooking
from markupsafe import escape

booking_bp = Blueprint('booking', __name__)


@booking_bp.route('/booking', methods=['GET', 'POST'])
def booking():
    """
    Trial booking form page.
    
    GET: Display the trial booking form
    POST: Validate form, check for duplicates, sanitize input, save to database, 
          and show confirmation with booking details
    
    Implements:
    - Requirement 3.2: Form validation
    - Requirement 3.3: Store booking in database
    - Requirement 3.4: Display confirmation message with booking details
    - Requirement 3.6: Display validation errors
    - Requirement 3.8: Prevent duplicate bookings (same email within 24 hours)
    - Requirement 7.5: Input sanitization
    
    Returns:
        Rendered booking template or redirect to booking page with flash message
    """
    form = TrialBookingForm()
    
    if form.validate_on_submit():
        # Check for duplicate booking (Requirement 3.8)
        # Same email within 24 hours should be rejected
        email = form.email.data.strip().lower()
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
        
        existing_booking = TrialBooking.query.filter(
            db.func.lower(TrialBooking.email) == email,
            TrialBooking.submitted_at >= twenty_four_hours_ago
        ).first()
        
        if existing_booking:
            # Display error message for duplicate booking
            flash(
                'You have already booked a trial class within the last 24 hours. '
                'Please wait before booking another trial or contact us directly.',
                'error'
            )
            return render_template('booking.html', form=form)
        
        # Sanitize user input to prevent XSS attacks (Requirement 7.5)
        # Using escape() to convert HTML special characters to safe entities
        sanitized_name = escape(form.name.data.strip())
        sanitized_email = escape(form.email.data.strip())
        sanitized_phone = escape(form.phone.data.strip())
        
        # Create new trial booking (Requirement 3.3)
        booking = TrialBooking(
            name=sanitized_name,
            email=sanitized_email,
            phone=sanitized_phone,
            preferred_date=form.preferred_date.data,
            preferred_time=form.preferred_time.data
        )
        
        try:
            # Save to database
            db.session.add(booking)
            db.session.commit()
            
            # Display confirmation message with booking details (Requirement 3.4)
            # Format the date for display
            date_str = form.preferred_date.data.strftime('%B %d, %Y')
            time_label = dict(form.preferred_time.choices).get(form.preferred_time.data)
            
            flash(
                f'Your trial class has been booked! We will contact you at {sanitized_email} '
                f'to confirm your booking for {date_str} during {time_label}.',
                'success'
            )
            
            # Redirect to clear form (POST-Redirect-GET pattern)
            return redirect(url_for('booking.booking'))
            
        except Exception as e:
            # Rollback on error
            db.session.rollback()
            
            # Log error (in production, use proper logging)
            print(f"Error saving trial booking: {e}")
            
            # Display error message to user
            flash('An error occurred while booking your trial class. Please try again.', 'error')
    
    # GET request or validation failed - display form
    # Validation errors are automatically displayed by the template (Requirement 3.6)
    return render_template('booking.html', form=form)
