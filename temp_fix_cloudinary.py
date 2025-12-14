#!/usr/bin/env python3
"""
Temporary script to replace CloudinaryField with ImageField for development
"""

import os
import re

def replace_cloudinary_fields(file_path):
    """Replace CloudinaryField with ImageField in a Python file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace CloudinaryField imports
    content = re.sub(
        r'from cloudinary\.models import CloudinaryField',
        '# from cloudinary.models import CloudinaryField  # Temporarily disabled',
        content
    )
    
    # Replace CloudinaryField declarations with ImageField
    # Pattern for video files
    content = re.sub(
        r'CloudinaryField\(\'video\'[^)]*\)',
        'models.FileField(upload_to=\'videos/\', blank=True, null=True)',
        content
    )
    
    # Pattern for audio files
    content = re.sub(
        r'CloudinaryField\(\'audio\'[^)]*\)',
        'models.FileField(upload_to=\'audio/\', blank=True, null=True)',
        content
    )
    
    # Pattern for image files
    content = re.sub(
        r'CloudinaryField\(\'image\'[^)]*\)',
        'models.ImageField(upload_to=\'images/\', blank=True, null=True)',
        content
    )
    
    # Generic CloudinaryField replacement
    content = re.sub(
        r'CloudinaryField\([^)]*\)',
        'models.ImageField(upload_to=\'images/\', blank=True, null=True)',
        content
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed CloudinaryField in {file_path}")

def main():
    """Find and fix all Python files with CloudinaryField"""
    model_files = [
        'accounts/models.py',
        'elearning/models.py',
        'reporting/models.py',
        'gamification/models.py',
        'community/models.py',
        'collaboration/models.py',
    ]
    
    for file_path in model_files:
        if os.path.exists(file_path):
            replace_cloudinary_fields(file_path)
        else:
            print(f"File not found: {file_path}")

if __name__ == '__main__':
    main()