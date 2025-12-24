from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from .file_validators import validate_resume_file, validate_profile_photo, validate_document_file

# Conditional storage for S3
if settings.USE_S3:
    from storages.backends.s3boto3 import S3Boto3Storage
    media_storage = S3Boto3Storage(location='media')
else:
    media_storage = None

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # Personal Details
    middle_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], blank=True)
    # Address
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    # Files
    profile_photo = models.ImageField(
        upload_to='profile_photos/',
        blank=True,
        null=True,
        storage=media_storage if settings.USE_S3 else None,
        validators=[validate_profile_photo],
        help_text="JPG or PNG, max 1 MB"
    )
    resume = models.FileField(
        upload_to='resumes/',
        blank=True,
        null=True,
        storage=media_storage if settings.USE_S3 else None,
        validators=[validate_resume_file],
        help_text="PDF only, max 5 MB"
    )
    # Education
    college_name = models.CharField(max_length=255, blank=True)
    branch = models.CharField(max_length=100, blank=True, help_text="Branch/Stream (e.g., CSE, ECE, Mechanical)")
    degree = models.CharField(max_length=100, blank=True)
    specialization = models.CharField(max_length=100, blank=True)
    cgpa = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    year_of_study = models.CharField(max_length=20, choices=[('1', 'First Year'), ('2', 'Second Year'), ('3', 'Third Year'), ('4', 'Fourth Year'), ('5', 'Fifth Year')], blank=True)
    admission_year = models.IntegerField(blank=True, null=True)
    backlogs = models.IntegerField(default=0, blank=True)
    current_backlogs = models.IntegerField(default=0, blank=True)
    certifications_links = models.TextField(blank=True, help_text="Paste certification links, one per line")
    # Professional
    skills = models.TextField(blank=True)
    github_username = models.CharField(max_length=255, blank=True)
    linkedin_username = models.CharField(max_length=255, blank=True)
    hackerrank_username = models.CharField(max_length=255, blank=True)
    other_platforms = models.TextField(blank=True, help_text="Other platform usernames (e.g., Codeforces: username, LeetCode: username)")
    bio = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    # Only create UserProfile for non-staff, non-superuser accounts (students only)
    if created and not instance.is_staff and not instance.is_superuser:
        UserProfile.objects.get_or_create(user=instance)
    
    # Clean up: Remove UserProfile if user becomes staff/superuser
    if not created and (instance.is_staff or instance.is_superuser):
        UserProfile.objects.filter(user=instance).delete()

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    file = models.FileField(
        upload_to='documents/',
        storage=media_storage if settings.USE_S3 else None,
        validators=[validate_document_file],
        help_text="PDF, JPG, or PNG - max 5 MB"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title

class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class HRProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hr_profile')
    company_name = models.CharField(max_length=255, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    admin_notes = models.TextField(blank=True, help_text="Notes/message for admin from HR applicant")
    # Approval workflow fields
    is_approved = models.BooleanField(default=False, help_text="HR account approved by admin")
    approval_requested_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_hr_profiles')
    approved_at = models.DateTimeField(null=True, blank=True)
    approval_token = models.CharField(max_length=100, unique=True, null=True, blank=True)
    rejection_reason = models.TextField(blank=True, help_text="Reason for rejection if applicable")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        status = "✓ Approved" if self.is_approved else "⏳ Pending"
        return f"HR Profile of {self.user.username} ({status})"
    
    def generate_approval_token(self):
        """Generate unique approval token"""
        import secrets
        self.approval_token = secrets.token_urlsafe(50)
        self.save()
        return self.approval_token


class EmailOTP(models.Model):
    """Model to store OTP for email verification during registration"""
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=255)  # Stores hashed OTP (PBKDF2-SHA256)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    failed_attempts = models.IntegerField(default=0)  # Track failed verification attempts
    last_attempt_at = models.DateTimeField(null=True, blank=True)  # Track last failed attempt time
    last_request_at = models.DateTimeField(null=True, blank=True)  # Track last OTP request time
    request_count = models.IntegerField(default=0)  # Track OTP requests in current window
    
    # Rate limiting constants
    MAX_FAILED_ATTEMPTS = 5
    MAX_ATTEMPTS_PER_HOUR = 5
    ATTEMPT_LOCKOUT_MINUTES = 30
    REQUEST_RATE_LIMIT_MINUTES = 1
    
    class Meta:
        verbose_name = "Email OTP"
        verbose_name_plural = "Email OTPs"
    
    def __str__(self):
        return f"OTP for {self.email}"
    
    def save(self, *args, **kwargs):
        """Hash OTP before saving using PBKDF2-SHA256"""
        if not self.otp.startswith('pbkdf2_sha256$'):
            # Only hash if not already hashed
            self.otp = make_password(self.otp)
        super().save(*args, **kwargs)
    
    def verify_otp(self, plain_otp):
        """Verify plain OTP against stored hash"""
        return check_password(plain_otp, self.otp)
    
    def is_expired(self):
        """Check if OTP expired (valid for 10 minutes)"""
        from django.utils import timezone
        from datetime import timedelta
        return timezone.now() - self.created_at > timedelta(minutes=10)
    
    def is_valid_attempt(self):
        """Check if user has too many failed attempts"""
        return self.failed_attempts < self.MAX_FAILED_ATTEMPTS
    
    def is_locked_out(self):
        """Check if email is locked out due to too many failed attempts"""
        from django.utils import timezone
        from datetime import timedelta
        
        if self.failed_attempts >= self.MAX_FAILED_ATTEMPTS:
            # Check if lockout period has passed
            if self.last_attempt_at:
                lockout_until = self.last_attempt_at + timedelta(minutes=self.ATTEMPT_LOCKOUT_MINUTES)
                return timezone.now() < lockout_until
            return True
        return False
    
    def can_request_otp(self):
        """Check if email can request a new OTP (rate limiting)"""
        from django.utils import timezone
        from datetime import timedelta
        
        if self.last_request_at is None:
            return True, 0
        
        time_since_last_request = timezone.now() - self.last_request_at
        wait_time = timedelta(minutes=self.REQUEST_RATE_LIMIT_MINUTES)
        
        if time_since_last_request < wait_time:
            seconds_to_wait = int((wait_time - time_since_last_request).total_seconds())
            return False, seconds_to_wait
        
        return True, 0
    
    def get_hourly_request_count(self):
        """Get number of OTP requests in the last hour"""
        from django.utils import timezone
        from datetime import timedelta
        
        one_hour_ago = timezone.now() - timedelta(hours=1)
        
        # If last request was within last hour, use request_count
        if self.last_request_at and self.last_request_at > one_hour_ago:
            return self.request_count
        
        return 0
    
    def record_failed_attempt(self):
        """Record a failed verification attempt and update lockout time"""
        from django.utils import timezone
        
        self.failed_attempts += 1
        self.last_attempt_at = timezone.now()
        self.save()
    
    def reset_failed_attempts(self):
        """Reset failed attempts after successful verification"""
        self.failed_attempts = 0
        self.last_attempt_at = None
        self.save()
    
    def record_otp_request(self):
        """Record an OTP request for rate limiting"""
        from django.utils import timezone
        from datetime import timedelta
        
        one_hour_ago = timezone.now() - timedelta(hours=1)
        
        # Reset counter if outside the hourly window
        if self.last_request_at is None or self.last_request_at < one_hour_ago:
            self.request_count = 0
        
        self.request_count += 1
        self.last_request_at = timezone.now()
        self.save()


class IPRateLimit(models.Model):
    """Model to track OTP verification attempts per IP address"""
    ip_address = models.GenericIPAddressField(unique=True)
    endpoint = models.CharField(max_length=100, default='otp_verify')  # Track by endpoint
    attempt_count = models.IntegerField(default=0)
    first_attempt_at = models.DateTimeField(auto_now_add=True)
    last_attempt_at = models.DateTimeField(auto_now=True)
    blocked_until = models.DateTimeField(null=True, blank=True)
    
    # IP Rate limiting constants
    MAX_ATTEMPTS_PER_MINUTE = 3
    BLOCK_DURATION_MINUTES = 15
    
    class Meta:
        unique_together = ('ip_address', 'endpoint')
        verbose_name = "IP Rate Limit"
        verbose_name_plural = "IP Rate Limits"
        indexes = [
            models.Index(fields=['ip_address', 'endpoint']),
        ]
    
    def __str__(self):
        return f"IP Rate Limit: {self.ip_address} ({self.endpoint})"
    
    def increment_attempt(self):
        """Increment attempt count and update timestamp"""
        from django.utils import timezone
        
        self.attempt_count += 1
        self.last_attempt_at = timezone.now()
        self.save()
    
    def is_blocked(self):
        """Check if IP is currently blocked"""
        from django.utils import timezone
        
        if self.blocked_until is None:
            return False
        
        if timezone.now() > self.blocked_until:
            # Unblock IP
            self.blocked_until = None
            self.attempt_count = 0
            self.save()
            return False
        
        return True
    
    def check_rate_limit(self):
        """
        Check if IP exceeds rate limit (3 attempts per minute)
        Returns: (is_blocked: bool, remaining_attempts: int, wait_seconds: int)
        """
        from django.utils import timezone
        from datetime import timedelta
        
        # Check if currently blocked
        if self.is_blocked():
            wait_seconds = int((self.blocked_until - timezone.now()).total_seconds())
            return True, 0, wait_seconds
        
        # Check if rate limit window has passed
        time_since_first = timezone.now() - self.first_attempt_at
        if time_since_first > timedelta(minutes=1):
            # Reset the window
            self.attempt_count = 0
            self.first_attempt_at = timezone.now()
            self.save()
            return False, self.MAX_ATTEMPTS_PER_MINUTE, 0
        
        # Check if under limit
        if self.attempt_count < self.MAX_ATTEMPTS_PER_MINUTE:
            remaining = self.MAX_ATTEMPTS_PER_MINUTE - self.attempt_count
            return False, remaining, 0
        
        # Exceeded limit - block IP
        self.blocked_until = timezone.now() + timedelta(minutes=self.BLOCK_DURATION_MINUTES)
        self.save()
        wait_seconds = self.BLOCK_DURATION_MINUTES * 60
        return True, 0, wait_seconds
    
    def reset_for_ip(self):
        """Reset rate limiting for this IP"""
        from django.utils import timezone
        
        self.attempt_count = 0
        self.blocked_until = None
        # Reset first_attempt_at to current time (don't set to None)
        self.first_attempt_at = timezone.now()
        self.save()
    
    @classmethod
    def get_or_create_for_ip(cls, ip_address, endpoint='otp_verify'):
        """Get or create IPRateLimit record for IP"""
        try:
            return cls.objects.get(ip_address=ip_address, endpoint=endpoint)
        except cls.DoesNotExist:
            return cls.objects.create(ip_address=ip_address, endpoint=endpoint)


@receiver(pre_delete, sender=User)
def delete_email_otp_on_user_delete(sender, instance, **kwargs):
    """Delete associated EmailOTP when user is deleted"""
    try:
        EmailOTP.objects.filter(email=instance.email).delete()
    except Exception as e:
        print(f"Note: Could not delete EmailOTP for {instance.email}: {str(e)}")
