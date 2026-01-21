"""
Main Routes Blueprint

This module defines routes for the home page and instructor page.
"""

from flask import Blueprint, render_template, current_app
from app.services.instagram import InstagramService, InstagramAPIError
import logging

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
    
    Displays biographical information, qualifications, certifications,
    and training history of the BJJ school instructor.
    
    Returns:
        Rendered instructor template
    """
    # Instructor data - in a real application, this might come from a database
    # or configuration file. For now, we'll pass it directly to the template.
    instructor_data = {
        'name': 'Master Instructor',
        'bio': 'Experienced Brazilian Jiu-Jitsu instructor with over 15 years of training and teaching.',
        'qualifications': [
            'Black Belt in Brazilian Jiu-Jitsu',
            'Certified Gracie Jiu-Jitsu Instructor',
            'First Aid and CPR Certified'
        ],
        'training_history': [
            'Trained under Master Carlos Gracie Jr.',
            'Competed in IBJJF World Championships',
            'Teaching BJJ since 2010'
        ]
    }
    
    return render_template('instructor.html', instructor=instructor_data)
