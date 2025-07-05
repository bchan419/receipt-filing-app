import os
import magic
from typing import List

class FileHandler:
    """Handle file operations and validation"""
    
    SUPPORTED_FORMATS = [
        'image/jpeg',
        'image/png', 
        'image/webp',
        'image/heic',
        'image/heif'
    ]
    
    SUPPORTED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp', '.heic', '.heif']
    
    def is_valid_image(self, filename: str) -> bool:
        """Check if file is a supported image format"""
        if not filename:
            return False
        
        # Check by extension
        ext = os.path.splitext(filename.lower())[1]
        return ext in self.SUPPORTED_EXTENSIONS
    
    def validate_file_content(self, file_content: bytes) -> bool:
        """Validate file content using magic numbers"""
        try:
            mime_type = magic.from_buffer(file_content, mime=True)
            return mime_type in self.SUPPORTED_FORMATS
        except:
            return False
    
    def get_file_size(self, file_content: bytes) -> int:
        """Get file size in bytes"""
        return len(file_content)
    
    def is_file_size_valid(self, file_content: bytes, max_size_mb: int = 10) -> bool:
        """Check if file size is within limits"""
        max_size_bytes = max_size_mb * 1024 * 1024
        return self.get_file_size(file_content) <= max_size_bytes