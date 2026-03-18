#!/usr/bin/env python
"""
Environment Variables Validator
Run this script to verify all required environment variables are set correctly

Usage:
    python validate_env_vars.py
"""

import os
import sys
from pathlib import Path

# Load .env file if it exists
try:
    from dotenv import load_dotenv
    env_file = Path('.env')
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    pass


class Colors:
    """Terminal color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'


def check_var(name, required=False, pattern=None):
    """Check if environment variable exists and matches pattern"""
    value = os.environ.get(name)
    
    if not value:
        if required:
            print(f"{Colors.RED}✗ CRITICAL: {name} is missing!{Colors.RESET}")
            return False
        else:
            print(f"{Colors.YELLOW}⚠ OPTIONAL: {name} is not set{Colors.RESET}")
            return True
    
    # Check pattern if provided
    if pattern:
        if pattern == 'boolean':
            if value.lower() not in ['true', 'false']:
                print(f"{Colors.RED}✗ {name} must be 'True' or 'False', got: {value}{Colors.RESET}")
                return False
        elif pattern == 'aws_key':
            if not value.startswith('AKIA') or len(value) != 20:
                print(f"{Colors.RED}✗ {name} doesn't look like valid AWS key: {value[:10]}...{Colors.RESET}")
                return False
        elif pattern == 'region':
            regions = ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-south-1']
            if value not in regions:
                print(f"{Colors.YELLOW}⚠ {name} = {value} (not in common regions){Colors.RESET}")
                return True
    
    # Show masked value for security
    if 'KEY' in name or 'PASSWORD' in name or 'SECRET' in name:
        masked = value[:5] + '*' * (len(value) - 10) + value[-5:]
        print(f"{Colors.GREEN}✓ {name} = {masked}{Colors.RESET}")
    else:
        print(f"{Colors.GREEN}✓ {name} = {value}{Colors.RESET}")
    
    return True


def main():
    """Check all required environment variables"""
    print(f"\n{Colors.BLUE}=== RecruitHub Environment Variables Validator ==={Colors.RESET}\n")
    
    # Track errors
    errors = []
    warnings = []
    
    print(f"{Colors.BLUE}CRITICAL VARIABLES (Required):{Colors.RESET}")
    print("-" * 50)
    
    critical_vars = {
        'SECRET_KEY': ('secret', 50),  # Should be 50+ chars
        'DEBUG': ('boolean', None),
        'ALLOWED_HOSTS': (None, None),
        'AWS_ACCESS_KEY_ID': ('aws_key', None),
        'AWS_SECRET_ACCESS_KEY': ('secret', None),
        'AWS_REGION': ('region', None),
        'USE_DYNAMODB': ('boolean', None),
        'USE_S3': ('boolean', None),
        'AWS_STORAGE_BUCKET_NAME': (None, None),
        'AWS_S3_REGION_NAME': ('region', None),
        'DYNAMODB_TABLE_PREFIX': (None, None),
    }
    
    for var, (type_, length) in critical_vars.items():
        value = os.environ.get(var)
        if not value:
            errors.append(var)
            print(f"{Colors.RED}✗ MISSING: {var}{Colors.RESET}")
        else:
            # Validate format
            if type_ == 'secret' and length and len(value) < length:
                warnings.append(f"{var} might be too short ({len(value)} < {length})")
            
            if 'KEY' in var or 'PASSWORD' in var or 'SECRET' in var:
                masked = value[:5] + '*' * (len(value) - 10) + value[-5:]
                print(f"{Colors.GREEN}✓ {var} = {masked}{Colors.RESET}")
            else:
                if len(value) > 50:
                    print(f"{Colors.GREEN}✓ {var} = {value[:40]}...{Colors.RESET}")
                else:
                    print(f"{Colors.GREEN}✓ {var} = {value}{Colors.RESET}")
    
    print(f"\n{Colors.BLUE}OPTIONAL VARIABLES:{Colors.RESET}")
    print("-" * 50)
    
    optional_vars = [
        'EMAIL_BACKEND',
        'RESEND_API_KEY',
        'EMAIL_HOST',
        'EMAIL_PORT',
        'EMAIL_HOST_USER',
        'EMAIL_HOST_PASSWORD',
        'CSRF_TRUSTED_ORIGINS',
        'ADMIN_URL_PATH',
        'ENABLE_RATE_LIMITING',
    ]
    
    for var in optional_vars:
        if var not in os.environ:
            print(f"{Colors.YELLOW}○ {var} not set (optional){Colors.RESET}")
        else:
            value = os.environ.get(var)
            if 'PASS' in var or 'KEY' in var:
                masked = value[:5] + '*' * (len(value) - 10) + value[-5:]
                print(f"{Colors.GREEN}✓ {var} = {masked}{Colors.RESET}")
            else:
                print(f"{Colors.GREEN}✓ {var} = {value}{Colors.RESET}")
    
    # Summary
    print(f"\n{Colors.BLUE}=== SUMMARY ==={Colors.RESET}")
    print("-" * 50)
    
    if errors:
        print(f"{Colors.RED}❌ MISSING CRITICAL VARIABLES ({len(errors)}):{Colors.RESET}")
        for var in errors:
            print(f"   - {var}")
    else:
        print(f"{Colors.GREEN}✓ All critical variables are set!{Colors.RESET}")
    
    if warnings:
        print(f"\n{Colors.YELLOW}⚠ WARNINGS ({len(warnings)}):{Colors.RESET}")
        for warning in warnings:
            print(f"   - {warning}")
    
    # Exit code
    if errors:
        print(f"\n{Colors.RED}❌ VALIDATION FAILED - Please set missing variables{Colors.RESET}\n")
        return 1
    else:
        print(f"\n{Colors.GREEN}✅ VALIDATION PASSED - Ready for deployment!{Colors.RESET}\n")
        return 0


if __name__ == '__main__':
    sys.exit(main())
