"""
File upload utility functions for handling image uploads.

This module provides helper functions for validating, saving, and deleting
uploaded files. It includes support for file type validation, size limits,
and secure filename handling.
"""

import os
import uuid
from typing import Optional, Set
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from PIL import Image


# Configuration constants
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes
UPLOAD_FOLDER = 'app/static/uploads'

# Allowed file extensions by category
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
ALLOWED_LOGO_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'}


def allowed_file(filename: str, allowed_extensions: Set[str]) -> bool:
    """
    Check if file extension is allowed.
    
    Args:
        filename: Name of uploaded file
        allowed_extensions: Set of allowed extensions (e.g., {'jpg', 'png'})
        
    Returns:
        bool: True if extension is allowed, False otherwise
        
    Example:
        >>> allowed_file('photo.jpg', {'jpg', 'png'})
        True
        >>> allowed_file('document.pdf', {'jpg', 'png'})
        False
    """
    if not filename or '.' not in filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in allowed_extensions


def validate_image_file(file: FileStorage, allowed_extensions: Set[str]) -> tuple[bool, Optional[str]]:
    """
    Validate an uploaded image file.
    
    Checks:
    - File has an allowed extension
    - File is not empty
    - File size is within limits
    - File is a valid image (using Pillow)
    
    Args:
        file: FileStorage object from request.files
        allowed_extensions: Set of allowed file extensions
        
    Returns:
        tuple: (is_valid, error_message)
            - is_valid: True if file is valid, False otherwise
            - error_message: Description of validation error, or None if valid
            
    Example:
        >>> is_valid, error = validate_image_file(file, ALLOWED_IMAGE_EXTENSIONS)
        >>> if not is_valid:
        ...     flash(error, 'error')
    """
    # Check if file exists
    if not file or not file.filename:
        return False, "No file selected"
    
    # Check file extension
    if not allowed_file(file.filename, allowed_extensions):
        extensions_str = ', '.join(sorted(allowed_extensions))
        return False, f"Invalid file type. Allowed types: {extensions_str.upper()}"
    
    # Check file size by reading content
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reset file pointer
    
    if file_size == 0:
        return False, "File is empty"
    
    if file_size > MAX_FILE_SIZE:
        max_size_mb = MAX_FILE_SIZE / (1024 * 1024)
        return False, f"File too large. Maximum size: {max_size_mb}MB"
    
    # For non-SVG files, validate using Pillow
    extension = file.filename.rsplit('.', 1)[1].lower()
    if extension != 'svg':
        try:
            # Try to open and verify the image
            image = Image.open(file.stream)
            image.verify()
            file.seek(0)  # Reset file pointer after verification
        except Exception as e:
            return False, f"Invalid image file: {str(e)}"
    
    return True, None


def save_uploaded_file(file: FileStorage, upload_folder: str, prefix: str = '') -> str:
    """
    Save uploaded file with secure filename.
    
    The file is saved with a UUID-based name to prevent conflicts and
    security issues. The original extension is preserved.
    
    Args:
        file: FileStorage object from request.files
        upload_folder: Destination folder path (relative to app root)
        prefix: Optional prefix for filename (e.g., 'banner_', 'profile_')
        
    Returns:
        str: Relative path to saved file (e.g., 'uploads/banners/uuid.jpg')
        
    Raises:
        ValueError: If file type not allowed or file too large
        IOError: If file cannot be saved
        
    Example:
        >>> file_path = save_uploaded_file(file, 'app/static/uploads/banners', 'banner_')
        >>> # Returns: 'uploads/banners/banner_abc123.jpg'
    """
    # Ensure upload folder exists
    os.makedirs(upload_folder, exist_ok=True)
    
    # Get file extension
    original_filename = secure_filename(file.filename)
    extension = original_filename.rsplit('.', 1)[1].lower()
    
    # Generate unique filename with UUID
    unique_filename = f"{prefix}{uuid.uuid4().hex}.{extension}"
    
    # Full path for saving
    file_path = os.path.join(upload_folder, unique_filename)
    
    # Save the file
    file.save(file_path)
    
    # Return relative path for storing in database
    # Remove 'app/static/' or 'app\static\' prefix and normalize to forward slashes
    if file_path.startswith('app/static/'):
        relative_path = file_path[11:]  # Remove 'app/static/'
    elif file_path.startswith('app\\static\\'):
        relative_path = file_path[12:]  # Remove 'app\static\'
    else:
        # Fallback: try to find and remove the static prefix
        relative_path = file_path.replace('app/static/', '').replace('app\\static\\', '')
    
    # Normalize to forward slashes for consistency
    relative_path = relative_path.replace('\\', '/')
    return relative_path


def delete_file(file_path: str) -> bool:
    """
    Delete file from filesystem.
    
    Args:
        file_path: Path to file to delete (relative to static folder)
        
    Returns:
        bool: True if deleted successfully, False if file doesn't exist
        
    Example:
        >>> delete_file('uploads/banners/old_banner.jpg')
        True
    """
    if not file_path:
        return False
    
    # Construct full path
    full_path = os.path.join('app/static', file_path)
    
    # Check if file exists and delete
    if os.path.exists(full_path):
        try:
            os.remove(full_path)
            return True
        except OSError:
            return False
    
    return False


def get_file_size_mb(file: FileStorage) -> float:
    """
    Get file size in megabytes.
    
    Args:
        file: FileStorage object from request.files
        
    Returns:
        float: File size in MB
        
    Example:
        >>> size_mb = get_file_size_mb(file)
        >>> print(f"File size: {size_mb:.2f}MB")
    """
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reset file pointer
    
    return file_size / (1024 * 1024)
