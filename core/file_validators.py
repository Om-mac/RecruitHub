"""
File upload validators and handlers for S3 security
Enforces file type and size restrictions with magic byte validation

Security Features:
- Extension whitelist (not blacklist)
- Magic byte validation (prevents extension spoofing)
- File size limits
- Filename sanitization (no path traversal, no special chars)
- Blocked dangerous extensions
"""

import os
import re
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

# Magic bytes for file type validation (prevents extension spoofing)
MAGIC_BYTES = {
    'pdf': b'%PDF',
    'jpg': b'\xff\xd8\xff',
    'jpeg': b'\xff\xd8\xff',
    'png': b'\x89PNG\r\n\x1a\n',
}

# Blocked extensions - ALWAYS reject these regardless of other checks
BLOCKED_EXTENSIONS = {
    'exe', 'zip', 'js', 'html', 'htm', 'dll', 'bat', 'cmd', 'sh', 'php', 
    'jsp', 'asp', 'aspx', 'cgi', 'pl', 'py', 'rb', 'jar', 'war', 'msi',
    'scr', 'vbs', 'wsf', 'ps1', 'psd1', 'psm1', 'reg', 'inf', 'hta',
    'svg', 'xml', 'xhtml', 'swf'  # SVG can contain scripts
}

# File size limits (in bytes)
MAX_RESUME_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_PHOTO_SIZE = 2 * 1024 * 1024  # 2 MB
MAX_DOCUMENT_SIZE = 5 * 1024 * 1024  # 5 MB

# Safe filename pattern - only alphanumeric, dash, underscore, dot
SAFE_FILENAME_PATTERN = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9_\-\.]*$')


def get_file_extension(filename):
    """Get file extension from filename (lowercase)"""
    if not filename:
        return ''
    return os.path.splitext(filename)[1].lstrip('.').lower()


def get_mime_type_from_extension(filename):
    """Get MIME type from file extension"""
    ext = get_file_extension(filename)
    return EXTENSION_TO_MIME.get(ext, 'application/octet-stream')


def sanitize_filename(filename):
    """
    Sanitize filename to prevent security issues:
    - Remove null bytes
    - Remove path traversal attempts
    - Remove special/control characters
    - Limit length
    """
    if not filename:
        raise ValidationError(_('Filename is required.'), code='no_filename')
    
    # Remove null bytes (security: prevents null byte injection)
    filename = filename.replace('\x00', '')
    
    # Remove path separators and traversal
    filename = os.path.basename(filename)
    filename = filename.replace('..', '')
    
    # Remove control characters and non-printable chars
    filename = ''.join(c for c in filename if c.isprintable() and ord(c) < 128)
    
    # Limit filename length (255 is typical filesystem limit)
    if len(filename) > 200:
        ext = get_file_extension(filename)
        base = filename[:195]
        filename = f"{base}.{ext}" if ext else base
    
    if not filename or filename == '.':
        raise ValidationError(_('Invalid filename.'), code='invalid_filename')
    
    return filename


def validate_filename_safety(filename):
    """
    Validate filename is safe for storage:
    - No path traversal
    - No blocked extensions
    - No suspicious patterns
    """
    if not filename:
        raise ValidationError(_('Filename is required.'), code='no_filename')
    
    # Path traversal check
    if '/' in filename or '\\' in filename or '..' in filename:
        raise ValidationError(
            _('Invalid filename: path separators not allowed.'),
            code='path_traversal',
        )
    
    # Null byte check
    if '\x00' in filename:
        raise ValidationError(
            _('Invalid filename: contains illegal characters.'),
            code='null_byte',
        )
    
    # Check extension against blocked list
    ext = get_file_extension(filename)
    if ext in BLOCKED_EXTENSIONS:
        raise ValidationError(
            _('File type not allowed: .%(ext)s'),
            code='blocked_extension',
            params={'ext': ext},
        )
    
    # Check for double extensions (e.g., file.pdf.exe)
    parts = filename.split('.')
    if len(parts) > 2:
        for part in parts[1:]:  # Skip the base name
            if part.lower() in BLOCKED_EXTENSIONS:
                raise ValidationError(
                    _('File contains blocked extension: .%(ext)s'),
                    code='hidden_blocked_extension',
                    params={'ext': part.lower()},
                )


def validate_magic_bytes(file, expected_ext):
    """
    Validate file content matches expected type using magic bytes
    Prevents malicious files disguised with fake extensions
    """
    expected_magic = MAGIC_BYTES.get(expected_ext)
    if not expected_magic:
        return  # No magic bytes defined for this type
    
    # Read file header
    file.seek(0)
    header = file.read(16)  # Read first 16 bytes
    file.seek(0)  # Reset file pointer
    
    if not header.startswith(expected_magic):
        raise ValidationError(
            _('File content does not match extension. The file may be corrupted or malicious.'),
            code='invalid_magic_bytes',
        )


def validate_content_type(file, allowed_types):
    """
    Validate Content-Type header matches allowed types
    Note: Content-Type can be spoofed, so this is defense-in-depth
    """
    content_type = getattr(file, 'content_type', None)
    if content_type and content_type not in allowed_types:
        # Don't reject, just log - magic bytes are the real check
        import logging
        logger = logging.getLogger('core')
        logger.warning(f"Content-Type mismatch: {content_type} not in {allowed_types}")


def validate_resume_file(file):
    """
    Validate resume file:
    - Must be PDF
    - Maximum 5 MB
    - Magic bytes validation
    - Filename safety check
    """
    if not file:
        return

    # Sanitize and validate filename first
    file.name = sanitize_filename(file.name)
    validate_filename_safety(file.name)

    # Check file extension (whitelist)
    ext = get_file_extension(file.name)
    if ext not in ['pdf']:
        raise ValidationError(
            _('Resume must be a PDF file. Received: .%(ext)s'),
            code='invalid_extension',
            params={'ext': ext},
        )

    # Check file size (defensive: handle missing storage objects)
    try:
        file_size = file.size
    except Exception as e:
        raise ValidationError(
            _('Stored resume is missing or inaccessible. Please re-upload the resume.'),
            code='missing_file'
        ) from e

    if file_size > MAX_RESUME_SIZE:
        max_size_mb = MAX_RESUME_SIZE / (1024 * 1024)
        raise ValidationError(
            _('Resume file is too large. Maximum size: %(max_size)s MB. Your file: %(file_size)s MB'),
            code='file_too_large',
            params={
                'max_size': int(max_size_mb),
                'file_size': round(file_size / (1024 * 1024), 2),
            },
        )
    
    # Validate Content-Type (defense in depth)
    validate_content_type(file, ALLOWED_RESUME_TYPES)
    
    # Validate magic bytes (security: prevent disguised malicious files)
    validate_magic_bytes(file, ext)


def validate_profile_photo(file):
    """
    Validate profile photo:
    - Must be JPG or PNG
    - Maximum 1 MB
    - Magic bytes validation
    - Filename safety check
    """

    if not file:
        return

    # ─────────────────────────────────────────────
    # 1️⃣ Sanitize & validate filename
    # ─────────────────────────────────────────────
    file.name = sanitize_filename(file.name)
    validate_filename_safety(file.name)

    # ─────────────────────────────────────────────
    # 2️⃣ Extension whitelist
    # ─────────────────────────────────────────────
    ext = get_file_extension(file.name).lower()
    if ext not in ("jpg", "jpeg", "png"):
        raise ValidationError(
            _("Profile photo must be JPG or PNG. Received: .%(ext)s"),
            code="invalid_extension",
            params={"ext": ext},
        )

    # ─────────────────────────────────────────────
    # 3️⃣ SAFE file size check (NO S3 HEAD REQUEST)
    # ─────────────────────────────────────────────
    try:
        file_size = file.size  # cached once – uses UploadedFile, not storage
    except Exception as e:
        # Storage backend (e.g., S3) may raise on missing objects; surface a friendly error
        raise ValidationError(
            _('Stored profile photo is missing or inaccessible. Please re-upload the profile photo.'),
            code='missing_file'
        ) from e

    if file_size > MAX_PHOTO_SIZE:
        raise ValidationError(
            _("Profile photo is too large. Maximum size: %(max_size)s MB. Your file: %(file_size)s MB"),
            code="file_too_large",
            params={
                "max_size": MAX_PHOTO_SIZE // (1024 * 1024),
                "file_size": round(file_size / (1024 * 1024), 2),
            },
        )

    # ─────────────────────────────────────────────
    # 4️⃣ Content-Type validation (defense in depth)
    # ─────────────────────────────────────────────
    validate_content_type(file, ALLOWED_PHOTO_TYPES)

    # ─────────────────────────────────────────────
    # 5️⃣ Magic bytes validation (anti-spoofing)
    # ─────────────────────────────────────────────
    validate_magic_bytes(file, ext)

def validate_document_file(file):
    """
    Validate document file:
    - Must be PDF, JPG, or PNG
    - Maximum 5 MB
    - Magic bytes validation
    - Filename safety check
    """
    if not file:
        return

    # Sanitize and validate filename first
    file.name = sanitize_filename(file.name)
    validate_filename_safety(file.name)

    # Check file extension (whitelist)
    ext = get_file_extension(file.name)
    if ext not in ['pdf', 'jpg', 'jpeg', 'png']:
        raise ValidationError(
            _('Document must be PDF, JPG, or PNG. Received: .%(ext)s'),
            code='invalid_extension',
            params={'ext': ext},
        )

    # Check file size (defensive: handle missing storage objects)
    try:
        file_size = file.size
    except Exception as e:
        raise ValidationError(
            _('Stored document is missing or inaccessible. Please re-upload the document.'),
            code='missing_file'
        ) from e

    if file_size > MAX_DOCUMENT_SIZE:
        max_size_mb = MAX_DOCUMENT_SIZE / (1024 * 1024)
        raise ValidationError(
            _('Document is too large. Maximum size: %(max_size)s MB. Your file: %(file_size)s MB'),
            code='file_too_large',
            params={
                'max_size': int(max_size_mb),
                'file_size': round(file_size / (1024 * 1024), 2),
            },
        )
    
    # Validate Content-Type (defense in depth)
    validate_content_type(file, ALLOWED_DOCUMENT_TYPES)
    
    # Validate magic bytes (security: prevent disguised malicious files)
    validate_magic_bytes(file, ext)


def is_safe_filename(filename):
    """
    Check if filename is safe (no path traversal attempts)
    DEPRECATED: Use validate_filename_safety() instead for better error messages
    """
    if not filename:
        return False
    
    # No path separators or traversal attempts
    if '/' in filename or '\\' in filename or '..' in filename:
        return False
    
    # No null bytes
    if '\x00' in filename:
        return False
    
    # Check extension is not blocked
    ext = get_file_extension(filename)
    if ext in BLOCKED_EXTENSIONS:
        return False
    
    return True
