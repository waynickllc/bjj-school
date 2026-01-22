"""
Admin Routes

This module handles admin dashboard routes for managing classes, announcements, FAQs, etc.
Implements Requirements 14-19 (Admin Dashboard functionality).
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, get_flashed_messages
from flask_login import login_required, current_user
from app import db
from app.models import Class, Announcement, FAQ, SiteSettings, InstructorProfile
from app.forms import ClassForm, AnnouncementForm, FAQForm, SiteSettingsForm, InstructorProfileForm
from app.file_utils import (
    validate_image_file, 
    save_uploaded_file, 
    delete_file,
    ALLOWED_IMAGE_EXTENSIONS,
    ALLOWED_LOGO_EXTENSIONS
)
from datetime import datetime
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Admin dashboard home page.
    
    Displays overview/statistics for the admin.
    
    Implements:
    - Requirement 16.1: Redirect unauthenticated users to login page
    - Requirement 16.3: Verify instructor authentication on every admin request
    
    Returns:
        Rendered admin dashboard template
    """
    return render_template('admin/dashboard.html')



# ============================================================================
# Class Management Routes
# ============================================================================

@admin_bp.route('/classes')
@login_required
def list_classes():
    """
    List all classes in the admin dashboard.
    
    Fetches all classes from the database and displays them in a table
    with options to edit or delete each class.
    
    Implements:
    - Requirement 14.2: Display list of all existing classes
    - Requirement 16.1: Redirect unauthenticated users to login page
    - Requirement 16.3: Verify instructor authentication on every admin request
    
    Returns:
        Rendered admin classes list template
    """
    classes = Class.query.order_by(Class.day_of_week, Class.start_time).all()
    return render_template('admin/classes.html', classes=classes)


@admin_bp.route('/classes/create', methods=['GET', 'POST'])
@login_required
def create_class():
    """
    Create a new class.
    
    GET: Display empty ClassForm
    POST: Validate form data, create new class in database, redirect to list
    
    Implements:
    - Requirement 14.3: Provide form to create new class
    - Requirement 14.4: Validate all required fields
    - Requirement 14.5: Store class in database and display confirmation
    - Requirement 14.10: Implement CSRF protection
    - Requirement 16.1: Redirect unauthenticated users to login page
    - Requirement 16.3: Verify instructor authentication on every admin request
    
    Returns:
        GET: Rendered create class form template
        POST: Redirect to classes list on success, or re-render form with errors
    """
    form = ClassForm()
    
    if form.validate_on_submit():
        # Create new class from form data
        new_class = Class(
            name=form.name.data,
            day_of_week=form.day_of_week.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data
        )
        
        try:
            db.session.add(new_class)
            db.session.commit()
            flash(f'Class "{new_class.name}" created successfully!', 'success')
            return redirect(url_for('admin.list_classes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating class: {str(e)}', 'error')
    
    return render_template('admin/class_form.html', form=form, action='Create')


@admin_bp.route('/classes/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_class(id):
    """
    Edit an existing class.
    
    GET: Load class data and display ClassForm pre-populated with current values
    POST: Validate form data, update class in database, redirect to list
    
    Implements:
    - Requirement 14.6: Provide edit function for each class
    - Requirement 14.7: Update class in database and display confirmation
    - Requirement 14.10: Implement CSRF protection
    - Requirement 16.1: Redirect unauthenticated users to login page
    - Requirement 16.3: Verify instructor authentication on every admin request
    
    Args:
        id: Class ID to edit
    
    Returns:
        GET: Rendered edit class form template with pre-populated data
        POST: Redirect to classes list on success, or re-render form with errors
        404: If class not found
    """
    class_obj = Class.query.get_or_404(id)
    form = ClassForm(obj=class_obj)
    
    if form.validate_on_submit():
        # Update class with form data
        class_obj.name = form.name.data
        class_obj.day_of_week = form.day_of_week.data
        class_obj.start_time = form.start_time.data
        class_obj.end_time = form.end_time.data
        
        try:
            db.session.commit()
            flash(f'Class "{class_obj.name}" updated successfully!', 'success')
            return redirect(url_for('admin.list_classes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating class: {str(e)}', 'error')
    
    return render_template('admin/class_form.html', form=form, action='Edit', class_obj=class_obj)


@admin_bp.route('/classes/<int:id>/delete', methods=['POST'])
@login_required
def delete_class(id):
    """
    Delete a class.
    
    Removes the class from the database and redirects to the classes list.
    This route only accepts POST requests for security (prevents accidental deletion via GET).
    
    Implements:
    - Requirement 14.8: Provide delete function for each class
    - Requirement 14.9: Remove class from database and display confirmation
    - Requirement 14.10: Implement CSRF protection
    - Requirement 16.1: Redirect unauthenticated users to login page
    - Requirement 16.3: Verify instructor authentication on every admin request
    
    Args:
        id: Class ID to delete
    
    Returns:
        Redirect to classes list with success or error message
        404: If class not found
    """
    class_obj = Class.query.get_or_404(id)
    class_name = class_obj.name
    
    try:
        db.session.delete(class_obj)
        db.session.commit()
        flash(f'Class "{class_name}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting class: {str(e)}', 'error')
    
    return redirect(url_for('admin.list_classes'))



# ============================================================================
# Announcement Management Routes
# ============================================================================

@admin_bp.route('/announcements')
@login_required
def list_announcements():
    """
    List all announcements in the admin dashboard.
    
    Fetches all announcements from the database and displays them in reverse
    chronological order (newest first) with options to edit or delete each.
    
    Implements:
    - Requirement 15.1: Display list of all existing announcements
    - Requirement 16.1: Redirect unauthenticated users to login page
    - Requirement 16.3: Verify instructor authentication on every admin request
    
    Returns:
        Rendered admin announcements list template
    """
    announcements = Announcement.query.order_by(Announcement.published_date.desc()).all()
    return render_template('admin/announcements.html', announcements=announcements)


@admin_bp.route('/announcements/create', methods=['GET', 'POST'])
@login_required
def create_announcement():
    """
    Create a new announcement.
    
    GET: Display empty AnnouncementForm
    POST: Validate form data, create new announcement with current timestamp, redirect to list
    
    Implements:
    - Requirement 15.2: Provide form to create new announcement
    - Requirement 15.3: Validate all required fields
    - Requirement 15.4: Store announcement in database with current timestamp and display confirmation
    - Requirement 15.9: Implement CSRF protection
    - Requirement 16.1: Redirect unauthenticated users to login page
    - Requirement 16.3: Verify instructor authentication on every admin request
    
    Returns:
        GET: Rendered create announcement form template
        POST: Redirect to announcements list on success, or re-render form with errors
    """
    form = AnnouncementForm()
    
    if form.validate_on_submit():
        # Create new announcement from form data with current timestamp
        new_announcement = Announcement(
            title=form.title.data,
            content=form.content.data,
            published_date=datetime.utcnow()
        )
        
        try:
            db.session.add(new_announcement)
            db.session.commit()
            flash(f'Announcement "{new_announcement.title}" created successfully!', 'success')
            return redirect(url_for('admin.list_announcements'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating announcement: {str(e)}', 'error')
    
    return render_template('admin/announcement_form.html', form=form, action='Create')


@admin_bp.route('/announcements/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_announcement(id):
    """
    Edit an existing announcement.
    
    GET: Load announcement data and display AnnouncementForm pre-populated with current values
    POST: Validate form data, update announcement in database, redirect to list
    
    Implements:
    - Requirement 15.5: Provide edit function for each announcement
    - Requirement 15.6: Update announcement in database and display confirmation
    - Requirement 15.9: Implement CSRF protection
    - Requirement 16.1: Redirect unauthenticated users to login page
    - Requirement 16.3: Verify instructor authentication on every admin request
    
    Args:
        id: Announcement ID to edit
    
    Returns:
        GET: Rendered edit announcement form template with pre-populated data
        POST: Redirect to announcements list on success, or re-render form with errors
        404: If announcement not found
    """
    announcement = Announcement.query.get_or_404(id)
    form = AnnouncementForm(obj=announcement)
    
    if form.validate_on_submit():
        # Update announcement with form data (keep original published_date)
        announcement.title = form.title.data
        announcement.content = form.content.data
        
        try:
            db.session.commit()
            flash(f'Announcement "{announcement.title}" updated successfully!', 'success')
            return redirect(url_for('admin.list_announcements'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating announcement: {str(e)}', 'error')
    
    return render_template('admin/announcement_form.html', form=form, action='Edit', announcement=announcement)


@admin_bp.route('/announcements/<int:id>/delete', methods=['POST'])
@login_required
def delete_announcement(id):
    """
    Delete an announcement.
    
    Removes the announcement from the database and redirects to the announcements list.
    This route only accepts POST requests for security (prevents accidental deletion via GET).
    
    Implements:
    - Requirement 15.7: Provide delete function for each announcement
    - Requirement 15.8: Remove announcement from database and display confirmation
    - Requirement 15.9: Implement CSRF protection
    - Requirement 16.1: Redirect unauthenticated users to login page
    - Requirement 16.3: Verify instructor authentication on every admin request
    
    Args:
        id: Announcement ID to delete
    
    Returns:
        Redirect to announcements list with success or error message
        404: If announcement not found
    """
    announcement = Announcement.query.get_or_404(id)
    announcement_title = announcement.title
    
    try:
        db.session.delete(announcement)
        db.session.commit()
        flash(f'Announcement "{announcement_title}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting announcement: {str(e)}', 'error')
    
    return redirect(url_for('admin.list_announcements'))



# ============================================================================
# FAQ Management Routes
# ============================================================================

@admin_bp.route('/faqs')
@login_required
def list_faqs():
    """
    List all FAQs in the admin dashboard.
    
    Fetches all FAQs from the database and displays them ordered by display_order
    with options to edit or delete each FAQ.
    
    Implements:
    - Requirement 19.1: Display list of all existing FAQs
    - Requirement 16.1: Redirect unauthenticated users to login page
    - Requirement 16.3: Verify instructor authentication on every admin request
    
    Returns:
        Rendered admin FAQs list template
    """
    faqs = FAQ.query.order_by(FAQ.display_order, FAQ.id).all()
    return render_template('admin/faqs.html', faqs=faqs)


@admin_bp.route('/faqs/create', methods=['GET', 'POST'])
@login_required
def create_faq():
    """
    Create a new FAQ.
    
    GET: Display empty FAQForm
    POST: Validate form data, create new FAQ in database, redirect to list
    
    Implements:
    - Requirement 19.2: Provide form to create new FAQ
    - Requirement 19.3: Validate that both question and answer fields are not empty
    - Requirement 19.4: Store FAQ in database and display confirmation
    - Requirement 19.10: Implement CSRF protection
    - Requirement 16.1: Redirect unauthenticated users to login page
    - Requirement 16.3: Verify instructor authentication on every admin request
    
    Returns:
        GET: Rendered create FAQ form template
        POST: Redirect to FAQs list on success, or re-render form with errors
    """
    form = FAQForm()
    
    if form.validate_on_submit():
        # Create new FAQ from form data
        new_faq = FAQ(
            question=form.question.data,
            answer=form.answer.data,
            display_order=form.display_order.data if form.display_order.data is not None else 0
        )
        
        try:
            db.session.add(new_faq)
            db.session.commit()
            flash('FAQ created successfully!', 'success')
            return redirect(url_for('admin.list_faqs'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating FAQ: {str(e)}', 'error')
    
    return render_template('admin/faq_form.html', form=form, action='Create')


@admin_bp.route('/faqs/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_faq(id):
    """
    Edit an existing FAQ.
    
    GET: Load FAQ data and display FAQForm pre-populated with current values
    POST: Validate form data, update FAQ in database, redirect to list
    
    Implements:
    - Requirement 19.5: Provide edit function for each FAQ
    - Requirement 19.6: Update FAQ in database and display confirmation
    - Requirement 19.10: Implement CSRF protection
    - Requirement 16.1: Redirect unauthenticated users to login page
    - Requirement 16.3: Verify instructor authentication on every admin request
    
    Args:
        id: FAQ ID to edit
    
    Returns:
        GET: Rendered edit FAQ form template with pre-populated data
        POST: Redirect to FAQs list on success, or re-render form with errors
        404: If FAQ not found
    """
    faq = FAQ.query.get_or_404(id)
    form = FAQForm(obj=faq)
    
    if form.validate_on_submit():
        # Update FAQ with form data
        faq.question = form.question.data
        faq.answer = form.answer.data
        faq.display_order = form.display_order.data if form.display_order.data is not None else 0
        
        try:
            db.session.commit()
            flash('FAQ updated successfully!', 'success')
            return redirect(url_for('admin.list_faqs'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating FAQ: {str(e)}', 'error')
    
    return render_template('admin/faq_form.html', form=form, action='Edit', faq=faq)


@admin_bp.route('/faqs/<int:id>/delete', methods=['POST'])
@login_required
def delete_faq(id):
    """
    Delete an FAQ.
    
    Removes the FAQ from the database and redirects to the FAQs list.
    This route only accepts POST requests for security (prevents accidental deletion via GET).
    
    Implements:
    - Requirement 19.7: Provide delete function for each FAQ
    - Requirement 19.8: Remove FAQ from database and display confirmation
    - Requirement 19.10: Implement CSRF protection
    - Requirement 16.1: Redirect unauthenticated users to login page
    - Requirement 16.3: Verify instructor authentication on every admin request
    
    Args:
        id: FAQ ID to delete
    
    Returns:
        Redirect to FAQs list with success or error message
        404: If FAQ not found
    """
    faq = FAQ.query.get_or_404(id)
    
    try:
        db.session.delete(faq)
        db.session.commit()
        flash('FAQ deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting FAQ: {str(e)}', 'error')
    
    return redirect(url_for('admin.list_faqs'))


@admin_bp.route('/faqs/reorder', methods=['POST'])
@login_required
def reorder_faqs():
    """
    Reorder FAQs.
    
    Accepts a list of FAQ IDs in the new desired order and updates the
    display_order field for each FAQ accordingly.
    
    Implements:
    - Requirement 19.9: Allow reordering FAQs to control display order
    - Requirement 19.10: Implement CSRF protection
    - Requirement 16.1: Redirect unauthenticated users to login page
    - Requirement 16.3: Verify instructor authentication on every admin request
    
    Expected POST data:
        faq_ids: List of FAQ IDs in the new order (e.g., [3, 1, 2])
    
    Returns:
        JSON response with success status
        400: If faq_ids not provided or invalid
    """
    try:
        # Get the list of FAQ IDs from the request
        faq_ids = request.json.get('faq_ids', [])
        
        if not faq_ids:
            return {'success': False, 'message': 'No FAQ IDs provided'}, 400
        
        # Update display_order for each FAQ
        for index, faq_id in enumerate(faq_ids):
            faq = FAQ.query.get(faq_id)
            if faq:
                faq.display_order = index
        
        db.session.commit()
        return {'success': True, 'message': 'FAQs reordered successfully'}
    
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': str(e)}, 500



# ============================================================================
# Site Settings Management Routes
# ============================================================================

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def site_settings():
    """
    Manage site settings (banner/logo).
    
    GET: Load current settings and display SiteSettingsForm with previews
    POST: Validate files, save uploads, update database, redirect with confirmation
    
    Implements:
    - Requirement 17.1: Provide site settings section for managing visual elements
    - Requirement 17.2: Allow uploading banner image file
    - Requirement 17.3: Allow uploading logo image file
    - Requirement 17.4: Validate banner image file type (JPEG, PNG, GIF, WebP)
    - Requirement 17.5: Validate logo image file type (JPEG, PNG, GIF, WebP, SVG)
    - Requirement 17.6: Store image file and update Site_Settings in database
    - Requirement 17.11: Display preview of current banner and logo
    - Requirement 17.12: Allow removing banner or logo to revert to defaults
    - Requirement 17.13: Implement CSRF protection
    - Requirement 16.1: Redirect unauthenticated users to login page
    - Requirement 16.3: Verify instructor authentication on every admin request
    
    Returns:
        GET: Rendered site settings form template with current settings
        POST: Redirect to settings page on success, or re-render form with errors
    """
    # Get or create site settings (singleton pattern - only one row with id=1)
    settings = SiteSettings.query.get(1)
    if not settings:
        settings = SiteSettings(id=1)
        db.session.add(settings)
        db.session.commit()
    
    form = SiteSettingsForm()
    
    if form.validate_on_submit():
        try:
            # Handle banner image removal
            if form.remove_banner.data and settings.banner_image_path:
                if delete_file(settings.banner_image_path):
                    settings.banner_image_path = None
                    flash('Banner image removed successfully!', 'success')
            
            # Handle logo image removal
            if form.remove_logo.data and settings.logo_image_path:
                if delete_file(settings.logo_image_path):
                    settings.logo_image_path = None
                    flash('Logo image removed successfully!', 'success')
            
            # Handle banner image upload
            if form.banner_image.data and form.banner_image.data.filename:
                banner_file = form.banner_image.data
                
                # Validate the banner image
                is_valid, error_message = validate_image_file(banner_file, ALLOWED_IMAGE_EXTENSIONS)
                if not is_valid:
                    flash(f'Banner upload error: {error_message}', 'error')
                else:
                    # Delete old banner if exists
                    if settings.banner_image_path:
                        delete_file(settings.banner_image_path)
                    
                    # Save new banner
                    upload_folder = os.path.join('app', 'static', 'uploads', 'banners')
                    banner_path = save_uploaded_file(banner_file, upload_folder, 'banner_')
                    settings.banner_image_path = banner_path
                    flash('Banner image uploaded successfully!', 'success')
            
            # Handle logo image upload
            if form.logo_image.data and form.logo_image.data.filename:
                logo_file = form.logo_image.data
                
                # Validate the logo image
                is_valid, error_message = validate_image_file(logo_file, ALLOWED_LOGO_EXTENSIONS)
                if not is_valid:
                    flash(f'Logo upload error: {error_message}', 'error')
                else:
                    # Delete old logo if exists
                    if settings.logo_image_path:
                        delete_file(settings.logo_image_path)
                    
                    # Save new logo
                    upload_folder = os.path.join('app', 'static', 'uploads', 'logos')
                    logo_path = save_uploaded_file(logo_file, upload_folder, 'logo_')
                    settings.logo_image_path = logo_path
                    flash('Logo image uploaded successfully!', 'success')
            
            # Commit changes to database
            db.session.commit()
            
            # Redirect to refresh the page and show updated images
            return redirect(url_for('admin.site_settings'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating site settings: {str(e)}', 'error')
    
    return render_template('admin/settings.html', form=form, settings=settings)



# ============================================================================
# Instructor Profile Management Routes
# ============================================================================

@admin_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def instructor_profile():
    """
    Manage instructor profile.
    
    GET: Load current user's profile and display InstructorProfileForm
    POST: Validate, handle photo upload, check head instructor logic, update database
    
    If setting is_head_instructor=True, unset for all other instructors to ensure
    only one head instructor at a time.
    
    Implements:
    - Requirement 18.1: Provide profile management section for each instructor user
    - Requirement 18.2: Allow uploading one profile photo
    - Requirement 18.3: Provide text field for biography/about information
    - Requirement 18.4: Provide field for title/designation
    - Requirement 18.5: Include checkbox to designate instructor as head instructor
    - Requirement 18.6: Validate profile photo file type (JPEG, PNG, GIF, WebP)
    - Requirement 18.7: Store image file and update InstructorProfile in database
    - Requirement 18.8: Validate biography text length (10-5000 characters)
    - Requirement 18.9: Display confirmation message on save
    - Requirement 18.10: Display preview of current profile photo and information
    - Requirement 18.11: Allow removing profile photo to revert to default placeholder
    - Requirement 18.12: Only one instructor designated as head instructor at a time
    - Requirement 18.13: Remove head instructor designation from other instructors when setting new one
    - Requirement 18.14: Implement CSRF protection
    - Requirement 16.1: Redirect unauthenticated users to login page
    - Requirement 16.3: Verify instructor authentication on every admin request
    
    Returns:
        GET: Rendered profile management form template with current profile data
        POST: Redirect to profile page on success, or re-render form with errors
    """
    # Get or create instructor profile for current user
    profile = InstructorProfile.query.filter_by(user_id=current_user.id).first()
    
    if not profile:
        # Create new profile if doesn't exist
        profile = InstructorProfile(
            user_id=current_user.id,
            biography='',
            title='Instructor',
            is_head_instructor=False
        )
        db.session.add(profile)
        db.session.commit()
    
    form = InstructorProfileForm(obj=profile)
    
    if form.validate_on_submit():
        try:
            # Handle photo removal
            if form.remove_photo.data and profile.photo_path:
                if delete_file(profile.photo_path):
                    profile.photo_path = None
                    flash('Profile photo removed successfully!', 'success')
            
            # Handle photo upload
            if form.photo.data and form.photo.data.filename:
                photo_file = form.photo.data
                
                # Validate the photo
                is_valid, error_message = validate_image_file(photo_file, ALLOWED_IMAGE_EXTENSIONS)
                if not is_valid:
                    flash(f'Photo upload error: {error_message}', 'error')
                else:
                    # Delete old photo if exists
                    if profile.photo_path:
                        delete_file(profile.photo_path)
                    
                    # Save new photo
                    upload_folder = os.path.join('app', 'static', 'uploads', 'profiles')
                    photo_path = save_uploaded_file(photo_file, upload_folder, 'profile_')
                    profile.photo_path = photo_path
                    flash('Profile photo uploaded successfully!', 'success')
            
            # Update biography and title
            profile.biography = form.biography.data
            profile.title = form.title.data
            
            # Handle head instructor designation
            # If setting this instructor as head instructor, unset all others
            if form.is_head_instructor.data and not profile.is_head_instructor:
                # Unset head instructor flag for all other instructors
                InstructorProfile.query.filter(
                    InstructorProfile.id != profile.id
                ).update({'is_head_instructor': False})
                profile.is_head_instructor = True
                flash('You have been designated as the Head Instructor!', 'success')
            elif not form.is_head_instructor.data and profile.is_head_instructor:
                # User is removing their head instructor status
                profile.is_head_instructor = False
                flash('Head Instructor designation removed.', 'info')
            else:
                # No change to head instructor status
                profile.is_head_instructor = form.is_head_instructor.data
            
            # Commit changes to database
            db.session.commit()
            
            if not any(cat == 'success' for cat, _ in get_flashed_messages(with_categories=True)):
                flash('Profile updated successfully!', 'success')
            
            # Redirect to refresh the page and show updated profile
            return redirect(url_for('admin.instructor_profile'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'error')
    
    return render_template('admin/profile.html', form=form, profile=profile)
