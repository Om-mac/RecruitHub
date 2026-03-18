#!/usr/bin/env python
"""
Test Resend API Configuration
Usage: python test_resend.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_project.settings')
sys.path.insert(0, '/Users/tapdiyaom/Desktop/recruit-hub/RecruitHub')

django.setup()

from django.conf import settings
from core.views import send_otp_email

print("=" * 80)
print("🧪 TESTING RESEND API CONFIGURATION")
print("=" * 80)

# Check configuration
print("\n1️⃣ Configuration Check:")
print(f"   RESEND_API_KEY exists: {'YES' if os.environ.get('RESEND_API_KEY') else 'NO'}")
print(f"   DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
print(f"   EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"   DEBUG: {settings.DEBUG}")

# Verify API key format
resend_key = os.environ.get('RESEND_API_KEY', '')
is_valid = (
    resend_key 
    and not resend_key.startswith('[')
    and 'ADD_YOUR' not in resend_key
)
print(f"   API Key Valid: {'✅ YES' if is_valid else '❌ NO'}")

if is_valid:
    print(f"   API Key (masked): {resend_key[:5]}...{resend_key[-5:]}")

# Test Resend library
print("\n2️⃣ Testing Resend Library:")
try:
    import resend
    print(f"   ✅ Resend library imported successfully")
    print(f"   Resend version: {resend.__version__ if hasattr(resend, '__version__') else 'Unknown'}")
except ImportError as e:
    print(f"   ❌ Failed to import Resend: {e}")
    sys.exit(1)

# Test API connection
if is_valid:
    print("\n3️⃣ Testing Resend API Connection:")
    try:
        resend.api_key = resend_key
        
        # Try to send a test email
        test_email = "omtapdiya75@gmail.com"  # Must use registered email for test domain
        
        response = resend.Emails.send({
            "from": settings.DEFAULT_FROM_EMAIL,
            "to": test_email,
            "subject": "🧪 RecruitHub OTP Test Email",
            "text": "This is a test email to verify Resend API is working.\n\nTest OTP: 123456",
        })
        
        print(f"   Response: {response}")
        
        if response.get('id'):
            print(f"   ✅ Test email sent successfully!")
            print(f"   Email ID: {response['id']}")
        else:
            error = response.get('message', 'Unknown error')
            print(f"   ❌ Failed to send test email: {error}")
            
    except Exception as e:
        print(f"   ❌ Exception: {type(e).__name__} - {str(e)}")

print("\n" + "=" * 80)
print("✅ TEST COMPLETE - Check your email for test message")
print("=" * 80)
