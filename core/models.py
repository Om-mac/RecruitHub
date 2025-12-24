from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.conf import settings

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
        storage=media_storage if settings.USE_S3 else None
    )
    resume = models.FileField(
        upload_to='resumes/',
        blank=True,
        null=True,
        storage=media_storage if settings.USE_S3 else None
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
        storage=media_storage if settings.USE_S3 else None
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
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    
    def __str__(self):
        return f"OTP for {self.email}"
    
    def is_expired(self):
        """Check if OTP expired (valid for 10 minutes)"""
        from django.utils import timezone
        from datetime import timedelta
        return timezone.now() - self.created_at > timedelta(minutes=10)
    
    def is_valid_attempt(self):
        """Check if user has too many failed attempts"""
        return self.attempts < 5


@receiver(pre_delete, sender=User)
def delete_email_otp_on_user_delete(sender, instance, **kwargs):
    """Delete associated EmailOTP when user is deleted"""
    try:
        EmailOTP.objects.filter(email=instance.email).delete()
    except Exception as e:
        print(f"Note: Could not delete EmailOTP for {instance.email}: {str(e)}")
