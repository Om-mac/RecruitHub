#!/usr/bin/env python
"""
Test Email Script for Password Reset Feature
Usage: python send_test_email.py

Environment variables needed for SMTP:
- EMAIL_HOST_USER (Gmail address)
- EMAIL_HOST_PASSWORD (Gmail app password)
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_project.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def send_test_email(recipient_email):
    """Send a test email to verify password reset functionality"""
    
    # Check if SMTP credentials are set
    email_host_user = os.environ.get('EMAIL_HOST_USER')
    email_host_password = os.environ.get('EMAIL_HOST_PASSWORD')
    
    if not email_host_user or not email_host_password:
        print("❌ ERROR: Email credentials not configured!")
        print("\nTo send a real email, set these environment variables:")
        print("  export EMAIL_HOST_USER='your-gmail@gmail.com'")
        print("  export EMAIL_HOST_PASSWORD='your-app-password'")
        print("\nThen run: python send_test_email.py")
        print("\n📖 Get Gmail App Password:")
        print("  1. Go to https://myaccount.google.com/security")
        print("  2. Enable 2-Step Verification")
        print("  3. Click 'App passwords'")
        print("  4. Select Mail → Windows Computer")
        print("  5. Copy the 16-character password")
        return False
    
    # Email content
    subject = 'Password Reset Test - RecruitHub'
    message = '''
Hello,

This is a test email from your RecruitHub password reset system.

If you received this email, the password reset functionality is working correctly!

To reset your password:
1. Visit your RecruitHub application
2. Click "Forgot Password?" on the login page
3. Enter your email address
4. Click the reset link in the email you receive
5. Set your new password

Features Tested:
✅ Email configuration working
✅ SMTP connection successful
✅ Password reset template rendering

Best regards,
RecruitHub Team

---
System Info:
Email Backend: {}
From Address: {}
Recipient: {}
    '''.format(settings.EMAIL_BACKEND, settings.DEFAULT_FROM_EMAIL, recipient_email)
    
    try:
        # Temporarily switch to SMTP backend
        original_backend = settings.EMAIL_BACKEND
        settings.EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
        
        # Send email
        result = send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            fail_silently=False,
        )
        
        # Restore original backend
        settings.EMAIL_BACKEND = original_backend
        
        if result:
            print("✅ Email sent successfully!")
            print(f"   To: {recipient_email}")
            print(f"   From: {settings.DEFAULT_FROM_EMAIL}")
            print(f"   Subject: {subject}")
            return True
        else:
            print("❌ Failed to send email")
            return False
            
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        print(f"\nTroubleshooting:")
        print(f"  - Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD")
        print(f"  - Verify Gmail 2-Step Verification is enabled")
        print(f"  - Verify you used an App Password, not regular password")
        print(f"  - Check your internet connection")
        return False

if __name__ == '__main__':
    recipient = sys.argv[1] if len(sys.argv) > 1 else 'omtapdiya75@gmail.com'
    print(f"📧 Sending test email to: {recipient}\n")
    send_test_email(recipient)
