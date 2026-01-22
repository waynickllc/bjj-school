#!/usr/bin/env python
"""
Admin User Initialization Script

This script creates an initial admin user account for the BJJ school website.
It can be run interactively (prompting for credentials) or with command-line arguments.

Usage:
    # Interactive mode (prompts for all inputs)
    python init_admin.py

    # With command-line arguments
    python init_admin.py --username admin --email admin@example.com

    # With all arguments (will still prompt for password securely)
    python init_admin.py --username admin --email admin@example.com --password

Requirements: 12, 15
"""

import sys
import argparse
import getpass
from app import create_app, db
from app.models import User, InstructorProfile


def validate_email(email):
    """
    Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """
    Validate password strength.
    
    Password must be at least 8 characters long.
    
    Args:
        password: Password to validate
        
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    return True, ""


def create_admin_user(username, email, password, biography=None, title=None, is_head_instructor=False):
    """
    Create an admin user with an instructor profile.
    
    Args:
        username: Username for login
        email: Email address
        password: Plain text password (will be hashed)
        biography: Optional biography text (default provided if None)
        title: Optional title/designation (default: "Instructor")
        is_head_instructor: Whether this is the head instructor (default: False)
        
    Returns:
        tuple: (bool, str) - (success, message)
    """
    app = create_app()
    
    with app.app_context():
        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return False, f"Error: Username '{username}' already exists"
        
        # Check if email already exists
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            return False, f"Error: Email '{email}' is already registered"
        
        try:
            # Create user
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.flush()  # Get user.id without committing
            
            # Create instructor profile with default values if not provided
            if biography is None:
                biography = f"Instructor at the BJJ school. Passionate about teaching Brazilian Jiu-Jitsu and helping students achieve their goals."
            
            if title is None:
                title = "Instructor"
            
            # If setting as head instructor, unset any existing head instructor
            if is_head_instructor:
                existing_head = InstructorProfile.query.filter_by(is_head_instructor=True).first()
                if existing_head:
                    existing_head.is_head_instructor = False
                    print(f"Note: Removed head instructor designation from user ID {existing_head.user_id}")
            
            profile = InstructorProfile(
                user_id=user.id,
                biography=biography,
                title=title,
                is_head_instructor=is_head_instructor
            )
            db.session.add(profile)
            
            # Commit transaction
            db.session.commit()
            
            head_status = " (Head Instructor)" if is_head_instructor else ""
            return True, f"Success: Admin user '{username}' created successfully{head_status}"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error creating user: {str(e)}"


def interactive_mode():
    """
    Run the script in interactive mode, prompting for all inputs.
    
    Returns:
        tuple: (username, email, password, biography, title, is_head_instructor)
    """
    print("=" * 60)
    print("BJJ School Website - Admin User Creation")
    print("=" * 60)
    print()
    
    # Get username
    while True:
        username = input("Enter username: ").strip()
        if username:
            break
        print("Error: Username cannot be empty")
    
    # Get email
    while True:
        email = input("Enter email address: ").strip()
        if not email:
            print("Error: Email cannot be empty")
            continue
        if not validate_email(email):
            print("Error: Invalid email format")
            continue
        break
    
    # Get password
    while True:
        password = getpass.getpass("Enter password (min 8 characters): ")
        if not password:
            print("Error: Password cannot be empty")
            continue
        
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            print(f"Error: {error_msg}")
            continue
        
        password_confirm = getpass.getpass("Confirm password: ")
        if password != password_confirm:
            print("Error: Passwords do not match")
            continue
        break
    
    # Get optional profile information
    print()
    print("Optional: Instructor Profile Information")
    print("(Press Enter to use defaults)")
    print()
    
    title = input("Enter title/designation [Instructor]: ").strip()
    if not title:
        title = "Instructor"
    
    print()
    print("Enter biography (press Enter twice when done):")
    print("(Leave empty to use default biography)")
    biography_lines = []
    empty_count = 0
    while empty_count < 2:
        line = input()
        if not line:
            empty_count += 1
        else:
            empty_count = 0
            biography_lines.append(line)
    
    biography = "\n".join(biography_lines).strip()
    if not biography:
        biography = None  # Use default
    
    # Ask about head instructor status
    print()
    is_head = input("Is this the head instructor? (y/N): ").strip().lower()
    is_head_instructor = is_head in ['y', 'yes']
    
    return username, email, password, biography, title, is_head_instructor


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Create an admin user for the BJJ school website',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (prompts for all inputs)
  python init_admin.py

  # Specify username and email (will prompt for password)
  python init_admin.py --username admin --email admin@example.com

  # Specify all details including head instructor status
  python init_admin.py --username professor --email prof@example.com --head-instructor
        """
    )
    
    parser.add_argument('--username', help='Username for the admin account')
    parser.add_argument('--email', help='Email address for the admin account')
    parser.add_argument('--password', action='store_true', 
                       help='Prompt for password (always prompts securely, this flag is for clarity)')
    parser.add_argument('--title', help='Title/designation (default: Instructor)')
    parser.add_argument('--biography', help='Biography text')
    parser.add_argument('--head-instructor', action='store_true',
                       help='Designate this user as the head instructor')
    
    args = parser.parse_args()
    
    # Determine if we need interactive mode
    if not args.username or not args.email:
        # Interactive mode
        username, email, password, biography, title, is_head_instructor = interactive_mode()
    else:
        # Command-line mode with prompts for missing info
        username = args.username
        email = args.email
        
        # Validate email
        if not validate_email(email):
            print(f"Error: Invalid email format: {email}")
            sys.exit(1)
        
        # Always prompt for password securely
        print(f"Creating admin user: {username} ({email})")
        while True:
            password = getpass.getpass("Enter password (min 8 characters): ")
            if not password:
                print("Error: Password cannot be empty")
                continue
            
            is_valid, error_msg = validate_password(password)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue
            
            password_confirm = getpass.getpass("Confirm password: ")
            if password != password_confirm:
                print("Error: Passwords do not match")
                continue
            break
        
        biography = args.biography
        title = args.title
        is_head_instructor = args.head_instructor
    
    # Create the user
    print()
    print("Creating admin user...")
    success, message = create_admin_user(
        username=username,
        email=email,
        password=password,
        biography=biography,
        title=title,
        is_head_instructor=is_head_instructor
    )
    
    print()
    print(message)
    
    if success:
        print()
        print("You can now log in at: http://localhost:5000/login")
        print(f"Username: {username}")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
