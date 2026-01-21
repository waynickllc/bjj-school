"""
Error handlers for the BJJ School Website.

This module provides custom error handlers for common HTTP errors
with logging and user-friendly error pages.
"""

import logging
import traceback
from flask import render_template, request
from werkzeug.exceptions import HTTPException


# Configure logger
logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """
    Register custom error handlers with the Flask application.
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(400)
    def bad_request_error(error):
        """
        Handle 400 Bad Request errors (including CSRF failures).
        
        Args:
            error: The error object
            
        Returns:
            Tuple of (rendered template, status code)
        """
        # Log the error with request context
        log_error(400, error, "Bad Request")
        
        # Get error description if available
        description = None
        if isinstance(error, HTTPException):
            description = error.description
        
        # Render custom 400 error page
        return render_template('errors/400.html', description=description), 400
    
    @app.errorhandler(404)
    def not_found_error(error):
        """
        Handle 404 Not Found errors.
        
        Args:
            error: The error object
            
        Returns:
            Tuple of (rendered template, status code)
        """
        # Log the error with request context
        log_error(404, error, "Page Not Found")
        
        # Render custom 404 error page
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """
        Handle 500 Internal Server Error.
        
        Args:
            error: The error object
            
        Returns:
            Tuple of (rendered template, status code)
        """
        # Log the error with full stack trace and request context
        log_error(500, error, "Internal Server Error", include_traceback=True)
        
        # Render custom 500 error page
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """
        Handle any unexpected exceptions that aren't caught elsewhere.
        
        Args:
            error: The error object
            
        Returns:
            Tuple of (rendered template, status code)
        """
        # Log the unexpected error with full details
        log_error(500, error, "Unexpected Error", include_traceback=True)
        
        # Render custom 500 error page
        return render_template('errors/500.html'), 500


def log_error(status_code, error, error_type, include_traceback=False):
    """
    Log error with request context information.
    
    Args:
        status_code: HTTP status code
        error: The error object
        error_type: String describing the error type
        include_traceback: Whether to include full stack trace
    """
    # Build error context
    error_context = {
        'error_type': error_type,
        'status_code': status_code,
        'error_message': str(error),
        'url': request.url,
        'method': request.method,
        'remote_addr': request.remote_addr,
        'user_agent': request.user_agent.string if request.user_agent else 'Unknown',
        'referrer': request.referrer or 'Direct',
    }
    
    # Add form data for POST requests (excluding sensitive fields)
    if request.method == 'POST':
        # Get form data but exclude password fields and CSRF tokens
        form_data = {
            key: value for key, value in request.form.items()
            if key not in ['password', 'csrf_token', 'confirm_password']
        }
        if form_data:
            error_context['form_data'] = form_data
    
    # Format log message
    log_message = (
        f"{error_type} ({status_code}): {error}\n"
        f"URL: {error_context['url']}\n"
        f"Method: {error_context['method']}\n"
        f"Remote Address: {error_context['remote_addr']}\n"
        f"User Agent: {error_context['user_agent']}\n"
        f"Referrer: {error_context['referrer']}"
    )
    
    # Add form data to log if present
    if 'form_data' in error_context:
        log_message += f"\nForm Data: {error_context['form_data']}"
    
    # Log based on severity
    if status_code >= 500:
        if include_traceback:
            # Log with full stack trace for server errors
            logger.error(log_message, exc_info=True)
        else:
            logger.error(log_message)
    elif status_code >= 400:
        # Log as warning for client errors
        logger.warning(log_message)
    else:
        # Log as info for other cases
        logger.info(log_message)
