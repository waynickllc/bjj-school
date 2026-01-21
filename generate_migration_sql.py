"""
Generate SQL Migration Script

This script generates SQL statements for creating the database schema
without requiring a database connection. The generated SQL can be used
to manually create the tables or can be executed by the init_db.py script.

Usage:
    python generate_migration_sql.py > migrations/initial_schema.sql
"""

def generate_sql():
    """Generate SQL statements for initial database schema."""
    
    sql = """-- Initial Migration: ContactSubmission and TrialBooking models
-- Generated for MySQL 8.0+
-- Character set: utf8mb4 (supports full Unicode including emojis)

-- Create contact_submissions table
CREATE TABLE IF NOT EXISTS contact_submissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL,
    phone VARCHAR(20),
    message TEXT NOT NULL,
    submitted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_submitted_at (submitted_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create trial_bookings table
CREATE TABLE IF NOT EXISTS trial_bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    preferred_date DATE NOT NULL,
    preferred_time VARCHAR(50) NOT NULL,
    submitted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_submitted_at (submitted_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Note: The check constraint for future dates (preferred_date >= CURDATE())
-- is enforced at the application level in form validation to maintain
-- compatibility with SQLite for testing. In production MySQL, you can add:
-- ALTER TABLE trial_bookings ADD CONSTRAINT chk_future_date 
--   CHECK (preferred_date >= CURDATE());
"""
    
    return sql


if __name__ == '__main__':
    print(generate_sql())
