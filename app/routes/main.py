"""
Main Routes Blueprint

This module defines routes for the home page and instructor page.
"""

from flask import Blueprint, render_template, current_app
from app.services.instagram import InstagramService, InstagramAPIError
from app.models import Class
import logging
from collections import defaultdict

main_bp = Blueprint('main', __name__)

# Configure logging
logger = logging.getLogger(__name__)


@main_bp.route('/')
def home():
    """
    Homepage with Instagram carousel.
    
    Fetches recent Instagram photos and displays them in a carousel.
    If Instagram API fails, displays a fallback message.
    
    Returns:
        Rendered home template with Instagram photos or fallback message
    """
    instagram_photos = []
    instagram_error = None
    
    try:
        # Get Instagram credentials from app config
        access_token = current_app.config.get('INSTAGRAM_ACCESS_TOKEN')
        user_id = current_app.config.get('INSTAGRAM_USER_ID')
        
        if not access_token or not user_id:
            raise InstagramAPIError("Instagram credentials not configured")
        
        # Initialize Instagram service
        instagram_service = InstagramService(access_token, user_id)
        
        # Fetch recent media (6 photos by default)
        instagram_photos = instagram_service.fetch_recent_media(limit=6)
        
        logger.info(f"Successfully fetched {len(instagram_photos)} Instagram photos")
        
    except InstagramAPIError as e:
        # Log the error and set error message for template
        logger.error(f"Instagram API error: {str(e)}")
        instagram_error = "Instagram photos temporarily unavailable. Please check back later."
        
    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"Unexpected error fetching Instagram photos: {str(e)}")
        instagram_error = "Instagram photos temporarily unavailable. Please check back later."
    
    return render_template(
        'home.html',
        instagram_photos=instagram_photos,
        instagram_error=instagram_error
    )


@main_bp.route('/instructor')
def instructor():
    """
    Instructor information page.
    
    Displays all instructors from the database with head instructor listed first.
    Shows default placeholder for missing photos.
    
    Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 1.6
    
    Returns:
        Rendered instructor template with all instructors
    """
    from app.models import InstructorProfile
    
    # Fetch all instructor profiles from database
    # Order by is_head_instructor DESC (head instructor first), then by id
    all_instructors = InstructorProfile.query.order_by(
        InstructorProfile.is_head_instructor.desc(),
        InstructorProfile.id
    ).all()
    
    logger.info(f"Displaying {len(all_instructors)} instructors")
    
    return render_template(
        'instructor.html',
        instructors=all_instructors,
        has_instructors=len(all_instructors) > 0
    )


@main_bp.route('/classes')
def classes():
    """
    Classes schedule page.
    
    Displays all available classes organized by day of the week.
    Shows a message when no classes are available.
    
    Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5
    
    Returns:
        Rendered classes template with classes organized by day
    """
    # Fetch all classes from database
    all_classes = Class.query.all()
    
    # Define day order for proper sorting
    day_order = {
        'Monday': 1,
        'Tuesday': 2,
        'Wednesday': 3,
        'Thursday': 4,
        'Friday': 5,
        'Saturday': 6,
        'Sunday': 7
    }
    
    # Organize classes by day of week
    classes_by_day = defaultdict(list)
    for cls in all_classes:
        classes_by_day[cls.day_of_week].append(cls)
    
    # Sort classes within each day by start time
    for day in classes_by_day:
        classes_by_day[day].sort(key=lambda x: x.start_time)
    
    # Convert to sorted list of tuples (day, classes) for template
    sorted_classes = sorted(
        classes_by_day.items(),
        key=lambda x: day_order.get(x[0], 8)
    )
    
    logger.info(f"Displaying {len(all_classes)} classes across {len(sorted_classes)} days")
    
    return render_template(
        'classes.html',
        classes_by_day=sorted_classes,
        has_classes=len(all_classes) > 0
    )


@main_bp.route('/announcements')
def announcements():
    """
    Announcements page.
    
    Displays all announcements in reverse chronological order (newest first).
    Shows a message when no announcements are available.
    
    Validates: Requirements 11.1, 11.2, 11.3, 11.4, 11.5
    
    Returns:
        Rendered announcements template with announcements in reverse chronological order
    """
    from app.models import Announcement
    
    # Fetch all announcements from database, ordered by published_date descending
    all_announcements = Announcement.query.order_by(Announcement.published_date.desc()).all()
    
    logger.info(f"Displaying {len(all_announcements)} announcements")
    
    return render_template(
        'announcements.html',
        announcements=all_announcements,
        has_announcements=len(all_announcements) > 0
    )


@main_bp.route('/faq')
def faq():
    """
    FAQ page.
    
    Displays all FAQs ordered by display_order.
    Shows a message when no FAQs are available.
    
    Validates: Requirements 11.5.1, 11.5.2, 11.5.3, 11.5.4, 11.5.5, 11.5.6
    
    Returns:
        Rendered FAQ template with FAQs ordered by display_order
    """
    from app.models import FAQ
    
    # Fetch all FAQs from database, ordered by display_order
    all_faqs = FAQ.query.order_by(FAQ.display_order).all()
    
    logger.info(f"Displaying {len(all_faqs)} FAQs")
    
    return render_template(
        'faq.html',
        faqs=all_faqs,
        has_faqs=len(all_faqs) > 0
    )
