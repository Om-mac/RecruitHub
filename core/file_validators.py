"""
File upload validators and handlers for S3 security
Enforces file type and size restrictions
"""

import os
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# Allowed MIME types
ALLOWED_RESUME_TYPES = {'application/pdf'}  # Only PDF for resumes
ALLOWED_PHOTO_TYPES = {'image/jpeg', 'image/png'}  # JPG and PNG for photos
ALLOWED_DOCUMENT_TYPES = {'application/pdf', 'image/jpeg', 'image/png'}

# File extensions mapping
EXTENSION_TO_MIME = {
    'pdf': 'application/pdf',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
}

# Blocked extensions
BLOCKED_EXTENSIONS = {'exe', 'zip', 'js', 'html', 'htm', 'dll', 'bat', 'cmd', 'sh'}

# File size limits (in bytes)
MAX_RESUME_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_PHOTO_SIZE = 1 * 1024 * 1024  # 1 MB
MAX_DOCUMENT_SIZE = 5 * 1024 * 1024  # 5 MB


def get_file_extension(filename):
    """Get file extension from filename (lowercase)"""
    if not filename:
        return ''
    return os.path.splitext(filename)[1].lstrip('.').lower()


def get_mime_type_from_extension(filename):
    """Get MIME type from file extension"""
    ext = get_file_extension(filename)
    return EXTENSION_TO_MIME.get(ext, 'application/octet-stream')


def validate_resume_file(file):
    """
    Validate resume file:
    - Must be PDF
    - Maximum 5 MB
    """
    if not file:
        return

    # Check file extension
    ext = get_file_extension(file.name)
    if ext not in ['pdf']:
        raise ValidationError(
            _('Resume must be a PDF file. Received: .%(ext)s'),
            code='invalid_extension',
            params={'ext': ext},
        )

    # Check file size
    if file.size > MAX_RESUME_SIZE:
        max_size_mb = MAX_RESUME_SIZE / (1024 * 1024)
        raise ValidationError(
            _('Resume file is too large. Maximum size: %(max_size)s MB. Your file: %(file_size)s MB'),
            code='file_too_large',
            params={
                'max_size': int(max_size_mb),
                'file_size': round(file.size / (1024 * 1024), 2),
            },
        )


def validate_profile_photo(file):
    """
    Validate profile photo:
    - Must be JPG or PNG
    - Maximum 1 MB
    """
    if not file:
        return

    # Check file extension
    ext = get_file_extension(file.name)
    if ext not in ['jpg', 'jpeg', 'png']:
        raise ValidationError(
            _('Profile photo must be JPG or PNG. Received: .%(ext)s'),
            code='invalid_extension',
            params={'ext': ext},
        )

    # Check file size
    if file.size > MAX_PHOTO_SIZE:
        max_size_mb = MAX_PHOTO_SIZE / (1024 * 1024)
        raise ValidationError(
            _('Profile photo is too large. Maximum size: %(max_size)s MB. Your file: %(file_size)s MB'),
            code='file_too_large',
            params={
                'max_size': int(max_size_mb),
                'file_size': round(file.size / (1024 * 1024), 2),
            },
        )


def validate_document_file(file):
    """
    Validate document file:
    - Must be PDF, JPG, or PNG
    - Maximum 5 MB
    """
    if not file:
        return

    # Check file extension
    ext = get_file_extension(file.name)
    if ext not in ['pdf', 'jpg', 'jpeg', 'png']:
        raise ValidationError(
            _('Document must be PDF, JPG, or PNG. Received: .%(ext)s'),
            code='invalid_extension',
            params={'ext': ext},
        )

    # Check file size
    if file.size > MAX_DOCUMENT_SIZE:
        max_size_mb = MAX_DOCUMENT_SIZE / (1024 * 1024)
        raise ValidationError(
            _('Document is too large. Maximum size: %(max_size)s MB. Your file: %(file_size)s MB'),
            code='file_too_large',
            params={
                'max_size': int(max_size_mb),
                'file_size': round(file.size / (1024 * 1024), 2),
            },
        )


def is_safe_filename(filename):
    """Check if filename is safe (no path traversal attempts)"""
    if not filename:
        return False
    
    # No path separators or traversal attempts
    if '/' in filename or '\\' in filename or '..' in filename:
        return False
    
    # Check extension is not blocked
    ext = get_file_extension(filename)
    if ext in BLOCKED_EXTENSIONS:
        return False
    
    return True
