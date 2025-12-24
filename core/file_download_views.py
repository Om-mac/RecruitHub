"""
Secure file download views using presigned URLs
Generates temporary signed URLs instead of exposing direct S3 access
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
            return JsonResponse({
                'error': 'Failed to generate download link',
                'status': 500
            }, status=500)
        
        # Log download attempt (no URL or bucket names)
        logger.info(f'Resume download initiated by user {request.user.id}')
        
        return JsonResponse({
            'url': presigned_url,
            'filename': get_download_filename(resume_path),
            'expires_in': 300,  # 5 minutes in seconds
            'status': 'success'
        })
        
    except UserProfile.DoesNotExist:
        return JsonResponse({
            'error': 'User profile not found',
            'status': 404
        }, status=404)
    except Exception as e:
        logger.error('Error generating resume download URL')
        return JsonResponse({
            'error': 'Server error processing request',
            'status': 500
        }, status=500)


@login_required
@require_http_methods(["GET"])
def download_profile_photo(request):
    """
    Generate presigned URL for user's profile photo
    
    Security:
    - Requires authentication
    - Verifies user owns the photo
    - Returns presigned URL (not direct S3 URL)
    - URL expires in 5 minutes
    """
    try:
        profile = request.user.profile
        if not profile.profile_photo:
            return JsonResponse({
                'error': 'No profile photo found',
                'status': 404
            }, status=404)
        
        # Get photo file path
        photo_path = profile.profile_photo.name
        
        # Verify user owns this file
        if not validate_s3_file_access(request.user, photo_path):
            return JsonResponse({
                'error': 'Access denied',
                'status': 403
            }, status=403)
        
        # Generate presigned URL (5 min validity)
        presigned_url = generate_presigned_url(photo_path, expiration=300)
        
        if not presigned_url:
            return JsonResponse({
                'error': 'Failed to generate download link',
                'status': 500
            }, status=500)
        
        # Log download attempt (no URL or bucket names)
        logger.info(f'Profile photo download initiated by user {request.user.id}')
        
        return JsonResponse({
            'url': presigned_url,
            'filename': get_download_filename(photo_path),
            'expires_in': 300,  # 5 minutes in seconds
            'status': 'success'
        })
        
    except UserProfile.DoesNotExist:
        return JsonResponse({
            'error': 'User profile not found',
            'status': 404
        }, status=404)
    except Exception as e:
        logger.error('Error generating profile photo download URL')
        return JsonResponse({
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
    - Verifies user owns the document
    - Returns presigned URL (not direct S3 URL)
    - URL expires in 5 minutes
    """
    try:
        # Get document and verify ownership
        doc = get_object_or_404(Document, id=doc_id, user=request.user)
        
        if not doc.file:
            return JsonResponse({
                'error': 'Document file not found',
                'status': 404
            }, status=404)
        
        # Get document file path
        file_path = doc.file.name
        
        # Generate presigned URL (5 min validity)
        presigned_url = generate_presigned_url(file_path, expiration=300)
        
        if not presigned_url:
            return JsonResponse({
                'error': 'Failed to generate download link',
                'status': 500
            }, status=500)
        
        # Log download attempt (no URL or bucket names)
        logger.info(f'Document {doc.id} download initiated by user {request.user.id}')
        
        return JsonResponse({
            'url': presigned_url,
            'filename': get_download_filename(file_path),
            'title': doc.title,
            'expires_in': 300,  # 5 minutes in seconds
            'status': 'success'
        })
        
    except Exception as e:
        logger.error('Error generating document download URL')
        return JsonResponse({
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
    """
    try:
        if file_type == 'resume':
            profile = request.user.profile
            if not profile.resume:
                return JsonResponse({'error': 'No resume', 'status': 404}, status=404)
            
            return JsonResponse({
                'exists': True,
                'filename': profile.resume.name.split('/')[-1],
                'size_mb': round(profile.resume.size / (1024 * 1024), 2),
                'status': 'success'
            })
        
        elif file_type == 'profile_photo':
            profile = request.user.profile
            if not profile.profile_photo:
                return JsonResponse({'error': 'No profile photo', 'status': 404}, status=404)
            
            return JsonResponse({
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
            
            return JsonResponse({
                'documents': doc_list,
                'count': len(doc_list),
                'status': 'success'
            })
        
        else:
            return JsonResponse({
                'error': 'Invalid file type',
                'status': 400
            }, status=400)
        
    except Exception as e:
        logger.error('Error getting file info')
        return JsonResponse({
            'error': 'Server error',
            'status': 500
        }, status=500)
