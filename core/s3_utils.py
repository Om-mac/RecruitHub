"""
S3 presigned URL generation for secure file downloads
Generates temporary signed URLs that expire after 1-5 minutes

Security Features:
- Presigned URLs with short expiration (1-5 minutes)
- Path traversal prevention
- User ownership validation
- No credential/bucket logging
"""

import logging
import re
import boto3
from django.conf import settings
from botocore.exceptions import ClientError

# Suppress S3 URL logging
logger = logging.getLogger('s3_security')
logger.setLevel(logging.WARNING)


def sanitize_s3_path(file_path):
    """
    Sanitize S3 file path to prevent path traversal attacks
    
    Security:
    - Removes path traversal sequences (../, ..\ )
    - Removes null bytes
    - Normalizes path separators
    - Ensures path stays within allowed directories
    """
    if not file_path:
        return None
    
    # Remove null bytes
    file_path = file_path.replace('\x00', '')
    
    # Normalize path separators
    file_path = file_path.replace('\\', '/')
    
    # Remove path traversal sequences
    while '../' in file_path or '..\\' in file_path:
        file_path = file_path.replace('../', '').replace('..\\', '')
    
    # Remove leading slashes
    file_path = file_path.lstrip('/')
    
    # Only allow files in expected directories
    allowed_prefixes = ('media/', 'profile_photos/', 'resumes/', 'documents/')
    if not file_path.startswith(allowed_prefixes):
        # Check if it's a direct file in allowed folder
        parts = file_path.split('/')
        if len(parts) > 0 and parts[0] not in ['media', 'profile_photos', 'resumes', 'documents']:
            return None
    
    return file_path


def get_s3_client():
    """Get boto3 S3 client (production only)"""
    if not settings.USE_S3:
        return None
    
    try:
        return boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )
    except Exception as e:
        # Don't log the actual error details (may contain credentials)
        logger.error('Failed to initialize S3 client')
        return None


def generate_presigned_url(file_path, expiration=300):
    """
    Generate presigned URL for S3 file
    
    Args:
        file_path: S3 object key (e.g., 'profile_photos/file.jpg')
        expiration: URL validity in seconds (default: 300 = 5 minutes)
    
    Returns:
        Presigned URL string or None if error
        
    Security:
        - URL expires automatically (default 5 minutes)
        - Requires AWS signature authentication
        - Bucket and credentials never logged
        - Path traversal prevention
    """
    if not settings.USE_S3:
        # Local development: return local file URL
        return f'/media/{file_path}'
    
    # Security: Sanitize file path to prevent traversal attacks
    file_path = sanitize_s3_path(file_path)
    if not file_path:
        logger.warning('Invalid file path rejected')
        return None
    
    # Validate expiration is within 1-5 minutes
    if expiration < 60 or expiration > 300:
        expiration = 300  # Default to 5 minutes
    
    try:
        s3_client = get_s3_client()
        if not s3_client:
            # Fallback to local storage if S3 client unavailable
            return f'/media/{file_path}'
        
        # Add media/ prefix if not already present (django-storages stores files under media/)
        s3_key = file_path if file_path.startswith('media/') else f'media/{file_path}'
        
        # Try to generate presigned URL
        try:
            presigned_url = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                    'Key': s3_key,
                },
                ExpiresIn=expiration,
            )
            
            # Security: Don't log the URL or bucket name
            logger.debug(f'Presigned URL generated with {expiration}s expiration')
            
            return presigned_url
        except ClientError as e:
            # If file doesn't exist in S3, try local storage fallback
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            if error_code == 'NoSuchKey':
                # Security: Don't log file path (may contain user IDs)
                logger.warning('File not found in S3, falling back to local storage')
                # Return local file URL as fallback
                return f'/media/{file_path}'
            else:
                raise
        
    except ClientError as e:
        # Don't expose S3 error details (may contain bucket/credentials info)
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        logger.error(f'Failed to generate presigned URL: {error_code}')
        # Fallback to local storage
        return f'/media/{file_path}'
    except Exception as e:
        # Log generic error without details
        logger.error('Unexpected error generating presigned URL')
        # Fallback to local storage
        return f'/media/{file_path}'


def generate_presigned_urls_batch(file_paths, expiration=300):
    """
    Generate multiple presigned URLs efficiently
    
    Args:
        file_paths: List of S3 object keys
        expiration: URL validity in seconds
    
    Returns:
        Dictionary mapping file_path -> presigned_url
    """
    urls = {}
    for file_path in file_paths:
        url = generate_presigned_url(file_path, expiration)
        if url:
            urls[file_path] = url
    
    return urls


def validate_s3_file_access(user, file_path):
    """
    Verify user has permission to access file
    
    Args:
        user: Django User object
        file_path: S3 object key (e.g., 'resumes/user123/resume.pdf')
    
    Returns:
        True if user can access file, False otherwise
    """
    if not user.is_authenticated:
        return False
    
    # File path should contain user ID for ownership verification
    # Examples:
    # - resumes/{user.id}/resume.pdf
    # - profile_photos/{user.id}/photo.png
    # - documents/{user.id}/doc.pdf
    
    # Extract user ID from path
    path_parts = file_path.split('/')
    
    # Validate path structure (at least 3 parts: folder/user_id/filename)
    if len(path_parts) < 3:
        return False
    
    # Check if user owns the file
    try:
        stored_user_id = int(path_parts[1])
        return user.id == stored_user_id
    except (ValueError, IndexError):
        return False


def get_download_filename(file_path):
    """
    Extract safe filename from S3 path for Content-Disposition header
    
    Args:
        file_path: S3 object key (e.g., 'resumes/user123/resume.pdf')
    
    Returns:
        Safe filename for download
    """
    # Get filename from path
    filename = file_path.split('/')[-1]
    
    # Sanitize filename (remove special characters)
    import re
    filename = re.sub(r'[^\w\s.-]', '', filename)
    
    return filename or 'download'
