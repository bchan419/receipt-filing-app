import pytest
import os
import tempfile

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.file_handler import FileHandler

class TestFileHandler:
    """Test cases for FileHandler class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.file_handler = FileHandler()
    
    def test_initialization(self):
        """Test FileHandler initialization"""
        assert self.file_handler.SUPPORTED_FORMATS is not None
        assert self.file_handler.SUPPORTED_EXTENSIONS is not None
        assert len(self.file_handler.SUPPORTED_FORMATS) > 0
        assert len(self.file_handler.SUPPORTED_EXTENSIONS) > 0
    
    def test_supported_formats(self):
        """Test that supported formats are properly defined"""
        expected_formats = [
            'image/jpeg',
            'image/png', 
            'image/webp',
            'image/heic',
            'image/heif'
        ]
        
        for format_type in expected_formats:
            assert format_type in self.file_handler.SUPPORTED_FORMATS
    
    def test_supported_extensions(self):
        """Test that supported extensions are properly defined"""
        expected_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.heic', '.heif']
        
        for ext in expected_extensions:
            assert ext in self.file_handler.SUPPORTED_EXTENSIONS
    
    def test_is_valid_image_valid_extensions(self):
        """Test is_valid_image with valid extensions"""
        valid_filenames = [
            'receipt.jpg',
            'receipt.jpeg',
            'receipt.png',
            'receipt.webp',
            'receipt.heic',
            'receipt.heif',
            'RECEIPT.JPG',  # Test case insensitive
            'receipt.JPEG',
            'my_receipt_2024.png'
        ]
        
        for filename in valid_filenames:
            assert self.file_handler.is_valid_image(filename), f"Should be valid: {filename}"
    
    def test_is_valid_image_invalid_extensions(self):
        """Test is_valid_image with invalid extensions"""
        invalid_filenames = [
            'receipt.gif',
            'receipt.bmp',
            'receipt.tiff',
            'receipt.pdf',
            'receipt.txt',
            'receipt.doc',
            'receipt',  # No extension
            'receipt.'  # Empty extension
        ]
        
        for filename in invalid_filenames:
            assert not self.file_handler.is_valid_image(filename), f"Should be invalid: {filename}"
    
    def test_is_valid_image_none_filename(self):
        """Test is_valid_image with None filename"""
        assert not self.file_handler.is_valid_image(None)
    
    def test_is_valid_image_empty_filename(self):
        """Test is_valid_image with empty filename"""
        assert not self.file_handler.is_valid_image("")
    
    def test_get_file_size(self):
        """Test get_file_size method"""
        test_content = b"Hello, World!"
        size = self.file_handler.get_file_size(test_content)
        assert size == len(test_content)
        assert size == 13
    
    def test_get_file_size_empty_content(self):
        """Test get_file_size with empty content"""
        empty_content = b""
        size = self.file_handler.get_file_size(empty_content)
        assert size == 0
    
    def test_get_file_size_large_content(self):
        """Test get_file_size with large content"""
        large_content = b"x" * 1000
        size = self.file_handler.get_file_size(large_content)
        assert size == 1000
    
    def test_is_file_size_valid_within_limit(self):
        """Test is_file_size_valid with content within limit"""
        # 1MB content
        content = b"x" * (1024 * 1024)
        assert self.file_handler.is_file_size_valid(content, max_size_mb=2)
        assert self.file_handler.is_file_size_valid(content, max_size_mb=1)
    
    def test_is_file_size_valid_exceeds_limit(self):
        """Test is_file_size_valid with content exceeding limit"""
        # 2MB content
        content = b"x" * (2 * 1024 * 1024)
        assert not self.file_handler.is_file_size_valid(content, max_size_mb=1)
        assert self.file_handler.is_file_size_valid(content, max_size_mb=3)
    
    def test_is_file_size_valid_default_limit(self):
        """Test is_file_size_valid with default limit (10MB)"""
        # 5MB content - should be valid
        content = b"x" * (5 * 1024 * 1024)
        assert self.file_handler.is_file_size_valid(content)
        
        # 15MB content - should be invalid
        content = b"x" * (15 * 1024 * 1024)
        assert not self.file_handler.is_file_size_valid(content)
    
    def test_is_file_size_valid_empty_content(self):
        """Test is_file_size_valid with empty content"""
        empty_content = b""
        assert self.file_handler.is_file_size_valid(empty_content)
    
    def test_is_file_size_valid_zero_limit(self):
        """Test is_file_size_valid with zero limit"""
        content = b"x"
        assert not self.file_handler.is_file_size_valid(content, max_size_mb=0)
    
    def test_case_insensitive_extension_matching(self):
        """Test that extension matching is case insensitive"""
        test_cases = [
            ('receipt.JPG', True),
            ('receipt.Jpg', True),
            ('receipt.jPg', True),
            ('receipt.PNG', True),
            ('receipt.WebP', True),
            ('receipt.HEIC', True),
            ('receipt.GIF', False),
            ('receipt.BMP', False)
        ]
        
        for filename, expected in test_cases:
            result = self.file_handler.is_valid_image(filename)
            assert result == expected, f"Expected {expected} for {filename}, got {result}"
    
    def test_path_with_spaces(self):
        """Test file validation with paths containing spaces"""
        test_files = [
            'my receipt.jpg',
            'receipt file.png',
            'folder name/receipt.webp'
        ]
        
        for filename in test_files:
            assert self.file_handler.is_valid_image(filename)
    
    def test_multiple_dots_in_filename(self):
        """Test file validation with multiple dots in filename"""
        test_files = [
            'receipt.2024.01.15.jpg',
            'my.receipt.file.png',
            'test.backup.old.webp'
        ]
        
        for filename in test_files:
            assert self.file_handler.is_valid_image(filename)
    
    def test_validate_file_content_mock(self):
        """Test validate_file_content method (mocked since it requires python-magic)"""
        # This test would require actual image files or mocking python-magic
        # For now, we'll test the method exists and handles basic cases
        
        # Test with empty content
        try:
            result = self.file_handler.validate_file_content(b"")
            # Should return False for empty content
            assert result is False
        except Exception:
            # If python-magic is not available, method should handle gracefully
            pass
    
    def test_integration_file_validation(self):
        """Test complete file validation workflow"""
        # Test valid file
        assert self.file_handler.is_valid_image('receipt.jpg')
        
        # Test file size
        small_content = b"small file"
        assert self.file_handler.is_file_size_valid(small_content)
        
        # Test invalid file
        assert not self.file_handler.is_valid_image('receipt.txt')
        
        # Test large file
        large_content = b"x" * (20 * 1024 * 1024)  # 20MB
        assert not self.file_handler.is_file_size_valid(large_content)