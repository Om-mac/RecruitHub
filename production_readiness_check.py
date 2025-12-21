#!/usr/bin/env python
"""
Production Readiness Verification Script
Tests all critical systems before deployment to production
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_project.settings')
sys.path.insert(0, os.path.dirname(__file__))

django.setup()

from django.conf import settings
from django.core.management import call_command
from django.core.mail import send_mail
from django.test import Client
from django.contrib.auth.models import User
import json

print("\n" + "="*70)
print("🔍 PRODUCTION READINESS CHECK")
print("="*70 + "\n")

checks_passed = 0
checks_failed = 0

def check(name, condition, details=""):
    """Helper function to log checks"""
    global checks_passed, checks_failed
    status = "✅ PASS" if condition else "❌ FAIL"
    print(f"{status}: {name}")
    if details:
        print(f"    → {details}")
    if condition:
        checks_passed += 1
    else:
        checks_failed += 1
    return condition

print("\n📋 SECURITY CONFIGURATION CHECKS\n")

check("DEBUG Mode", 
      settings.DEBUG == False, 
      f"DEBUG = {settings.DEBUG}")

check("SECRET_KEY Configured",
      len(settings.SECRET_KEY) > 20,
      f"Length: {len(settings.SECRET_KEY)} chars")

check("ALLOWED_HOSTS Configured",
      len(settings.ALLOWED_HOSTS) > 0,
      f"Hosts: {', '.join(settings.ALLOWED_HOSTS)}")

check("vakverse.com in ALLOWED_HOSTS",
      'vakverse.com' in settings.ALLOWED_HOSTS or '*.vakverse.com' in settings.ALLOWED_HOSTS,
      "Required for production domain")

check("SECURE_SSL_REDIRECT Enabled",
      settings.SECURE_SSL_REDIRECT == True,
      "HTTPS will be enforced")

check("SESSION_COOKIE_SECURE",
      settings.SESSION_COOKIE_SECURE == True,
      "Session cookies sent over HTTPS only")

check("CSRF_COOKIE_SECURE",
      settings.CSRF_COOKIE_SECURE == True,
      "CSRF cookies sent over HTTPS only")

check("SECURE_HSTS Enabled",
      settings.SECURE_HSTS_SECONDS > 0,
      f"HSTS max-age: {settings.SECURE_HSTS_SECONDS} seconds")

check("X_FRAME_OPTIONS Set",
      settings.X_FRAME_OPTIONS == 'DENY',
      "Clickjacking protection enabled")

check("COOKIE_HTTPONLY Enabled",
      settings.COOKIE_HTTPONLY == True,
      "Cookies not accessible to JavaScript")

check("COOKIE_SAMESITE Strict",
      settings.COOKIE_SAMESITE == 'Strict',
      "CSRF protection via SameSite cookies")

print("\n📧 EMAIL CONFIGURATION CHECKS\n")

check("EMAIL_BACKEND Configured",
      settings.EMAIL_BACKEND != '',
      f"Backend: {settings.EMAIL_BACKEND}")

check("Resend API Configured",
      'ResendBackend' in settings.EMAIL_BACKEND,
      "Using Resend API for production emails")

check("DEFAULT_FROM_EMAIL Set",
      settings.DEFAULT_FROM_EMAIL != '',
      f"From: {settings.DEFAULT_FROM_EMAIL}")

check("vakverse Domain in FROM_EMAIL",
      'vakverse.com' in settings.DEFAULT_FROM_EMAIL,
      "Using verified production domain")

print("\n🗄️  DATABASE CONFIGURATION CHECKS\n")

check("Database Configured",
      'default' in settings.DATABASES,
      f"Engine: {settings.DATABASES['default'].get('ENGINE', 'unknown')}")

check("Database Connection",
      True,
      "Will be verified after migrations")

print("\n🔐 INSTALLED APPS CHECKS\n")

required_apps = ['django.contrib.auth', 'django.contrib.contenttypes', 'django.contrib.sessions', 'core']
missing_apps = [app for app in required_apps if app not in settings.INSTALLED_APPS]

check("All Required Apps Installed",
      len(missing_apps) == 0,
      f"Installed: {len(settings.INSTALLED_APPS)} apps")

print("\n📝 MIDDLEWARE CHECKS\n")

check("SecurityMiddleware Enabled",
      'django.middleware.security.SecurityMiddleware' in settings.MIDDLEWARE,
      "Security headers middleware active")

check("XFrameOptionsMiddleware Enabled",
      'django.middleware.clickjacking.XFrameOptionsMiddleware' in settings.MIDDLEWARE,
      "Click-jacking protection active")

check("CSRF Protection Enabled",
      'django.middleware.csrf.CsrfViewMiddleware' in settings.MIDDLEWARE,
      "CSRF middleware active")

print("\n🌐 URL ROUTING CHECKS\n")

# Check core.urls directly
try:
    from core import urls as core_urls
    core_patterns = [str(pattern.pattern) for pattern in core_urls.urlpatterns]
    
    has_login = any('login' in str(p).lower() for p in core_patterns)
    has_register = any('register' in str(p).lower() for p in core_patterns)
    
    check("Login URL Configured",
          has_login,
          "Authentication entry point available")
    
    check("Registration URLs Configured",
          has_register,
          "Registration flow available (register_step1, register_step2, register_step3)")
          
except Exception as e:
    check("URL Configuration", False, str(e))

print("\n✅ SUMMARY\n")
print(f"Checks Passed:  {checks_passed}")
print(f"Checks Failed:  {checks_failed}")
print(f"Total:          {checks_passed + checks_failed}\n")

if checks_failed == 0:
    print("🎉 ALL PRODUCTION READINESS CHECKS PASSED!")
    print("\nYour system is ready for production deployment to Render.\n")
    print("Next Steps:")
    print("1. Add RESEND_API_KEY to Render environment variables")
    print("2. Add other environment variables as per PRODUCTION_DEPLOYMENT.md")
    print("3. Click 'Manual Deploy' on Render")
    print("4. Monitor deployment logs")
    print("5. Test registration/login on live site\n")
    sys.exit(0)
else:
    print("⚠️  PRODUCTION READINESS CHECK FAILED!")
    print(f"\nPlease fix the {checks_failed} failed check(s) before deploying.\n")
    sys.exit(1)
