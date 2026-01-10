#!/usr/bin/env python
"""
Configure S3 CORS policy for secure cross-origin uploads from your domain
This enables presigned POST uploads and file downloads via presigned URLs
"""

import os
import sys
import json
import boto3
from botocore.exceptions import ClientError

def configure_s3_cors():
    """
    Configure CORS policy on S3 bucket to allow requests from your domain
    """
    # Get credentials from environment
    aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    region = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
    
    # Get domain from environment (your production domain)
    domain = os.environ.get('DOMAIN_NAME', 'https://vakverse.com')
    
    if not all([aws_access_key, aws_secret_key, bucket_name]):
        print("❌ Error: Missing AWS credentials")
        print("   Please set: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME")
        return False
    
    print(f"🔧 Configuring S3 CORS for bucket: {bucket_name}")
    print(f"📍 Region: {region}")
    print(f"🌐 Domain: {domain}")
    
    try:
        # Create S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )
        
        # CORS configuration allowing presigned uploads/downloads from your domain
        cors_configuration = {
            'CORSRules': [
                {
                    'AllowedHeaders': ['*'],
                    'AllowedMethods': ['GET', 'PUT', 'POST', 'DELETE', 'HEAD'],
                    'AllowedOrigins': [
                        domain,
                        f"{domain.rstrip('/')}",
                        'https://vakverse.com',
                        'https://www.vakverse.com',
                    ],
                    'ExposeHeaders': ['ETag', 'x-amz-version-id'],
                    'MaxAgeSeconds': 3000
                }
            ]
        }
        
        # Apply CORS configuration
        s3_client.put_bucket_cors(
            Bucket=bucket_name,
            CORSConfiguration=cors_configuration
        )
        
        print("\n✅ S3 CORS configured successfully!")
        print("\n📋 CORS Rules Applied:")
        print(json.dumps(cors_configuration, indent=2))
        
        # Verify configuration
        print("\n🔍 Verifying CORS configuration...")
        current_cors = s3_client.get_bucket_cors(Bucket=bucket_name)
        print("✅ Verified! Current CORS configuration:")
        print(json.dumps(current_cors['CORSRules'], indent=2))
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = e.response['Error']['Message']
        
        print(f"\n❌ AWS Error ({error_code}): {error_msg}")
        
        if error_code == 'NoSuchBucket':
            print(f"   Bucket '{bucket_name}' does not exist")
        elif error_code == 'AccessDenied':
            print("   Access denied. Check your AWS credentials and permissions")
        
        return False
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False

def configure_s3_bucket_policy():
    """
    Configure bucket policy to allow presigned URL access
    This is optional but recommended for better control
    """
    aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    region = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
    
    if not all([aws_access_key, aws_secret_key, bucket_name]):
        return False
    
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )
        
        print("\n🔐 Verifying bucket public access settings...")
        
        # Check public access block settings
        try:
            public_access = s3_client.get_public_access_block(Bucket=bucket_name)
            rules = public_access['PublicAccessBlockConfiguration']
            
            print("   Current Public Access Block settings:")
            print(f"   - Block Public ACLs: {rules['BlockPublicAcls']}")
            print(f"   - Ignore Public ACLs: {rules['IgnorePublicAcls']}")
            print(f"   - Block Public Policy: {rules['BlockPublicPolicy']}")
            print(f"   - Restrict Public Buckets: {rules['RestrictPublicBuckets']}")
            
            # For presigned URLs to work, we need these settings
            if rules['BlockPublicPolicy'] or rules['RestrictPublicBuckets']:
                print("\n   ⚠️  Note: Your bucket has restrictions that may affect public access")
                print("   This is GOOD for security! Presigned URLs will still work.")
        except ClientError as e:
            if e.response['Error']['Code'] != 'NoSuchPublicAccessBlockConfiguration':
                raise
        
        return True
        
    except Exception as e:
        print(f"⚠️  Could not verify bucket policy: {str(e)}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("S3 CORS Configuration Setup")
    print("=" * 60)
    
    success = configure_s3_cors()
    configure_s3_bucket_policy()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ Setup Complete!")
        print("=" * 60)
        print("\nYour S3 bucket is now configured for:")
        print("  ✓ Presigned POST uploads")
        print("  ✓ Presigned URL downloads")
        print("  ✓ Cross-origin requests from your domain")
        print("\nYou can now:")
        print("  1. Upload files via presigned URLs")
        print("  2. Download files via presigned URLs")
        print("  3. Avoid CORS access denied errors")
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ Configuration failed")
        print("=" * 60)
        sys.exit(1)
