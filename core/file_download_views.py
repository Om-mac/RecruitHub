"""
Secure file download views using presigned URLs
Generates temporary signed URLs instead of exposing direct S3 access

Security Features:
- Authentication required on all endpoints
- IDOR prevention via ownership validation
- Presigned URLs with short expiration
- No-cache headers on all responses
- Sanitized logging (no file paths)
"""

import logging
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse
from core.models import UserProfile, Document
from core.s3_utils import generate_presigned_url, validate_s3_file_access, get_download_filename

# Logger for download tracking (no URL logging)
logger = logging.getLogger('file_downloads')


def secure_json_response(data, status=200):
    """
    Create JSON response with security headers
    - No caching of presigned URLs
    - No sniffing of content type
    """
    response = JsonResponse(data, status=status)
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
    response['Pragma'] = 'no-cache'
    response['X-Content-Type-Options'] = 'nosniff'
    return response


@login_required
@require_http_methods(["GET"])
def download_resume(request):
    """
    Generate presigned URL for user's resume
    
    Security:
    - Requires authentication
    - Verifies user owns the resume
    - Returns presigned URL (not direct S3 URL)
    - URL expires in 5 minutes
    """
    try:
        profile = request.user.profile
        if not profile.resume:
            return JsonResponse({
                'error': 'No resume found',
                'status': 404
            }, status=404)
        
        # Get resume file path
        resume_path = profile.resume.name
        
        # Verify user owns this file
        if not validate_s3_file_access(request.user, resume_path):
            return JsonResponse({
                'error': 'Access denied',
                'status': 403
            }, status=403)
        
        # Generate presigned URL (5 min validity)
        presigned_url = generate_presigned_url(resume_path, expiration=300)
        
        if not presigned_url:
            # Security: Don't log file path (contains user ID)
            logger.warning('Failed to generate presigned URL for resume')
            return secure_json_response({
                'error': 'File not accessible',
                'status': 404
            }, status=404)
        
        # Log download attempt (no URL or bucket names)
        logger.info(f'Resume download initiated by user {request.user.id}')
        
        return secure_json_response({
            'url': presigned_url,
            'filename': get_download_filename(resume_path),
            'expires_in': 300,  # 5 minutes in seconds
            'status': 'success'
        })
        
    except UserProfile.DoesNotExist:
        return secure_json_response({
            'error': 'User profile not found',
            'status': 404
        }, status=404)
    except Exception as e:
        # Security: Don't log exception details
        logger.error('Error generating resume download URL')
        return secure_json_response({
            'error': 'Server error processing request',
            'status': 500
        }, status=500)


@login_required
@require_http_methods(["GET"])
def download_profile_photo(request):
    """
    Generate presigned URL for profile photo
    
    Parameters:
    - user_id (optional): Get another user's photo (for HR/admin viewing students)
    
    Security:
    - Requires authentication
    - If user_id provided: Approved HR/admin permission check
    - If no user_id: Returns current user's photo
    - Returns presigned URL (not direct S3 URL)
    - URL expires in 5 minutes
    """
    try:
        # Get user_id from query parameters (optional)
        user_id = request.GET.get('user_id')
        
        if user_id:
            # Security: Validate user_id is integer
            try:
                user_id = int(user_id)
            except (ValueError, TypeError):
                return secure_json_response({
                    'error': 'Invalid user ID',
                    'status': 400
                }, status=400)
            
            # HR/Admin viewing a student's photo
            # Security: Check if current user is APPROVED HR or superuser
            is_approved_hr = False
            if hasattr(request.user, 'hr_profile'):
                is_approved_hr = request.user.hr_profile.is_approved
            
            if not (request.user.is_superuser or is_approved_hr):
                return secure_json_response({
                    'error': 'Access denied',
                    'status': 403
                }, status=403)
            
            # Get the requested user's profile
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                target_user = User.objects.get(id=user_id)
                profile = target_user.profile
            except User.DoesNotExist:
                return secure_json_response({
                    'error': 'User not found',
                    'status': 404
                }, status=404)
        else:
            # Get current user's photo
            profile = request.user.profile
        
        if not profile.profile_photo:
            return secure_json_response({
                'error': 'No profile photo found',
                'status': 404
            }, status=404)
        
        # Get photo file path (this is the S3 key)
        photo_path = profile.profile_photo.name
        
        # Generate presigned URL (5 min validity)
        presigned_url = generate_presigned_url(photo_path, expiration=300)
        
        if not presigned_url:
            # Security: Don't log file path
            logger.warning('Failed to generate presigned URL for profile photo')
            return secure_json_response({
                'error': 'File not accessible',
                'status': 404
            }, status=404)
        
        # Log download attempt (no URL or bucket names)
        logger.info(f'Profile photo download initiated by user {request.user.id}')
        
        return secure_json_response({
            'url': presigned_url,
            'filename': get_download_filename(photo_path),
            'expires_in': 300,  # 5 minutes in seconds
            'status': 'success'
        })
        
    except UserProfile.DoesNotExist:
        return secure_json_response({
            'error': 'User profile not found',
            'status': 404
        }, status=404)
    except Exception as e:
        # Security: Don't log exception details
        logger.error('Error generating profile photo download URL')
        return secure_json_response({
            'error': 'Server error processing request',
            'status': 500
        }, status=500)


@login_required
@require_http_methods(["GET"])
def download_document(request, doc_id):
    """
    Generate presigned URL for a document
    
    Security:
    - Requires authentication
    - Verifies user owns the document (IDOR prevention)
    - Returns presigned URL (not direct S3 URL)
    - URL expires in 5 minutes
    - No-cache headers prevent URL caching
    """
    try:
        # Security: Validate doc_id is integer
        try:
            doc_id = int(doc_id)
        except (ValueError, TypeError):
            return secure_json_response({
                'error': 'Invalid document ID',
                'status': 400
            }, status=400)
        
        # Get document and verify ownership (IDOR prevention)
        doc = get_object_or_404(Document, id=doc_id, user=request.user)
        
        if not doc.file:
            return secure_json_response({
                'error': 'Document file not found',
                'status': 404
            }, status=404)
        
        # Get document file path
        file_path = doc.file.name
        
        # Generate presigned URL (5 min validity)
        presigned_url = generate_presigned_url(file_path, expiration=300)
        
        if not presigned_url:
            return secure_json_response({
                'error': 'Failed to generate download link',
                'status': 500
            }, status=500)
        
        # Log download attempt (no URL or bucket names)
        logger.info(f'Document download initiated by user {request.user.id}')
        
        return secure_json_response({
            'url': presigned_url,
            'filename': get_download_filename(file_path),
            'title': doc.title,
            'expires_in': 300,  # 5 minutes in seconds
            'status': 'success'
        })
        
    except Exception as e:
        logger.error('Error generating document download URL')
        return secure_json_response({
            'error': 'Server error processing request',
            'status': 500
        }, status=500)


@login_required
@require_http_methods(["GET"])
def view_file_info(request, file_type):
    """
    Get file information without exposing S3 URLs
    Returns file metadata like size, type, upload date
    
    Args:
        file_type: 'resume', 'profile_photo', or 'documents'
    
    Security:
    - Authentication required
    - Only returns own files
    - Validates file_type parameter
    """
    # Security: Whitelist allowed file types
    ALLOWED_FILE_TYPES = {'resume', 'profile_photo', 'documents'}
    if file_type not in ALLOWED_FILE_TYPES:
        return secure_json_response({
            'error': 'Invalid file type',
            'status': 400
        }, status=400)
    
    try:
        if file_type == 'resume':
            profile = request.user.profile
            if not profile.resume:
                return secure_json_response({'error': 'No resume', 'status': 404}, status=404)
            
            return secure_json_response({
                'exists': True,
                'filename': profile.resume.name.split('/')[-1],
                'size_mb': round(profile.resume.size / (1024 * 1024), 2),
                'status': 'success'
            })
        
        elif file_type == 'profile_photo':
            profile = request.user.profile
            if not profile.profile_photo:
                return secure_json_response({'error': 'No profile photo', 'status': 404}, status=404)
            
            return secure_json_response({
                'exists': True,
                'filename': profile.profile_photo.name.split('/')[-1],
                'size_mb': round(profile.profile_photo.size / (1024 * 1024), 2),
                'status': 'success'
            })
        
        elif file_type == 'documents':
            docs = Document.objects.filter(user=request.user)
            doc_list = [
                {
                    'id': doc.id,
                    'title': doc.title,
                    'filename': doc.file.name.split('/')[-1],
                    'size_mb': round(doc.file.size / (1024 * 1024), 2),
                    'uploaded_at': doc.uploaded_at.isoformat()
                }
                for doc in docs
            ]
            
            return secure_json_response({
                'documents': doc_list,
                'count': len(doc_list),
                'status': 'success'
            })
        
    except Exception as e:
        logger.error('Error getting file info')
        return secure_json_response({
            'error': 'Server error',
            'status': 500
        }, status=500)
