"""
Unit tests for file upload utility functions.

Tests cover:
- File extension validation
- Image file validation (type, size, content)
- File saving with secure filenames
- File deletion
- Edge cases and error handling
"""

import os
import pytest
from io import BytesIO
from PIL import Image
from werkzeug.datastructures import FileStorage
from app.file_utils import (
    allowed_file,
    validate_image_file,
    save_uploaded_file,
    delete_file,
    get_file_size_mb,
    ALLOWED_IMAGE_EXTENSIONS,
    ALLOWED_LOGO_EXTENSIONS,
    MAX_FILE_SIZE
)


class TestAllowedFile:
    """Test the allowed_file function."""
    
    def test_allowed_extension_jpg(self):
        """Test that JPG files are allowed."""
        assert allowed_file('photo.jpg', ALLOWED_IMAGE_EXTENSIONS) is True
    
    def test_allowed_extension_jpeg(self):
        """Test that JPEG files are allowed."""
        assert allowed_file('photo.jpeg', ALLOWED_IMAGE_EXTENSIONS) is True
    
    def test_allowed_extension_png(self):
        """Test that PNG files are allowed."""
        assert allowed_file('photo.png', ALLOWED_IMAGE_EXTENSIONS) is True
    
    def test_allowed_extension_gif(self):
        """Test that GIF files are allowed."""
        assert allowed_file('photo.gif', ALLOWED_IMAGE_EXTENSIONS) is True
    
    def test_allowed_extension_webp(self):
        """Test that WebP files are allowed."""
        assert allowed_file('photo.webp', ALLOWED_IMAGE_EXTENSIONS) is True
    
    def test_allowed_extension_svg_for_logo(self):
        """Test that SVG files are allowed for logos."""
        assert allowed_file('logo.svg', ALLOWED_LOGO_EXTENSIONS) is True
    
    def test_disallowed_extension_pdf(self):
        """Test that PDF files are not allowed."""
        assert allowed_file('document.pdf', ALLOWED_IMAGE_EXTENSIONS) is False
    
    def test_disallowed_extension_exe(self):
        """Test that executable files are not allowed."""
        assert allowed_file('malware.exe', ALLOWED_IMAGE_EXTENSIONS) is False
    
    def test_case_insensitive(self):
        """Test that extension checking is case-insensitive."""
        assert allowed_file('photo.JPG', ALLOWED_IMAGE_EXTENSIONS) is True
        assert allowed_file('photo.PNG', ALLOWED_IMAGE_EXTENSIONS) is True
    
    def test_no_extension(self):
        """Test that files without extensions are rejected."""
        assert allowed_file('photo', ALLOWED_IMAGE_EXTENSIONS) is False
    
    def test_empty_filename(self):
        """Test that empty filenames are rejected."""
        assert allowed_file('', ALLOWED_IMAGE_EXTENSIONS) is False
    
    def test_none_filename(self):
        """Test that None filenames are rejected."""
        assert allowed_file(None, ALLOWED_IMAGE_EXTENSIONS) is False
    
    def test_multiple_dots_in_filename(self):
        """Test that files with multiple dots use the last extension."""
        assert allowed_file('my.photo.jpg', ALLOWED_IMAGE_EXTENSIONS) is True
        assert allowed_file('my.photo.pdf', ALLOWED_IMAGE_EXTENSIONS) is False


class TestValidateImageFile:
    """Test the validate_image_file function."""
    
    def create_test_image(self, format='JPEG', size=(100, 100)):
        """Helper to create a test image in memory."""
        img = Image.new('RGB', size, color='red')
        img_io = BytesIO()
        img.save(img_io, format=format)
        img_io.seek(0)
        return img_io
    
    def test_valid_jpeg_image(self):
        """Test that valid JPEG images pass validation."""
        img_data = self.create_test_image('JPEG')
        file = FileStorage(stream=img_data, filename='test.jpg', content_type='image/jpeg')
        
        is_valid, error = validate_image_file(file, ALLOWED_IMAGE_EXTENSIONS)
        assert is_valid is True
        assert error is None
    
    def test_valid_png_image(self):
        """Test that valid PNG images pass validation."""
        img_data = self.create_test_image('PNG')
        file = FileStorage(stream=img_data, filename='test.png', content_type='image/png')
        
        is_valid, error = validate_image_file(file, ALLOWED_IMAGE_EXTENSIONS)
        assert is_valid is True
        assert error is None
    
    def test_no_file_selected(self):
        """Test that missing file is rejected."""
        file = FileStorage(stream=None, filename='', content_type='')
        
        is_valid, error = validate_image_file(file, ALLOWED_IMAGE_EXTENSIONS)
        assert is_valid is False
        assert error == "No file selected"
    
    def test_invalid_extension(self):
        """Test that files with invalid extensions are rejected."""
        file = FileStorage(stream=BytesIO(b'test'), filename='test.pdf', content_type='application/pdf')
        
        is_valid, error = validate_image_file(file, ALLOWED_IMAGE_EXTENSIONS)
        assert is_valid is False
        assert "Invalid file type" in error
    
    def test_empty_file(self):
        """Test that empty files are rejected."""
        file = FileStorage(stream=BytesIO(b''), filename='test.jpg', content_type='image/jpeg')
        
        is_valid, error = validate_image_file(file, ALLOWED_IMAGE_EXTENSIONS)
        assert is_valid is False
        assert error == "File is empty"
    
    def test_file_too_large(self):
        """Test that files exceeding size limit are rejected."""
        # Create a large file (larger than MAX_FILE_SIZE)
        large_data = BytesIO(b'x' * (MAX_FILE_SIZE + 1))
        file = FileStorage(stream=large_data, filename='test.jpg', content_type='image/jpeg')
        
        is_valid, error = validate_image_file(file, ALLOWED_IMAGE_EXTENSIONS)
        assert is_valid is False
        assert "File too large" in error
    
    def test_invalid_image_content(self):
        """Test that files with invalid image content are rejected."""
        # Create a file with .jpg extension but invalid content
        invalid_data = BytesIO(b'This is not an image')
        file = FileStorage(stream=invalid_data, filename='test.jpg', content_type='image/jpeg')
        
        is_valid, error = validate_image_file(file, ALLOWED_IMAGE_EXTENSIONS)
        assert is_valid is False
        assert "Invalid image file" in error
    
    def test_svg_file_skips_pillow_validation(self):
        """Test that SVG files skip Pillow validation."""
        # SVG files can't be validated by Pillow, so they should pass basic checks
        svg_data = BytesIO(b'<svg></svg>')
        file = FileStorage(stream=svg_data, filename='test.svg', content_type='image/svg+xml')
        
        is_valid, error = validate_image_file(file, ALLOWED_LOGO_EXTENSIONS)
        assert is_valid is True
        assert error is None


class TestSaveUploadedFile:
    """Test the save_uploaded_file function."""
    
    def create_test_image(self, format='JPEG'):
        """Helper to create a test image in memory."""
        img = Image.new('RGB', (100, 100), color='blue')
        img_io = BytesIO()
        img.save(img_io, format=format)
        img_io.seek(0)
        return img_io
    
    def test_save_file_with_unique_name(self, tmp_path):
        """Test that files are saved with unique UUID-based names."""
        img_data = self.create_test_image()
        file = FileStorage(stream=img_data, filename='test.jpg', content_type='image/jpeg')
        
        upload_folder = str(tmp_path / 'uploads')
        relative_path = save_uploaded_file(file, upload_folder)
        
        # Check that file was saved
        full_path = os.path.join(upload_folder, os.path.basename(relative_path))
        assert os.path.exists(full_path)
        
        # Check that filename contains UUID (32 hex chars)
        filename = os.path.basename(relative_path)
        assert len(filename.split('.')[0]) == 32  # UUID hex is 32 chars
        assert filename.endswith('.jpg')
    
    def test_save_file_with_prefix(self, tmp_path):
        """Test that files are saved with specified prefix."""
        img_data = self.create_test_image()
        file = FileStorage(stream=img_data, filename='test.jpg', content_type='image/jpeg')
        
        upload_folder = str(tmp_path / 'uploads')
        relative_path = save_uploaded_file(file, upload_folder, prefix='banner_')
        
        # Check that filename has prefix
        filename = os.path.basename(relative_path)
        assert filename.startswith('banner_')
    
    def test_save_file_creates_directory(self, tmp_path):
        """Test that upload directory is created if it doesn't exist."""
        img_data = self.create_test_image()
        file = FileStorage(stream=img_data, filename='test.jpg', content_type='image/jpeg')
        
        upload_folder = str(tmp_path / 'new_folder' / 'uploads')
        relative_path = save_uploaded_file(file, upload_folder)
        
        # Check that directory was created
        assert os.path.exists(upload_folder)
        
        # Check that file was saved
        full_path = os.path.join(upload_folder, os.path.basename(relative_path))
        assert os.path.exists(full_path)
    
    def test_save_file_preserves_extension(self, tmp_path):
        """Test that original file extension is preserved."""
        img_data = self.create_test_image('PNG')
        file = FileStorage(stream=img_data, filename='test.png', content_type='image/png')
        
        upload_folder = str(tmp_path / 'uploads')
        relative_path = save_uploaded_file(file, upload_folder)
        
        # Check that extension is preserved
        assert relative_path.endswith('.png')
    
    def test_save_multiple_files_unique_names(self, tmp_path):
        """Test that multiple files get unique names."""
        upload_folder = str(tmp_path / 'uploads')
        
        # Save two files with same original name
        img_data1 = self.create_test_image()
        file1 = FileStorage(stream=img_data1, filename='test.jpg', content_type='image/jpeg')
        path1 = save_uploaded_file(file1, upload_folder)
        
        img_data2 = self.create_test_image()
        file2 = FileStorage(stream=img_data2, filename='test.jpg', content_type='image/jpeg')
        path2 = save_uploaded_file(file2, upload_folder)
        
        # Check that paths are different
        assert path1 != path2


class TestDeleteFile:
    """Test the delete_file function."""
    
    def test_delete_existing_file(self, tmp_path, monkeypatch):
        """Test that existing files are deleted successfully."""
        # Create a test file in a mock static folder
        static_folder = tmp_path / 'app' / 'static'
        static_folder.mkdir(parents=True)
        test_file = static_folder / 'test.txt'
        test_file.write_text('test content')
        
        # Change working directory context for the test
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        
        try:
            result = delete_file('test.txt')
            assert result is True
            assert not test_file.exists()
        finally:
            os.chdir(original_cwd)
    
    def test_delete_nonexistent_file(self):
        """Test that deleting non-existent file returns False."""
        result = delete_file('nonexistent/file.jpg')
        assert result is False
    
    def test_delete_empty_path(self):
        """Test that empty path returns False."""
        result = delete_file('')
        assert result is False
    
    def test_delete_none_path(self):
        """Test that None path returns False."""
        result = delete_file(None)
        assert result is False


class TestGetFileSizeMb:
    """Test the get_file_size_mb function."""
    
    def test_file_size_calculation(self):
        """Test that file size is calculated correctly."""
        # Create a 1KB file
        data = BytesIO(b'x' * 1024)
        file = FileStorage(stream=data, filename='test.txt')
        
        size_mb = get_file_size_mb(file)
        assert abs(size_mb - 0.0009765625) < 0.0001  # 1KB = 0.0009765625 MB
    
    def test_empty_file_size(self):
        """Test that empty file returns 0 MB."""
        data = BytesIO(b'')
        file = FileStorage(stream=data, filename='test.txt')
        
        size_mb = get_file_size_mb(file)
        assert size_mb == 0.0
    
    def test_large_file_size(self):
        """Test file size calculation for larger files."""
        # Create a 5MB file
        data = BytesIO(b'x' * (5 * 1024 * 1024))
        file = FileStorage(stream=data, filename='test.txt')
        
        size_mb = get_file_size_mb(file)
        assert abs(size_mb - 5.0) < 0.01  # Should be approximately 5MB


class TestFileUtilsIntegration:
    """Integration tests for file upload workflow."""
    
    def create_test_image(self, format='JPEG'):
        """Helper to create a test image in memory."""
        img = Image.new('RGB', (100, 100), color='green')
        img_io = BytesIO()
        img.save(img_io, format=format)
        img_io.seek(0)
        return img_io
    
    def test_complete_upload_workflow(self, tmp_path):
        """Test complete workflow: validate, save, verify."""
        # Create test image
        img_data = self.create_test_image()
        file = FileStorage(stream=img_data, filename='test.jpg', content_type='image/jpeg')
        
        # Validate
        is_valid, error = validate_image_file(file, ALLOWED_IMAGE_EXTENSIONS)
        assert is_valid is True
        assert error is None
        
        # Save
        upload_folder = str(tmp_path / 'uploads')
        relative_path = save_uploaded_file(file, upload_folder)
        
        # Verify file exists
        full_path = os.path.join(upload_folder, os.path.basename(relative_path))
        assert os.path.exists(full_path)
        
        # Verify it's a valid image
        saved_image = Image.open(full_path)
        assert saved_image.size == (100, 100)
        assert saved_image.mode == 'RGB'
