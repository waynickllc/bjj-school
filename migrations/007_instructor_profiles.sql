-- Migration 007: Add instructor_profiles table
-- This SQL file documents the database changes for reference
-- The actual migration is managed by Alembic in migrations/versions/007_add_instructor_profiles_table.py

-- Create instructor_profiles table
CREATE TABLE instructor_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    photo_path VARCHAR(255),
    biography TEXT NOT NULL,
    title VARCHAR(100) NOT NULL,
    is_head_instructor BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_is_head_instructor (is_head_instructor)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Note: Biography length constraint (10-5000 characters) is enforced at the application level
-- In production MySQL, you can add this constraint:
-- ALTER TABLE instructor_profiles ADD CONSTRAINT chk_biography_length 
-- CHECK (CHAR_LENGTH(biography) >= 10 AND CHAR_LENGTH(biography) <= 5000);
