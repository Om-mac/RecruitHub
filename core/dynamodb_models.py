"""
DynamoDB Models for RecruitHub
Replaces PostgreSQL-based Django ORM models
"""

from pynamodb.models import Model
from pynamodb.attributes import (
    UnicodeAttribute, NumberAttribute, BooleanAttribute,
    UTCDateTimeAttribute, ListAttribute, MapAttribute,
    JSONAttribute, UnicodeSetAttribute
)
from datetime import datetime
import uuid
import os
from django.conf import settings

# ==================== DynamoDB Attributes ====================

class AddressMap(MapAttribute):
    """Nested attribute for address information"""
    street = UnicodeAttribute(null=True)
    city = UnicodeAttribute(null=True)
    state = UnicodeAttribute(null=True)
    pincode = UnicodeAttribute(null=True)
    country = UnicodeAttribute(null=True, default='India')


class EducationMap(MapAttribute):
    """Nested attribute for education information"""
    college_name = UnicodeAttribute(null=True)
    branch = UnicodeAttribute(null=True)
    degree = UnicodeAttribute(null=True)
    specialization = UnicodeAttribute(null=True)
    cgpa = UnicodeAttribute(null=True)  # Store as string decimal
    year_of_study = UnicodeAttribute(null=True)  # 1, 2, 3, 4, 5
    admission_year = NumberAttribute(null=True)
    backlogs = NumberAttribute(null=True, default=0)
    current_backlogs = NumberAttribute(null=True, default=0)


class ProfessionalMap(MapAttribute):
    """Nested attribute for professional information"""
    skills = ListAttribute(of=UnicodeAttribute, null=True)
    github_username = UnicodeAttribute(null=True)
    linkedin_username = UnicodeAttribute(null=True)
    hackerrank_username = UnicodeAttribute(null=True)
    codeforces_username = UnicodeAttribute(null=True)
    leetcode_username = UnicodeAttribute(null=True)
    bio = UnicodeAttribute(null=True)
    experience = UnicodeAttribute(null=True)
    certifications = ListAttribute(of=UnicodeAttribute, null=True)  # URLs to certifications


# ==================== Main Models ====================

class User(Model):
    """
    DynamoDB User Model
    Partition Key: user_id (UUID)
    """
    class Meta:
        table_name = os.environ.get('DYNAMODB_TABLE_PREFIX', 'recruithub-') + 'users'
        region = os.environ.get('AWS_REGION', 'us-east-1')
        host = os.environ.get('DYNAMODB_LOCAL_HOST', None) # For local testing

    # Keys
    user_id = UnicodeAttribute(hash_key=True)  # UUID
    email = UnicodeAttribute()  # Email for login
    
    # Authentication
    username = UnicodeAttribute()
    password_hash = UnicodeAttribute()  # Use Django's make_password()
    
    # Personal Info
    first_name = UnicodeAttribute(null=True)
    last_name = UnicodeAttribute(null=True)
    middle_name = UnicodeAttribute(null=True)
    phone = UnicodeAttribute(null=True)
    date_of_birth = UnicodeAttribute(null=True)  # ISO format: YYYY-MM-DD
    gender = UnicodeAttribute(null=True)  # M, F, O
    
    # Address
    address = AddressMap(null=True)
    
    # User Type
    user_type = UnicodeAttribute()  # 'student' or 'hr'
    is_staff = BooleanAttribute(default=False)
    is_superuser = BooleanAttribute(default=False)
    is_active = BooleanAttribute(default=True)
    
    # Timestamps
    created_at = UTCDateTimeAttribute(default=datetime.utcnow)
    updated_at = UTCDateTimeAttribute(default=datetime.utcnow)
    last_login = UTCDateTimeAttribute(null=True)


class UserProfile(Model):
    """
    Student Profile Model
    Partition Key: user_id
    """
    class Meta:
        table_name = os.environ.get('DYNAMODB_TABLE_PREFIX', 'recruithub-') + 'user-profiles'
        region = os.environ.get('AWS_REGION', 'us-east-1')

    user_id = UnicodeAttribute(hash_key=True)  # References User.user_id
    
    # Files (stored in S3, URI stored here)
    profile_photo_url = UnicodeAttribute(null=True)  # S3 URL
    resume_url = UnicodeAttribute(null=True)  # S3 URL
    
    # Education
    education = EducationMap(null=True)
    
    # Professional
    professional = ProfessionalMap(null=True)
    
    # Metadata
    created_at = UTCDateTimeAttribute(default=datetime.utcnow)
    updated_at = UTCDateTimeAttribute(default=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserProfile {self.user_id}>"


class Document(Model):
    """
    User Document Model
    Partition Key: user_id
    Sort Key: document_id (UUID)
    """
    class Meta:
        table_name = os.environ.get('DYNAMODB_TABLE_PREFIX', 'recruithub-') + 'documents'
        region = os.environ.get('AWS_REGION', 'us-east-1')

    user_id = UnicodeAttribute(hash_key=True)
    document_id = UnicodeAttribute(range_key=True)  # UUID
    
    title = UnicodeAttribute()
    file_url = UnicodeAttribute()  # S3 URL
    file_size = NumberAttribute()  # Size in bytes
    file_type = UnicodeAttribute()  # PDF, JPG, PNG
    
    uploaded_at = UTCDateTimeAttribute(default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Document {self.document_id}>"


class Note(Model):
    """
    User Note Model
    Partition Key: user_id
    Sort Key: note_id (UUID)
    """
    class Meta:
        table_name = os.environ.get('DYNAMODB_TABLE_PREFIX', 'recruithub-') + 'notes'
        region = os.environ.get('AWS_REGION', 'us-east-1')

    user_id = UnicodeAttribute(hash_key=True)
    note_id = UnicodeAttribute(range_key=True)  # UUID
    
    title = UnicodeAttribute()
    content = UnicodeAttribute()
    
    created_at = UTCDateTimeAttribute(default=datetime.utcnow)
    updated_at = UTCDateTimeAttribute(default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Note {self.note_id}>"


class HRProfile(Model):
    """
    HR Profile Model
    Partition Key: user_id
    """
    class Meta:
        table_name = os.environ.get('DYNAMODB_TABLE_PREFIX', 'recruithub-') + 'hr-profiles'
        region = os.environ.get('AWS_REGION', 'us-east-1')

    user_id = UnicodeAttribute(hash_key=True)  # References User.user_id
    
    # HR Information
    company_name = UnicodeAttribute()
    designation = UnicodeAttribute(null=True)
    department = UnicodeAttribute(null=True)
    admin_notes = UnicodeAttribute(null=True)
    
    # Approval Workflow
    is_approved = BooleanAttribute(default=False)
    approval_requested_at = UTCDateTimeAttribute(default=datetime.utcnow)
    approved_by = UnicodeAttribute(null=True)  # admin_user_id
    approved_at = UTCDateTimeAttribute(null=True)
    approval_token = UnicodeAttribute(null=True)  # Unique approval tokens
    rejection_reason = UnicodeAttribute(null=True)
    
    created_at = UTCDateTimeAttribute(default=datetime.utcnow)
    updated_at = UTCDateTimeAttribute(default=datetime.utcnow)
    
    def __repr__(self):
        status = "Approved" if self.is_approved else "Pending"
        return f"<HRProfile {self.user_id} - {status}>"


class EmailOTP(Model):
    """
    Email OTP Model for email verification
    Partition Key: email
    """
    class Meta:
        table_name = os.environ.get('DYNAMODB_TABLE_PREFIX', 'recruithub-') + 'email-otps'
        region = os.environ.get('AWS_REGION', 'us-east-1')

    email = UnicodeAttribute(hash_key=True)
    
    # OTP Data
    otp_hash = UnicodeAttribute()  # PBKDF2-SHA256 hash
    
    # Verification
    is_verified = BooleanAttribute(default=False)
    attempts = NumberAttribute(default=0)
    failed_attempts = NumberAttribute(default=0)
    
    # Rate limiting
    last_attempt_at = UTCDateTimeAttribute(null=True)
    last_request_at = UTCDateTimeAttribute(null=True)
    request_count = NumberAttribute(default=0)
    
    # Timestamps
    created_at = UTCDateTimeAttribute(default=datetime.utcnow)
    expires_at = UTCDateTimeAttribute()  # 15 minutes from creation
    
    # Constants
    MAX_FAILED_ATTEMPTS = 5
    ATTEMPT_LOCKOUT_MINUTES = 30
    REQUEST_RATE_LIMIT_MINUTES = 1
    OTP_VALIDITY_MINUTES = 15
    
    def __repr__(self):
        return f"<EmailOTP {self.email}>"


class IPRateLimit(Model):
    """
    Rate Limiting by IP Address
    Partition Key: endpoint
    Sort Key: ip_address
    """
    class Meta:
        table_name = os.environ.get('DYNAMODB_TABLE_PREFIX', 'recruithub-') + 'rate-limits'
        region = os.environ.get('AWS_REGION', 'us-east-1')

    endpoint = UnicodeAttribute(hash_key=True)  # e.g., '/login/', '/register/'
    ip_address = UnicodeAttribute(range_key=True)
    
    # Rate limiting data
    attempt_count = NumberAttribute(default=1)
    first_attempt_at = UTCDateTimeAttribute(default=datetime.utcnow)
    last_attempt_at = UTCDateTimeAttribute(default=datetime.utcnow)
    
    ttl = NumberAttribute()  # Unix timestamp for DynamoDB TTL expiration
    
    def __repr__(self):
        return f"<IPRateLimit {self.endpoint} - {self.ip_address}>"


class DynamoDBSession(Model):
    """
    Django Sessions stored in DynamoDB
    Partition Key: session_key
    """
    class Meta:
        table_name = os.environ.get('DYNAMODB_TABLE_PREFIX', 'recruithub-') + 'sessions'
        region = os.environ.get('AWS_REGION', 'us-east-1')

    session_key = UnicodeAttribute(hash_key=True)
    
    # Session data
    session_data = UnicodeAttribute()  # Pickled and base64 encoded session data
    
    # Timestamps
    created_at = UTCDateTimeAttribute(default=datetime.utcnow)
    expire_date = UTCDateTimeAttribute()
    
    ttl = NumberAttribute()  # For DynamoDB TTL
    
    def __repr__(self):
        return f"<DynamoDBSession {self.session_key[:10]}...>"


# ==================== Helper Functions ====================

def create_all_tables():
    """
    Create all DynamoDB tables
    Run this during deployment (one-time setup)
    """
    models = [
        User,
        UserProfile,
        Document,
        Note,
        HRProfile,
        EmailOTP,
        IPRateLimit,
        DynamoDBSession
    ]
    
    for model in models:
        try:
            if not model.exists():
                model.create_table(
                    read_capacity_units=10,
                    write_capacity_units=10,
                    wait=True
                )
                print(f"✅ Created table: {model.Meta.table_name}")
            else:
                print(f"⚠️  Table already exists: {model.Meta.table_name}")
        except Exception as e:
            print(f"❌ Error creating {model.Meta.table_name}: {e}")


def delete_all_tables():
    """
    Delete all DynamoDB tables (WARNING: Data loss!)
    Only use in development
    """
    models = [
        User,
        UserProfile,
        Document,
        Note,
        HRProfile,
        EmailOTP,
        IPRateLimit,
        DynamoDBSession
    ]
    
    for model in models:
        try:
            if model.exists():
                model.delete_table()
                print(f"🗑️  Deleted table: {model.Meta.table_name}")
        except Exception as e:
            print(f"❌ Error deleting {model.Meta.table_name}: {e}")
