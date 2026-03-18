"""
DynamoDB Helper Functions for RecruitHub
Provides unified interface between Django ORM and DynamoDB
"""

import os
import uuid
from datetime import datetime
from django.contrib.auth.models import User
from .dynamodb_models import (
    User as DDBUser, 
    UserProfile as DDBUserProfile,
    HRProfile as DDBHRProfile,
    Document as DDBDocument,
    Note as DDBNote,
)
import logging

logger = logging.getLogger('core')

USE_DYNAMODB = os.environ.get('USE_DYNAMODB', 'False').lower() == 'true'


def sync_django_user_to_dynamodb(django_user, user_type='student'):
    """Sync Django User to DynamoDB
    
    When Django User is created/updated, also create/update in DynamoDB
    """
    if not USE_DYNAMODB:
        return None
    
    try:
        ddb_user = DDBUser(
            user_id=str(django_user.id),
            email=django_user.email,
            username=django_user.username,
            password_hash=django_user.password,
            first_name=django_user.first_name,
            last_name=django_user.last_name,
            user_type=user_type,
            is_staff=django_user.is_staff,
            is_superuser=django_user.is_superuser,
            is_active=django_user.is_active,
        )
        ddb_user.save()
        logger.info(f"✅ Django User {django_user.username} synced to DynamoDB")
        return ddb_user
    except Exception as e:
        logger.error(f"❌ Failed to sync user to DynamoDB: {e}")
        return None


def get_user_profile_ddb(django_user):
    """Get user profile from DynamoDB
    
    Args:
        django_user: Django User instance
        
    Returns:
        DynamoDB UserProfile or None
    """
    if not USE_DYNAMODB:
        return None
    
    try:
        profile = DDBUserProfile.get(str(django_user.id))
        return profile
    except DDBUserProfile.DoesNotExist:
        logger.debug(f"User profile not found in DynamoDB for {django_user.username}")
        return None
    except Exception as e:
        logger.error(f"Error getting DynamoDB profile: {e}")
        return None


def create_user_profile_ddb(django_user):
    """Create new user profile in DynamoDB
    
    Args:
        django_user: Django User instance
        
    Returns:
        DynamoDB UserProfile
    """
    if not USE_DYNAMODB:
        return None
    
    try:
        profile = DDBUserProfile(
            user_id=str(django_user.id),
            profile_photo_url=None,
            resume_url=None,
            education=None,
            professional=None,
        )
        profile.save()
        logger.info(f"✅ User profile created in DynamoDB for {django_user.username}")
        return profile
    except Exception as e:
        logger.error(f"❌ Failed to create profile in DynamoDB: {e}")
        return None


def get_hr_profile_ddb(django_user):
    """Get HR profile from DynamoDB
    
    Args:
        django_user: Django User instance
        
    Returns:
        DynamoDB HRProfile or None
    """
    if not USE_DYNAMODB:
        return None
    
    try:
        hr_profile = DDBHRProfile.get(str(django_user.id))
        return hr_profile
    except DDBHRProfile.DoesNotExist:
        return None
    except Exception as e:
        logger.error(f"Error getting DynamoDB HR profile: {e}")
        return None


def create_hr_profile_ddb(django_user, company_name, designation=None, department=None):
    """Create new HR profile in DynamoDB
    
    Args:
        django_user: Django User instance
        company_name: Company name
        designation: Optional designation
        department: Optional department
        
    Returns:
        DynamoDB HRProfile
    """
    if not USE_DYNAMODB:
        return None
    
    try:
        hr_profile = DDBHRProfile(
            user_id=str(django_user.id),
            company_name=company_name,
            designation=designation,
            department=department,
            admin_notes='',
            is_approved=False,
            approval_requested_at=datetime.utcnow(),
        )
        hr_profile.save()
        logger.info(f"✅ HR profile created in DynamoDB for {django_user.username}")
        return hr_profile
    except Exception as e:
        logger.error(f"❌ Failed to create HR profile in DynamoDB: {e}")
        return None


def update_user_profile_ddb(django_user, **kwargs):
    """Update user profile in DynamoDB
    
    Args:
        django_user: Django User instance
        **kwargs: Fields to update (profile_photo_url, resume_url, etc.)
        
    Returns:
        Updated DynamoDB UserProfile or None
    """
    if not USE_DYNAMODB:
        return None
    
    try:
        profile = get_user_profile_ddb(django_user)
        if not profile:
            profile = create_user_profile_ddb(django_user)
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        profile.save()
        logger.info(f"✅ User profile updated in DynamoDB for {django_user.username}")
        return profile
    except Exception as e:
        logger.error(f"❌ Failed to update profile in DynamoDB: {e}")
        return None


def get_user_documents_ddb(django_user):
    """Get all documents for user from DynamoDB
    
    Args:
        django_user: Django User instance
        
    Returns:
        List of DynamoDB Document objects
    """
    if not USE_DYNAMODB:
        return []
    
    try:
        documents = DDBDocument.query(str(django_user.id))
        return list(documents)
    except Exception as e:
        logger.error(f"Error getting documents from DynamoDB: {e}")
        return []


def create_document_ddb(django_user, title, file_url, file_size, file_type):
    """Create new document in DynamoDB
    
    Args:
        django_user: Django User instance
        title: Document title
        file_url: S3 URL
        file_size: File size in bytes
        file_type: File type (PDF, JPG, PNG)
        
    Returns:
        DynamoDB Document
    """
    if not USE_DYNAMODB:
        return None
    
    try:
        doc = DDBDocument(
            user_id=str(django_user.id),
            document_id=str(uuid.uuid4()),
            title=title,
            file_url=file_url,
            file_size=file_size,
            file_type=file_type,
        )
        doc.save()
        logger.info(f"✅ Document created in DynamoDB for {django_user.username}")
        return doc
    except Exception as e:
        logger.error(f"❌ Failed to create document in DynamoDB: {e}")
        return None


def get_user_notes_ddb(django_user):
    """Get all notes for user from DynamoDB
    
    Args:
        django_user: Django User instance
        
    Returns:
        List of DynamoDB Note objects
    """
    if not USE_DYNAMODB:
        return []
    
    try:
        notes = DDBNote.query(str(django_user.id))
        return list(notes)
    except Exception as e:
        logger.error(f"Error getting notes from DynamoDB: {e}")
        return []


def create_note_ddb(django_user, title, content):
    """Create new note in DynamoDB
    
    Args:
        django_user: Django User instance
        title: Note title
        content: Note content
        
    Returns:
        DynamoDB Note
    """
    if not USE_DYNAMODB:
        return None
    
    try:
        note = DDBNote(
            user_id=str(django_user.id),
            note_id=str(uuid.uuid4()),
            title=title,
            content=content,
        )
        note.save()
        logger.info(f"✅ Note created in DynamoDB for {django_user.username}")
        return note
    except Exception as e:
        logger.error(f"❌ Failed to create note in DynamoDB: {e}")
        return None


def delete_note_ddb(django_user, note_id):
    """Delete note from DynamoDB
    
    Args:
        django_user: Django User instance
        note_id: Note ID to delete
        
    Returns:
        True if deleted, False otherwise
    """
    if not USE_DYNAMODB:
        return False
    
    try:
        note = DDBNote.get(str(django_user.id), note_id)
        note.delete()
        logger.info(f"✅ Note deleted from DynamoDB for {django_user.username}")
        return True
    except Exception as e:
        logger.error(f"Error deleting note from DynamoDB: {e}")
        return False
