"""
Authentication Routes

This module handles user authentication including login and logout.
Implements Requirements 13.1-13.8 (Instructor Authentication).
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.forms import LoginForm

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login page for instructors.
    
    GET: Display login form
    POST: Validate credentials, create session, redirect to admin dashboard
    
    Implements:
    - Requirement 13.1: Provide login page for instructors
    - Requirement 13.2: Require username and password
    - Requirement 13.3: Authenticate user and redirect to admin dashboard on valid credentials
    - Requirement 13.4: Display error message and remain on login page for invalid credentials
    - Requirement 13.5: Implement CSRF protection on login form
    - Requirement 13.7: Maintain instructor session state after successful login
    
    Returns:
        GET: Rendered login.html template with LoginForm
        POST: Redirect to admin dashboard on success, or re-render login form with errors
    """
    # If user is already logged in, redirect to admin dashboard
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        # Query user by username
        user = User.query.filter_by(username=form.username.data).first()
        
        # Verify password using bcrypt check_password()
        if user is None or not user.check_password(form.password.data):
            # Invalid credentials - display error and remain on login page
            flash('Invalid username or password', 'error')
            return render_template('login.html', form=form)
        
        # Valid credentials - log in user and create session
        # Mark session as permanent to enable 30-minute timeout (Requirement 16.4)
        from flask import session
        session.permanent = True
        login_user(user, remember=False)
        
        # Redirect to admin dashboard or to the page user was trying to access
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('admin.dashboard'))
    
    return render_template('login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """
    Logout current user.
    
    Clears the session and redirects to home page.
    
    Implements:
    - Requirement 13.8: Provide logout function that clears the session
    
    Returns:
        Redirect to home page
    """
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('main.home'))
