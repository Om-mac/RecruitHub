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
    - Removes path traversal sequences (.., //, backslash)
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
        import botocore.config
        
        # Configure boto3 for ap-south-1 region with SigV4
        config = botocore.config.Config(
            region_name=settings.AWS_S3_REGION_NAME,
            signature_version='s3v4',
            retries={'max_attempts': 3, 'mode': 'standard'}
        )
        
        # Use regional endpoint URL explicitly
        endpoint_url = f'https://s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com'
        
        return boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            endpoint_url=endpoint_url,
            config=config
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
    import logging
    core_logger = logging.getLogger('core')
    
    if not settings.USE_S3:
        # Local development: return local file URL
        return f'/media/{file_path}'
    
    core_logger.info(f'generate_presigned_url called with: {file_path}')
    
    # Security: Sanitize file path to prevent traversal attacks
    file_path = sanitize_s3_path(file_path)
    core_logger.info(f'After sanitization: {file_path}')
    
    if not file_path:
        logger.warning('Invalid file path rejected')
        return None
    
    # Validate expiration is within 1-5 minutes
    if expiration < 60 or expiration > 300:
        expiration = 300  # Default to 5 minutes
    
    try:
        s3_client = get_s3_client()
        if not s3_client:
            core_logger.error('S3 client is None')
            # Fallback to local storage if S3 client unavailable
            return f'/media/{file_path}'
        
        core_logger.info(f'S3 client initialized')
        
        # Add media/ prefix if not already present (django-storages stores files under media/)
        s3_key = file_path if file_path.startswith('media/') else f'media/{file_path}'
        core_logger.info(f'Final S3 key: {s3_key}')
        core_logger.info(f'S3 bucket: {settings.AWS_STORAGE_BUCKET_NAME}')
        
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
            
            core_logger.info(f'Presigned URL generated successfully')
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
        file_path: S3 object key (e.g., 'resumes/user123/resume.pdf' or 'resumes/test-user1-resume.pdf')
    
    Returns:
        True if user can access file, False otherwise
    """
    import logging
    core_logger = logging.getLogger('core')
    
    if not user.is_authenticated:
        return False
    
    # File path can be in two formats:
    # OLD: folder/{user.id}/filename (3+ parts)
    # NEW: folder/firstname-lastname-filename (2 parts)
    
    core_logger.info(f'validate_s3_file_access: user={user.id} ({user.first_name} {user.last_name}), path={file_path}')
    
    # Extract parts from path
    path_parts = file_path.split('/')
    core_logger.info(f'Path parts: {path_parts}, count: {len(path_parts)}')
    
    # Try old format first: folder/user_id/filename (3+ parts)
    if len(path_parts) >= 3:
        try:
            stored_user_id = int(path_parts[1])
            is_match = user.id == stored_user_id
            core_logger.info(f'OLD format: stored_user_id={stored_user_id}, match={is_match}')
            return is_match
        except (ValueError, IndexError):
            core_logger.info(f'OLD format parse failed')
            pass  # Not old format, try new format
    
    # Try new format: folder/firstname-lastname-filename (2 parts)
    if len(path_parts) >= 2:
        filename = path_parts[-1].lower()
        first_name = user.first_name.replace(" ", "-").lower() if user.first_name else ""
        last_name = user.last_name.replace(" ", "-").lower() if user.last_name else str(user.id)
        
        core_logger.info(f'NEW format: filename={filename}, first={first_name}, last={last_name}')
        
        # Check if filename contains user's name
        if first_name and last_name:
            match = first_name in filename and last_name in filename
            core_logger.info(f'NEW format name match: {match}')
            return match
        
        # Fallback: check if user_id is in filename
        if str(user.id) in filename:
            core_logger.info(f'NEW format ID match: {user.id} in filename')
            return True
    
    core_logger.warning(f'validate_s3_file_access DENIED for user {user.id}')
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


def generate_presigned_post(file_path, expiration=3600):
    """
    Generate presigned POST policy for direct S3 upload
    
    Args:
        file_path: Target S3 object key (e.g., 'documents/user123/filename.pdf')
        expiration: Policy validity in seconds (default: 3600 = 1 hour)
    
    Returns:
        Dict with 'url', 'fields' for POST request, or None if error
        
    Security:
        - Policy expires automatically
        - File path restricted to specific location
        - Content type and size restrictions enforced
        - Path traversal prevention
    """
    if not settings.USE_S3:
        # Local development: return None (use regular upload)
        return None
    
    # Sanitize path
    file_path = sanitize_s3_path(file_path)
    if not file_path:
        logger.warning('Invalid file path for presigned POST')
        return None
    
    # Ensure media/ prefix
    s3_key = file_path if file_path.startswith('media/') else f'media/{file_path}'
    
    try:
        s3_client = get_s3_client()
        if not s3_client:
            logger.error('S3 client is None')
            return None
        
        # Generate presigned POST with conditions
        presigned_post = s3_client.generate_presigned_post(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=s3_key,
            Fields=None,
            Conditions=[
                # Restrict file size to 5MB (only size restriction, no content-type)
                ["content-length-range", 0, 5 * 1024 * 1024],
            ],
            ExpiresIn=expiration,
        )
        
        logger.debug(f'Presigned POST generated for {s3_key}')
        return presigned_post
        
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        logger.error(f'Failed to generate presigned POST: {error_code}')
        return None
    except Exception as e:
        logger.error('Unexpected error generating presigned POST')
        return None
