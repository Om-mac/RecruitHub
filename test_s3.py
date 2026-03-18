#!/usr/bin/env python
"""
Test S3 Credentials and Connection
Usage: python test_s3.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_project.settings')
sys.path.insert(0, '/Users/tapdiyaom/Desktop/recruit-hub/RecruitHub')

django.setup()

from django.conf import settings
import boto3

print("=" * 80)
print("🧪 TESTING S3 CREDENTIALS")
print("=" * 80)

# Check environment variables
print("\n1️⃣ Environment Variables:")
aws_key = os.environ.get('AWS_ACCESS_KEY_ID', '')
aws_secret = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
aws_bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME', '')
aws_region = os.environ.get('AWS_REGION', '')

print(f"   AWS_ACCESS_KEY_ID: {aws_key[:10]}...{aws_key[-5:] if len(aws_key) > 15 else ''}")
print(f"   AWS_SECRET_ACCESS_KEY: {aws_secret[:10]}...{aws_secret[-5:] if len(aws_secret) > 15 else ''}")
print(f"   AWS_STORAGE_BUCKET_NAME: {aws_bucket}")
print(f"   AWS_REGION: {aws_region}")

# Check Django settings
print("\n2️⃣ Django Settings:")
print(f"   USE_S3: {settings.USE_S3}")
if settings.USE_S3:
    print(f"   AWS_ACCESS_KEY_ID (settings): {settings.AWS_ACCESS_KEY_ID[:10]}...{settings.AWS_ACCESS_KEY_ID[-5:] if len(settings.AWS_ACCESS_KEY_ID) > 15 else ''}")
    print(f"   AWS_SECRET_ACCESS_KEY (settings): {settings.AWS_SECRET_ACCESS_KEY[:10]}...{settings.AWS_SECRET_ACCESS_KEY[-5:] if len(settings.AWS_SECRET_ACCESS_KEY) > 15 else ''}")
    print(f"   AWS_STORAGE_BUCKET_NAME (settings): {settings.AWS_STORAGE_BUCKET_NAME}")
    print(f"   AWS_S3_REGION_NAME (settings): {settings.AWS_S3_REGION_NAME}")
    print(f"   AWS_S3_CUSTOM_DOMAIN (settings): {settings.AWS_S3_CUSTOM_DOMAIN}")

# Test S3 connection
print("\n3️⃣ Testing S3 Connection with boto3:")
try:
    # Create S3 client with explicit credentials
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )
    
    # List buckets to verify credentials
    response = s3_client.list_buckets()
    print(f"   ✅ S3 Connection successful!")
    print(f"   Available buckets: {[b['Name'] for b in response.get('Buckets', [])]}")
    
    # Check if our bucket exists
    if settings.AWS_STORAGE_BUCKET_NAME in [b['Name'] for b in response.get('Buckets', [])]:
        print(f"   ✅ Bucket '{settings.AWS_STORAGE_BUCKET_NAME}' found!")
    else:
        print(f"   ⚠️  Bucket '{settings.AWS_STORAGE_BUCKET_NAME}' NOT found in account!")
        
except Exception as e:
    print(f"   ❌ S3 Connection failed: {e}")
    print(f"   Error type: {type(e).__name__}")

# Test presigned URL generation
print("\n4️⃣ Testing Presigned URL Generation:")
try:
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )
    
    # Generate presigned GET URL
    url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': 'test.jpg'},
        ExpiresIn=300
    )
    print(f"   ✅ Presigned URL generated!")
    print(f"   URL: {url[:80]}...")
    
except Exception as e:
    print(f"   ❌ Presigned URL generation failed: {e}")

print("\n" + "=" * 80)
print("✅ S3 TEST COMPLETE")
print("=" * 80)
